def test_login_success(client, test_user):
    resp = client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_email(client):
    resp = client.post("/api/auth/login", json={"email": "x@y.com", "password": "no"})
    assert resp.status_code == 401


def test_login_invalid_password(client, test_user):
    resp = client.post("/api/auth/login", json={"email": test_user.email, "password": "wrong"})
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


def test_register_success_as_manager(client, manager_user, auth_token):
    token = auth_token(manager_user.email, "pass")
    
    resp = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "new@x.com", "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["email"] == "new@x.com"


def test_register_success_as_admin(client, admin_user, auth_token):
    token = auth_token(admin_user.email, "pass")
    
    resp = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "new2@x.com", "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


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
