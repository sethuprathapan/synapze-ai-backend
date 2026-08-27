from datetime import UTC, datetime, timedelta

from app.models.notification import Notification
from tests.conftest import auth_headers, create_project


def task_payload(project_id: int, assignee_id: int | None = None) -> dict:
    return {
        "project_id": project_id,
        "title": "Prepare onboarding checklist",
        "description": "Create checklist for new engineering hires.",
        "status": "todo",
        "due_date": (datetime.now(UTC).replace(tzinfo=None) + timedelta(days=3)).isoformat(),
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

    assignee_notifications = client.get(
        "/api/v1/notifications",
        headers=auth_headers(client, users["assignee"].email),
    )
    assert assignee_notifications.status_code == 200
    assert assignee_notifications.json()["data"][0]["type"] == "status_changed"


def test_task_filters_reject_invalid_due_range(client, users):
    headers = auth_headers(client, users["alice"].email)

    response = client.get(
        "/api/v1/tasks?due_from=2026-09-01T00:00:00&due_to=2026-08-01T00:00:00",
        headers=headers,
    )

    assert response.status_code == 400


def test_task_rejects_missing_assignee(client, users):
    headers = auth_headers(client, users["alice"].email)
    project = create_project(client, headers)

    response = client.post(
        "/api/v1/tasks",
        json=task_payload(project["id"], assignee_id=9999),
        headers=headers,
    )

    assert response.status_code == 400


def test_put_replaces_project_and_task(client, users):
    headers = auth_headers(client, users["alice"].email)
    project = create_project(client, headers)
    task_id = client.post(
        "/api/v1/tasks",
        json=task_payload(project["id"]),
        headers=headers,
    ).json()["data"]["id"]

    replaced_project = client.put(
        f"/api/v1/projects/{project['id']}",
        json={"name": "Replacement project", "description": None},
        headers=headers,
    )
    assert replaced_project.status_code == 200
    assert replaced_project.json()["data"]["name"] == "Replacement project"

    replaced_task = client.put(
        f"/api/v1/tasks/{task_id}",
        json={
            "project_id": project["id"],
            "title": "Replacement task",
            "description": None,
            "status": "done",
            "assignee_id": None,
            "due_date": None,
        },
        headers=headers,
    )
    assert replaced_task.status_code == 200
    assert replaced_task.json()["data"]["title"] == "Replacement task"
    assert replaced_task.json()["data"]["status"] == "done"
