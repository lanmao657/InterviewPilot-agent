import asyncio

from app.services.ai_agent import AIAgent


async def _generate_questions() -> None:
    questions = await AIAgent().generate_questions("项目深挖", 3, user_id=1)
    assert len(questions) == 3
    assert questions[0]["prompt"]


def test_generate_questions_fallback() -> None:
    asyncio.run(_generate_questions())
