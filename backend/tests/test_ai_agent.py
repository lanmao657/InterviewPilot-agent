import asyncio
from unittest.mock import AsyncMock

from app.services.ai_agent import AIAgent


async def _generate_questions() -> None:
    questions = await AIAgent().generate_questions("项目深挖", 3, user_id=1)
    assert len(questions) == 3
    assert questions[0]["prompt"]


def test_generate_questions_fallback() -> None:
    asyncio.run(_generate_questions())


def test_generate_questions_unwraps_common_questions_object() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent._chat_with_rag = AsyncMock(
            return_value='{"questions":[{"category":"项目","difficulty":"hard","prompt":"讲一个项目","rubric":"按 STAR 评分"}]}'
        )

        questions = await agent.generate_questions("项目深挖", 3, user_id=1)

        assert len(questions) == 1
        assert questions[0]["category"] == "项目"
        assert questions[0]["prompt"] == "讲一个项目"
        assert questions[0]["rubric"] == {"评分标准": "按 STAR 评分"}

    asyncio.run(_run())


def test_generate_questions_falls_back_for_incomplete_json_items() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent._chat_with_rag = AsyncMock(return_value='[{"prompt":"只有题干"}]')

        questions = await agent.generate_questions("项目深挖", 2, user_id=1)

        assert len(questions) == 2
        assert all(question["category"] for question in questions)
        assert all(question["rubric"] for question in questions)

    asyncio.run(_run())


def test_generate_questions_marks_ai_fallback_when_provider_fails() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent.settings.ai_api_key = "test-key"
        agent._chat_with_rag = AsyncMock(side_effect=RuntimeError("provider down"))

        questions = await agent.generate_questions("项目深挖", 2, user_id=1)

        assert len(questions) == 2
        assert questions[0]["rubric"]["_ai_notice"] == "AI 服务暂时不可用，已使用本地示例结果。"

    asyncio.run(_run())


def test_score_answer_marks_ai_fallback_for_invalid_model_output() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent.settings.ai_api_key = "test-key"
        agent._chat_with_rag = AsyncMock(return_value='{"score": "not a number"}')

        result = await agent.score_answer("测试问题", "测试回答", user_id=1)

        assert result["score"] == 70
        assert result["_ai_notice"] == "AI 返回格式异常，已使用本地示例结果。"

    asyncio.run(_run())


def test_coach_with_context_returns_safe_message_when_provider_fails() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent.settings.ai_api_key = "test-key"
        agent._chat = AsyncMock(side_effect=RuntimeError("provider down"))

        answer = await agent.coach_with_context("我该怎么准备？", {})

        assert answer == "助手暂时无法回答，请稍后重试。"

    asyncio.run(_run())


def test_document_ai_features_mark_fallback_when_provider_fails() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent.settings.ai_api_key = "test-key"
        agent._chat_with_rag = AsyncMock(side_effect=RuntimeError("provider down"))

        analysis = await agent.analyze_resume("简历内容", user_id=1)
        jd_match = await agent.analyze_jd_match("简历内容", "JD 内容", user_id=1)
        rewrite = await agent.rewrite_resume("简历内容", "JD 内容", user_id=1)
        roadmap = await agent.build_roadmap("简历内容", "JD 内容", "工程师", user_id=1)

        assert analysis["_ai_notice"] == "AI 服务暂时不可用，已使用本地示例结果。"
        assert jd_match["_ai_notice"] == "AI 服务暂时不可用，已使用本地示例结果。"
        assert rewrite["_ai_notice"] == "AI 服务暂时不可用，已使用本地示例结果。"
        assert roadmap["_ai_notice"] == "AI 服务暂时不可用，已使用本地示例结果。"

    asyncio.run(_run())


def test_keyword_extraction_marks_local_fallback_without_ai_key() -> None:
    async def _run() -> None:
        agent = AIAgent()
        agent.settings.ai_api_key = None

        result = await agent.extract_jd_keywords("负责 Python FastAPI PostgreSQL 数据分析", user_id=1)

        assert result["_ai_notice"] == "未配置 AI 服务，当前使用本地模拟结果。"
        assert result["keywords"]

    asyncio.run(_run())
