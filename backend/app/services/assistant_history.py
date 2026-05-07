from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import AssistantConversation, AssistantMessage, User


def now_utc() -> datetime:
    return datetime.now(UTC)


def get_or_create_active_conversation(db: Session, user: User, conversation_id: int | None = None) -> AssistantConversation:
    if conversation_id is not None:
        conversation = db.scalar(
            select(AssistantConversation)
            .options(selectinload(AssistantConversation.messages))
            .where(
                AssistantConversation.id == conversation_id,
                AssistantConversation.user_id == user.id,
                AssistantConversation.archived_at.is_(None),
            )
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Assistant conversation not found")
        return conversation

    conversation = db.scalar(
        select(AssistantConversation)
        .options(selectinload(AssistantConversation.messages))
        .where(AssistantConversation.user_id == user.id, AssistantConversation.archived_at.is_(None))
        .order_by(AssistantConversation.updated_at.desc(), AssistantConversation.id.desc())
        .limit(1)
    )
    if conversation:
        return conversation

    conversation = AssistantConversation(user_id=user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_messages(
    db: Session,
    conversation: AssistantConversation,
    limit: int = 80,
    offset: int = 0,
    latest: bool = False,
) -> list[AssistantMessage]:
    query = select(AssistantMessage).where(AssistantMessage.conversation_id == conversation.id)
    if latest:
        messages = list(
            db.scalars(query.order_by(AssistantMessage.created_at.desc(), AssistantMessage.id.desc()).limit(limit)).all()
        )
        messages.reverse()
        return messages

    return list(
        db.scalars(query.order_by(AssistantMessage.created_at.asc(), AssistantMessage.id.asc()).offset(offset).limit(limit)).all()
    )


def add_message(
    db: Session,
    conversation: AssistantConversation,
    role: str,
    content: str,
    status: str = "done",
) -> AssistantMessage:
    timestamp = now_utc()
    message = AssistantMessage(
        conversation_id=conversation.id,
        role=role,
        content=content,
        status=status,
        completed_at=timestamp if status != "streaming" else None,
    )
    conversation.updated_at = timestamp
    db.add(message)
    db.add(conversation)
    db.commit()
    db.refresh(message)
    db.refresh(conversation)
    return message


def finish_message(db: Session, conversation: AssistantConversation, message: AssistantMessage, content: str, status: str) -> None:
    timestamp = now_utc()
    message.content = content
    message.status = status
    message.completed_at = timestamp
    conversation.updated_at = timestamp
    db.add(message)
    db.add(conversation)
    db.commit()


def archive_active_conversation(db: Session, user: User) -> None:
    conversation = db.scalar(
        select(AssistantConversation)
        .where(AssistantConversation.user_id == user.id, AssistantConversation.archived_at.is_(None))
        .order_by(AssistantConversation.updated_at.desc(), AssistantConversation.id.desc())
        .limit(1)
    )
    if not conversation:
        return
    timestamp = now_utc()
    conversation.archived_at = timestamp
    conversation.updated_at = timestamp
    db.add(conversation)
    db.commit()
