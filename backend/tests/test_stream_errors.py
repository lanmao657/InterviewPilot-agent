import pytest

from app.routers import streams


@pytest.mark.asyncio
async def test_assistant_stream_uses_safe_error_message(monkeypatch) -> None:
    class BrokenAgent:
        async def stream_coach_with_context(self, message: str, context: dict):
            raise RuntimeError("secret provider stack trace")
            yield ""

    monkeypatch.setattr(streams, "AIAgent", lambda: BrokenAgent())
    monkeypatch.setattr(streams, "finish_message", lambda *args, **kwargs: None)

    chunks = [
        chunk
        async for chunk in streams._sse_assistant_persisted(
            "你好",
            {},
            db=object(),
            conversation=object(),
            assistant_message=object(),
        )
    ]
    payload = "".join(chunks)

    assert "event: error" in payload
    assert "助手暂时无法回答，请稍后重试。" in payload
    assert "secret provider stack trace" not in payload
