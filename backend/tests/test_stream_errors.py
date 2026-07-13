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


@pytest.mark.asyncio
async def test_assistant_stream_preserves_multiline_markdown_before_done(monkeypatch) -> None:
    class MultilineAgent:
        async def stream_coach_with_context(self, message: str, context: dict):
            yield "第一段\n\n第二段"

    finished: dict[str, str] = {}

    def capture_finish(_db, _conversation, _message, content: str, status: str) -> None:
        finished.update(content=content, status=status)

    monkeypatch.setattr(streams, "AIAgent", lambda: MultilineAgent())
    monkeypatch.setattr(streams, "finish_message", capture_finish)

    chunks = [
        chunk
        async for chunk in streams._sse_assistant_persisted(
            "请分段回答", {}, db=object(), conversation=object(), assistant_message=object()
        )
    ]

    assert chunks == [
        "data: 第一段\ndata: \ndata: 第二段\n\n",
        "event: done\ndata: [DONE]\n\n",
    ]
    assert finished == {"content": "第一段\n\n第二段", "status": "done"}
