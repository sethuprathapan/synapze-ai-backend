from tests.conftest import auth_headers


def test_health_and_metrics(client):
    health = client.get("/health")
    metrics = client.get("/metrics")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert metrics.status_code == 200
    assert "requests_total" in metrics.json()
    assert "errors_total" in metrics.json()


def test_contact_create_and_admin_list(client, users):
    created = client.post(
        "/api/v1/contacts",
        json={"name": "Buyer", "email": "buyer@example.com", "message": "Tell me more."},
    )
    assert created.status_code == 201

    blocked = client.get(
        "/api/v1/contacts",
        headers=auth_headers(client, users["alice"].email),
    )
    assert blocked.status_code == 403

    listed = client.get(
        "/api/v1/contacts?email=buyer@example.com",
        headers=auth_headers(client, users["admin"].email),
    )
    assert listed.status_code == 200
    assert listed.json()["data"][0]["email"] == "buyer@example.com"
