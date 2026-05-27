def test_guest_login_creates_anonymous_user(client):
    """测试游客登录创建匿名用户"""
    response = client.post("/api/auth/guest")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["is_anonymous"] is True
    assert data["user"]["username"].startswith("guest_")


def test_guest_login_returns_valid_token(client):
    """测试游客登录返回有效 token"""
    response = client.post("/api/auth/guest")
    token = response.json()["access_token"]
    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["is_anonymous"] is True


def test_guest_login_multiple_times_creates_different_users(client):
    """测试多次游客登录创建不同用户"""
    resp1 = client.post("/api/auth/guest")
    resp2 = client.post("/api/auth/guest")
    assert resp1.json()["user"]["id"] != resp2.json()["user"]["id"]
