import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models import Document, DocumentKind


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


client = TestClient(app)


def _register(username: str) -> tuple[int, str]:
    response = client.post("/api/auth/register", json={"username": username, "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    return data["user"]["id"], data["access_token"]


def _add_document(user_id: int, status: str, error: str | None = None) -> int:
    with SessionLocal() as db:
        doc = Document(
            user_id=user_id,
            kind=DocumentKind.resume,
            filename=f"{status}.txt",
            content="测试简历内容",
            summary={"preview": "测试简历内容"},
            embedding_status=status,
            embedding_error=error,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc.id


def test_create_plan_rejects_processing_document() -> None:
    user_id, token = _register("plan-processing")
    doc_id = _add_document(user_id, "processing")

    response = client.post(
        "/api/prep-plans",
        json={"resume_id": doc_id, "title": "计划", "target_role": "工程师"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "文档语义索引仍在建立中，请稍后再试"


def test_create_plan_rejects_failed_document_with_saved_error() -> None:
    user_id, token = _register("plan-failed")
    doc_id = _add_document(user_id, "failed", "未解析到可用于索引的文本，请检查文件内容。")

    response = client.post(
        "/api/prep-plans",
        json={"resume_id": doc_id, "title": "计划", "target_role": "工程师"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "未解析到可用于索引的文本，请检查文件内容。"
