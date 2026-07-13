import os
from datetime import datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AI_API_KEY"] = ""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models import User


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


client = TestClient(app)


def test_guest_login_creates_anonymous_user():
    """测试游客登录创建匿名用户"""
    response = client.post("/api/auth/guest")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["is_anonymous"] is True
    assert data["user"]["username"].startswith("guest_")


def test_guest_login_returns_valid_token():
    """测试游客登录返回有效 token"""
    response = client.post("/api/auth/guest")
    token = response.json()["access_token"]
    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["is_anonymous"] is True


def test_guest_login_multiple_times_creates_different_users():
    """测试多次游客登录创建不同用户"""
    resp1 = client.post("/api/auth/guest")
    resp2 = client.post("/api/auth/guest")
    assert resp1.json()["user"]["id"] != resp2.json()["user"]["id"]


def test_expired_guest_token_is_rejected_and_cleaned_up():
    guest = client.post("/api/auth/guest")
    assert guest.status_code == 200
    token = guest.json()["access_token"]
    user_id = guest.json()["user"]["id"]

    with SessionLocal() as db:
        user = db.get(User, user_id)
        assert user is not None
        user.created_at = datetime.utcnow() - timedelta(hours=25)
        db.commit()

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "游客会话已过期，请重新登录"

    with SessionLocal() as db:
        assert db.scalar(select(User).where(User.id == user_id)) is None


def test_active_guest_token_still_works():
    guest = client.post("/api/auth/guest")
    assert guest.status_code == 200
    token = guest.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["is_anonymous"] is True


def test_expired_guest_refresh_token_is_rejected_and_cleaned_up():
    guest = client.post("/api/auth/guest")
    assert guest.status_code == 200
    refresh_token = guest.json()["refresh_token"]
    user_id = guest.json()["user"]["id"]

    with SessionLocal() as db:
        user = db.get(User, user_id)
        assert user is not None
        user.created_at = datetime.utcnow() - timedelta(hours=25)
        db.commit()

    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 401
    assert response.json()["detail"] == "游客会话已过期，请重新登录"

    with SessionLocal() as db:
        assert db.scalar(select(User).where(User.id == user_id)) is None
