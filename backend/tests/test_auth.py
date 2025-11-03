import pytest


def test_login_success(client, test_user):
    resp = client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.parametrize("email,password", [
    ("x@y.com", "no"),
    ("test@example.com", "wrong"),
])
def test_login_invalid_credentials(client, test_user, email, password):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 401


def test_login_missing_data(client):
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 401


def test_refresh_token_success(client, test_user):
    login_resp = client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    refresh_token = login_resp.get_json()["refresh_token"]
    
    resp = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data


def test_refresh_token_invalid(client):
    resp = client.post("/api/auth/refresh", headers={"Authorization": "Bearer invalid_token"})
    assert resp.status_code == 422


@pytest.mark.parametrize("user_fixture,email", [
    ("manager_user", "new@x.com"),
    ("admin_user", "new2@x.com"),
])
def test_register_success(client, request, auth_token, user_fixture, email):
    user = request.getfixturevalue(user_fixture)
    token = auth_token(user.email, "pass")
    
    resp = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": email, "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["email"] == email


def test_register_forbidden_as_member(client, member_user, auth_token):
    token = auth_token(member_user.email, "pass")
    
    resp = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "new3@x.com", "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_register_unauthorized(client):
    resp = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "new@x.com", "password": "pass123"},
    )
    assert resp.status_code == 401
