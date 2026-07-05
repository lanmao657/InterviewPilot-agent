import os
from datetime import datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

from sqlalchemy import func, select
import pytest

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    AssistantConversation,
    AssistantMessage,
    Document,
    DocumentChunk,
    DocumentKind,
    InterviewSession,
    InterviewTurn,
    PrepPlan,
    Question,
    Report,
    User,
)


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _count(db, model) -> int:
    return db.scalar(select(func.count()).select_from(model))


def test_cleanup_expired_guests_deletes_owned_data_and_keeps_others() -> None:
    try:
        from app.services.guest_cleanup import cleanup_expired_guests
    except ModuleNotFoundError:
        pytest.fail("cleanup_expired_guests 服务尚未实现")

    with SessionLocal() as db:
        expired = User(
            username="guest_expired",
            name="游客 expired",
            hashed_password=hash_password("password123"),
            is_anonymous=True,
            created_at=datetime.utcnow() - timedelta(hours=25),
        )
        active = User(
            username="guest_active",
            name="游客 active",
            hashed_password=hash_password("password123"),
            is_anonymous=True,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        registered = User(
            username="registered",
            name="registered",
            hashed_password=hash_password("password123"),
            is_anonymous=False,
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db.add_all([expired, active, registered])
        db.commit()
        db.refresh(expired)
        db.refresh(active)
        db.refresh(registered)
        expired_id = expired.id
        active_id = active.id
        registered_id = registered.id

        doc = Document(
            user_id=expired_id,
            kind=DocumentKind.resume,
            filename="resume.txt",
            content="expired resume",
            summary={"preview": "expired resume"},
        )
        kept_doc = Document(
            user_id=active_id,
            kind=DocumentKind.resume,
            filename="active.txt",
            content="active resume",
            summary={"preview": "active resume"},
        )
        db.add_all([doc, kept_doc])
        db.commit()
        db.refresh(doc)

        chunk = DocumentChunk(
            document_id=doc.id,
            user_id=expired_id,
            chunk_index=0,
            content="expired chunk",
            embedding=[0.1] * 1024,
        )
        plan = PrepPlan(user_id=expired_id, title="plan", target_role="role", fit_score=70, roadmap={})
        question = Question(user_id=expired_id, category="tech", prompt="q", rubric={})
        interview = InterviewSession(user_id=expired_id, title="interview")
        conversation = AssistantConversation(user_id=expired_id)
        db.add_all([chunk, plan, question, interview, conversation])
        db.commit()
        db.refresh(interview)
        db.refresh(conversation)

        turn = InterviewTurn(interview_id=interview.id, question="q", answer="a", feedback={}, score=70)
        report = Report(user_id=expired_id, interview_id=interview.id, title="report", content="ok", metrics={})
        message = AssistantMessage(conversation_id=conversation.id, role="user", content="hi")
        db.add_all([turn, report, message])
        db.commit()

        deleted = cleanup_expired_guests(db, retention_hours=24)

        assert deleted == 1
        assert db.get(User, expired_id) is None
        assert db.get(User, active_id) is not None
        assert db.get(User, registered_id) is not None
        assert _count(db, DocumentChunk) == 0
        assert _count(db, Document) == 1
        assert _count(db, PrepPlan) == 0
        assert _count(db, Question) == 0
        assert _count(db, InterviewTurn) == 0
        assert _count(db, InterviewSession) == 0
        assert _count(db, Report) == 0
        assert _count(db, AssistantMessage) == 0
        assert _count(db, AssistantConversation) == 0
