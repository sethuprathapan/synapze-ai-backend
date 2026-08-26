from datetime import datetime, timedelta

from app.models.notification import Notification
from tests.conftest import auth_headers, create_project


def task_payload(project_id: int, assignee_id: int | None = None) -> dict:
    return {
        "project_id": project_id,
        "title": "Prepare onboarding checklist",
        "description": "Create checklist for new engineering hires.",
        "status": "todo",
        "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        "assignee_id": assignee_id,
    }


def test_project_crud_is_scoped_to_owner(client, users):
    alice_headers = auth_headers(client, users["alice"].email)
    bob_headers = auth_headers(client, users["bob"].email)
    project = create_project(client, alice_headers)

    blocked = client.get(f"/api/v1/projects/{project['id']}", headers=bob_headers)
    assert blocked.status_code == 404

    updated = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "Updated launch"},
        headers=alice_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Updated launch"


def test_task_crud_filtering_and_cache_invalidation(client, users):
    headers = auth_headers(client, users["alice"].email)
    project = create_project(client, headers)
    task = client.post(
        "/api/v1/tasks",
        json=task_payload(project["id"], users["assignee"].id),
        headers=headers,
    )

    assert task.status_code == 201
    task_id = task.json()["data"]["id"]

    first_list = client.get("/api/v1/tasks?status=todo", headers=headers)
    assert first_list.status_code == 200
    assert first_list.json()["data"]["total"] == 1

    update = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "done"},
        headers=headers,
    )
    assert update.status_code == 200

    stale_check = client.get("/api/v1/tasks?status=todo", headers=headers)
    assert stale_check.status_code == 200
    assert stale_check.json()["data"]["total"] == 0

    done_tasks = client.get("/api/v1/tasks?status=done", headers=headers)
    assert done_tasks.json()["data"]["items"][0]["id"] == task_id


def test_user_cannot_access_task_in_another_users_project(client, users):
    alice_headers = auth_headers(client, users["alice"].email)
    bob_headers = auth_headers(client, users["bob"].email)
    project = create_project(client, alice_headers)
    task_id = client.post(
        "/api/v1/tasks",
        json=task_payload(project["id"]),
        headers=alice_headers,
    ).json()["data"]["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in_progress"},
        headers=bob_headers,
    )

    assert response.status_code == 404


def test_task_update_creates_background_notifications(client, db_session, users):
    headers = auth_headers(client, users["alice"].email)
    project = create_project(client, headers)
    task_id = client.post(
        "/api/v1/tasks",
        json=task_payload(project["id"]),
        headers=headers,
    ).json()["data"]["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"assignee_id": users["assignee"].id, "status": "in_progress"},
        headers=headers,
    )

    assert response.status_code == 200
    notifications = db_session.query(Notification).order_by(Notification.type.asc()).all()
    assert [notification.type for notification in notifications] == [
        "status_changed",
        "task_reassigned",
    ]
