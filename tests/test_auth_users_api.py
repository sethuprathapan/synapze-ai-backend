from tests.conftest import auth_headers


def test_signup_and_login(client):
    signup = client.post(
        "/api/v1/signup",
        json={
            "name": "New User",
            "email": "new.user@example.com",
            "password": "password123",
        },
    )

    assert signup.status_code == 201
    body = signup.json()
    assert body["data"]["email"] == "new.user@example.com"
    assert "password_hash" not in body["data"]

    login = client.post(
        "/api/v1/login",
        data={"username": "new.user@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


def test_duplicate_signup_is_rejected(client, users):
    response = client.post(
        "/api/v1/signup",
        json={
            "name": "Alice Again",
            "email": users["alice"].email,
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_admin_can_create_user(client, users):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "New Employee",
            "email": "employee@example.com",
            "password": "password123",
            "role": "user",
        },
        headers=auth_headers(client, users["admin"].email),
    )

    assert response.status_code == 201
    assert response.json()["data"]["email"] == "employee@example.com"


def test_non_admin_cannot_create_user(client, users):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Blocked User",
            "email": "blocked@example.com",
            "password": "password123",
            "role": "user",
        },
        headers=auth_headers(client, users["alice"].email),
    )

    assert response.status_code == 403
