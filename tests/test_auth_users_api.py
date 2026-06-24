from tests.conftest import auth_headers


def test_login_returns_consistent_token_response(client, users):
    response = client.post(
        "/api/v1/login",
        json={"email": users["admin"].email, "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Login successful"
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["access_token"]


def test_admin_can_create_user(client, users):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "New Employee",
            "email": "new.employee@example.com",
            "password": "password123",
            "role": "employee",
        },
        headers=auth_headers(client, users["admin"].email),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "new.employee@example.com"
    assert "password_hash" not in body["data"]


def test_manager_cannot_create_user(client, users):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Blocked User",
            "email": "blocked@example.com",
            "password": "password123",
            "role": "employee",
        },
        headers=auth_headers(client, users["manager"].email),
    )

    assert response.status_code == 403
