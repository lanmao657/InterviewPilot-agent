from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    AssistantConversation,
    AssistantMessage,
    Document,
    DocumentChunk,
    InterviewSession,
    InterviewTurn,
    PrepPlan,
    Question,
    Report,
    User,
)


def _utc_now_like(value: datetime | None) -> datetime:
    if value and value.tzinfo is not None:
        return datetime.now(timezone.utc)
    return datetime.utcnow()


def is_guest_expired(user: User, retention_hours: int) -> bool:
    if not user.is_anonymous or not user.created_at:
        return False
    cutoff = _utc_now_like(user.created_at) - timedelta(hours=retention_hours)
    return user.created_at < cutoff


def delete_guest_user_data(db: Session, user_ids: list[int]) -> int:
    if not user_ids:
        return 0

    interview_ids = select(InterviewSession.id).where(InterviewSession.user_id.in_(user_ids))
    conversation_ids = select(AssistantConversation.id).where(AssistantConversation.user_id.in_(user_ids))

    statements = [
        delete(AssistantMessage).where(AssistantMessage.conversation_id.in_(conversation_ids)),
        delete(AssistantConversation).where(AssistantConversation.user_id.in_(user_ids)),
        delete(Report).where(Report.user_id.in_(user_ids)),
        delete(InterviewTurn).where(InterviewTurn.interview_id.in_(interview_ids)),
        delete(InterviewSession).where(InterviewSession.user_id.in_(user_ids)),
        delete(Question).where(Question.user_id.in_(user_ids)),
        delete(PrepPlan).where(PrepPlan.user_id.in_(user_ids)),
        delete(DocumentChunk).where(DocumentChunk.user_id.in_(user_ids)),
        delete(Document).where(Document.user_id.in_(user_ids)),
        delete(User).where(User.id.in_(user_ids), User.is_anonymous.is_(True)),
    ]
    for statement in statements:
        db.execute(statement.execution_options(synchronize_session=False))
    return len(user_ids)


def cleanup_expired_guests(db: Session, retention_hours: int) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=retention_hours)
    user_ids = list(
        db.scalars(
            select(User.id).where(
                User.is_anonymous.is_(True),
                User.created_at < cutoff,
            )
        ).all()
    )
    deleted = delete_guest_user_data(db, user_ids)
    db.commit()
    return deleted
