import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models import AssistantConversation, AssistantMessage, User


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


client = TestClient(app)


def test_register_and_me() -> None:
    response = client.post(
        "/api/auth/register",
        json={"username": "tester", "password": "password123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "tester"
    assert me.json()["email"] is None


def test_login_with_username_and_password() -> None:
    register = client.post(
        "/api/auth/register",
        json={"username": "login-user", "password": "password123"},
    )
    assert register.status_code == 200

    response = client.post(
        "/api/auth/login",
        json={"username": " Login-User ", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["username"] == "login-user"


def test_login_allows_legacy_email_identifier() -> None:
    register = client.post(
        "/api/auth/register",
        json={"username": "legacy-user", "email": "legacy@example.com", "password": "password123"},
    )
    assert register.status_code == 200

    response = client.post(
        "/api/auth/login",
        json={"username": " LEGACY@example.com ", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["username"] == "legacy-user"


def test_login_rejects_email_payload() -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "tester@example.com", "password": "password123"},
    )

    assert response.status_code == 422


def test_register_rejects_duplicate_username() -> None:
    first = client.post(
        "/api/auth/register",
        json={"username": "duplicate", "password": "password123"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/auth/register",
        json={"username": " DUPLICATE ", "password": "password123"},
    )

    assert second.status_code == 409


def test_register_reports_invalid_username_or_password() -> None:
    invalid_username = client.post(
        "/api/auth/register",
        json={"username": "ab@example.com", "password": "password123"},
    )
    assert invalid_username.status_code == 422
    assert "用户名不能使用邮箱格式" in invalid_username.json()["detail"][0]["msg"]

    invalid_password = client.post(
        "/api/auth/register",
        json={"username": "valid-user", "password": "short"},
    )
    assert invalid_password.status_code == 422
    assert "密码至少需要 8 个字符" in invalid_password.json()["detail"][0]["msg"]


def test_cors_allows_vite_fallback_port() -> None:
    response = client.options(
        "/api/auth/register",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5174"


def test_assistant_context_empty_state() -> None:
    auth = client.post(
        "/api/auth/register",
        json={"username": "assistant", "password": "password123"},
    )
    assert auth.status_code == 200
    token = auth.json()["access_token"]

    response = client.post("/api/assistant/context", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["documents"] == []
    assert data["questionCount"] == 0


def test_assistant_stream_fallback() -> None:
    auth = client.post(
        "/api/auth/register",
        json={"username": "assistant-stream", "password": "password123"},
    )
    assert auth.status_code == 200
    token = auth.json()["access_token"]

    with client.stream(
        "GET",
        "/api/stream/assistant/chat?message=%E6%88%91%E4%B8%8B%E4%B8%80%E6%AD%A5%E8%AF%A5%E6%80%8E%E4%B9%88%E5%87%86%E5%A4%87",
        headers={"Authorization": f"Bearer {token}", "Origin": "http://localhost:5174"},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert "data:" in body
    assert "[DONE]" in body


def test_assistant_chat_persists_and_isolates_users() -> None:
    auth_a = client.post(
        "/api/auth/register",
        json={"username": "history-a", "password": "password123"},
    )
    assert auth_a.status_code == 200
    token_a = auth_a.json()["access_token"]

    chat = client.post(
        "/api/assistant/chat",
        json={"message": "请记住这段对话"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert chat.status_code == 200
    assert chat.json()["messages"][0]["role"] == "user"
    assert chat.json()["messages"][1]["role"] == "assistant"

    restored = client.get("/api/assistant/conversation", headers={"Authorization": f"Bearer {token_a}"})
    assert restored.status_code == 200
    messages = restored.json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[0]["content"] == "请记住这段对话"

    auth_b = client.post(
        "/api/auth/register",
        json={"username": "history-b", "password": "password123"},
    )
    assert auth_b.status_code == 200
    token_b = auth_b.json()["access_token"]

    isolated = client.get("/api/assistant/conversation", headers={"Authorization": f"Bearer {token_b}"})
    assert isolated.status_code == 200
    assert isolated.json()["messages"] == []


def test_clear_assistant_conversation_archives_current_thread() -> None:
    auth = client.post(
        "/api/auth/register",
        json={"username": "history-clear", "password": "password123"},
    )
    assert auth.status_code == 200
    token = auth.json()["access_token"]

    first = client.get("/api/assistant/conversation", headers={"Authorization": f"Bearer {token}"})
    assert first.status_code == 200
    first_id = first.json()["id"]

    response = client.delete("/api/assistant/conversation", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    second = client.get("/api/assistant/conversation", headers={"Authorization": f"Bearer {token}"})
    assert second.status_code == 200
    assert second.json()["id"] != first_id
    assert second.json()["messages"] == []


def test_assistant_stream_persists_done_messages() -> None:
    auth = client.post(
        "/api/auth/register",
        json={"username": "history-stream", "password": "password123"},
    )
    assert auth.status_code == 200
    token = auth.json()["access_token"]

    with client.stream(
        "GET",
        "/api/stream/assistant/chat?message=%E4%BF%9D%E5%AD%98%E6%B5%81%E5%BC%8F%E5%AF%B9%E8%AF%9D",
        headers={"Authorization": f"Bearer {token}", "Origin": "http://localhost:5174"},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert "[DONE]" in body

    restored = client.get("/api/assistant/conversation", headers={"Authorization": f"Bearer {token}"})
    assert restored.status_code == 200
    messages = restored.json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[1]["status"] == "done"
    assert messages[1]["content"]


def test_assistant_conversation_restores_latest_message_window() -> None:
    auth = client.post(
        "/api/auth/register",
        json={"username": "history-latest", "password": "password123"},
    )
    assert auth.status_code == 200
    token = auth.json()["access_token"]

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == "history-latest"))
        assert user is not None
        conversation = AssistantConversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        for index in range(85):
            db.add(
                AssistantMessage(
                    conversation_id=conversation.id,
                    role="user",
                    content=f"message-{index}",
                    status="done",
                )
            )
        db.commit()

    restored = client.get("/api/assistant/conversation", headers={"Authorization": f"Bearer {token}"})
    assert restored.status_code == 200
    messages = restored.json()["messages"]
    assert len(messages) == 80
    assert messages[0]["content"] == "message-5"
    assert messages[-1]["content"] == "message-84"
