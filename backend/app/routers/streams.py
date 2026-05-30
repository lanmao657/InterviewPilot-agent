import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.deps import get_current_user
from app.models import AssistantConversation, AssistantMessage, InterviewSession, User
from app.services.ai_agent import AIAgent
from app.services.assistant_context import build_assistant_context
from app.services.assistant_history import add_message, finish_message, get_or_create_active_conversation

router = APIRouter(prefix="/stream", tags=["stream"])

_SENTINEL = object()
_HEARTBEAT_INTERVAL = 15  # 心跳间隔（秒）


async def _heartbeat_producer(queue: asyncio.Queue, interval: int = _HEARTBEAT_INTERVAL):
    """定时发送 SSE 心跳，防止连接被中间代理断开"""
    try:
        while True:
            await asyncio.sleep(interval)
            await queue.put(_SENTINEL)
    except asyncio.CancelledError:
        pass


async def _stream_with_heartbeat(content_generator):
    """包装内容生成器，合并心跳信号"""
    queue: asyncio.Queue = asyncio.Queue()
    heartbeat_task = asyncio.create_task(_heartbeat_producer(queue))

    async def feed_content():
        async for chunk in content_generator:
            await queue.put(chunk)
        await queue.put(None)  # 结束信号

    content_task = asyncio.create_task(feed_content())

    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            if item is _SENTINEL:
                yield ":keepalive\n\n"
            else:
                yield item
    finally:
        heartbeat_task.cancel()
        content_task.cancel()


async def _sse_text(system: str, prompt: str):
    async for chunk in AIAgent().stream_chat(system, prompt):
        yield f"data: {chunk}\n\n"
    yield "event: done\ndata: [DONE]\n\n"


async def _sse_assistant_persisted(
    message: str,
    context: dict,
    db: Session,
    conversation: AssistantConversation,
    assistant_message: AssistantMessage,
):
    content = ""
    try:
        async for chunk in AIAgent().stream_coach_with_context(message, context):
            content += chunk
            yield f"data: {chunk}\n\n"
        finish_message(db, conversation, assistant_message, content, "done")
        yield "event: done\ndata: [DONE]\n\n"
    except asyncio.CancelledError:
        status = "done" if content else "error"
        finish_message(db, conversation, assistant_message, content or "助手回复已中断。", status)
        raise
    except Exception as exc:
        fallback = "助手暂时无法回答，请稍后重试。"
        content = content or fallback
        finish_message(db, conversation, assistant_message, content, "error")
        yield f"event: error\ndata: {str(exc)}\n\n"
        yield "event: done\ndata: [DONE]\n\n"


@router.get("/assistant/chat")
async def stream_assistant_chat(
    message: str = Query(min_length=1, max_length=4000),
    conversation_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    conversation = get_or_create_active_conversation(db, user, conversation_id)
    add_message(db, conversation, "user", message)
    assistant_message = add_message(db, conversation, "assistant", "", status="streaming")
    context = build_assistant_context(db, user)
    return StreamingResponse(
        _stream_with_heartbeat(_sse_assistant_persisted(message, context, db, conversation, assistant_message)),
        media_type="text/event-stream",
    )


@router.get("/interviews/{interview_id}/follow-up")
async def stream_follow_up(interview_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StreamingResponse:
    interview = db.scalar(
        select(InterviewSession)
        .options(selectinload(InterviewSession.turns))
        .where(InterviewSession.id == interview_id, InterviewSession.user_id == user.id)
    )
    if not interview:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    latest = interview.turns[-1] if interview.turns else None
    prompt = "请给出下一道中文追问题。"
    if latest:
        prompt = f"上一题：{latest.question}\n候选人回答：{latest.answer}\n请给出一个有针对性的追问。"
    return StreamingResponse(
        _stream_with_heartbeat(_sse_text("你是严格但友善的中文面试官。", prompt)),
        media_type="text/event-stream",
    )


@router.get("/reports/{interview_id}")
async def stream_report(interview_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StreamingResponse:
    interview = db.scalar(
        select(InterviewSession)
        .options(selectinload(InterviewSession.turns))
        .where(InterviewSession.id == interview_id, InterviewSession.user_id == user.id)
    )
    if not interview:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    turns = "\n".join(f"Q:{turn.question}\nA:{turn.answer}" for turn in interview.turns)
    return StreamingResponse(
        _stream_with_heartbeat(_sse_text("你是中文面试复盘教练。", f"请生成 STAR Feedback 报告：\n{turns}")),
        media_type="text/event-stream",
    )
