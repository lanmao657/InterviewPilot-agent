import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models import Document, DocumentKind
from app.routers import prep_plans
from app.services.ai_agent import AI_UNAVAILABLE_NOTICE


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


client = TestClient(app)


def _register(username: str) -> tuple[int, str]:
    response = client.post("/api/auth/register", json={"username": username, "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    return data["user"]["id"], data["access_token"]


def _add_document(user_id: int, kind: DocumentKind) -> int:
    with SessionLocal() as db:
        doc = Document(
            user_id=user_id,
            kind=kind,
            filename=f"{kind.value}.txt",
            content="候选人材料内容",
            summary={"preview": "候选人材料内容"},
            embedding_status="ready",
            chunk_count=1,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc.id


def test_stream_plan_emits_notice_when_ai_subtasks_fallback(monkeypatch) -> None:
    class NoticeAgent:
        async def build_roadmap(self, resume_text: str, jd_text: str, target_role: str, user_id: int) -> dict:
            return {
                "_ai_notice": AI_UNAVAILABLE_NOTICE,
                "summary": "AI 分析暂时不可用，已使用本地示例结果。",
                "milestones": ["岗位匹配分析"],
                "focusAreas": ["项目深挖"],
                "strengths": [],
                "gaps": [],
            }

        async def extract_jd_keywords(self, jd_text: str, user_id: int) -> dict:
            return {"_ai_notice": AI_UNAVAILABLE_NOTICE, "keywords": []}

    class NoticeMatchingService:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def compute_fit_score(self, resume_id: int, jd_id: int, user_id: int) -> dict:
            return {"score": 68, "_ai_notice": AI_UNAVAILABLE_NOTICE}

    user_id, token = _register("stream-notice")
    resume_id = _add_document(user_id, DocumentKind.resume)
    jd_id = _add_document(user_id, DocumentKind.job_description)
    monkeypatch.setattr(prep_plans, "AIAgent", lambda retrieval: NoticeAgent())
    monkeypatch.setattr(prep_plans, "MatchingService", NoticeMatchingService)

    response = client.post(
        "/api/prep-plans/stream",
        json={
            "resume_id": resume_id,
            "job_description_id": jd_id,
            "title": "计划",
            "target_role": "工程师",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.text
    assert "event: notice" in body
    assert AI_UNAVAILABLE_NOTICE in body
