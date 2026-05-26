from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantContextRead,
    AssistantConversationRead,
    AssistantMessageRead,
)
from app.services.ai_agent import AIAgent
from app.services.assistant_context import build_assistant_context
from app.services.assistant_history import (
    add_message,
    archive_active_conversation,
    get_or_create_active_conversation,
    list_messages,
)

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/context", response_model=AssistantContextRead)
def assistant_context(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return build_assistant_context(db, user)


@router.get("/conversation", response_model=AssistantConversationRead)
def assistant_conversation(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssistantConversationRead:
    conversation = get_or_create_active_conversation(db, user)
    messages = list_messages(db, conversation, latest=True)
    result = AssistantConversationRead.model_validate(conversation)
    result.messages = [AssistantMessageRead.model_validate(message) for message in messages]
    return result


@router.get("/messages", response_model=list[AssistantMessageRead])
def assistant_messages(
    conversation_id: int | None = None,
    limit: int = Query(default=80, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list:
    conversation = get_or_create_active_conversation(db, user, conversation_id)
    return list_messages(db, conversation, limit=limit, offset=offset)


@router.post("/chat", response_model=AssistantChatResponse)
async def assistant_chat(
    payload: AssistantChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssistantChatResponse:
    conversation = get_or_create_active_conversation(db, user, payload.conversation_id)
    add_message(db, conversation, "user", payload.message)
    context = build_assistant_context(db, user)
    answer = await AIAgent().coach_with_context(payload.message, context)
    add_message(db, conversation, "assistant", answer)
    messages = list_messages(db, conversation, latest=True)
    conversation_read = AssistantConversationRead.model_validate(conversation)
    conversation_read.messages = [AssistantMessageRead.model_validate(message) for message in messages]
    return AssistantChatResponse(answer=answer, context=context, conversation=conversation_read, messages=conversation_read.messages)


@router.delete("/conversation", status_code=204)
def clear_assistant_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    archive_active_conversation(db, user)
