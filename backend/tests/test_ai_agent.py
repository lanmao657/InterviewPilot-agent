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
