from datetime import datetime, timedelta

from app.models.task_history import TaskHistory
from tests.conftest import auth_headers


def task_payload(employee_id: int) -> dict:
    return {
        "title": "Prepare onboarding checklist",
        "description": "Create checklist for new engineering hires.",
        "priority": "high",
        "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        "assigned_to_id": employee_id,
    }


def test_manager_can_create_task(client, db_session, users):
    response = client.post(
        "/api/v1/tasks",
        json=task_payload(users["employee"].id),
        headers=auth_headers(client, users["manager"].email),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Prepare onboarding checklist"
    assert body["data"]["status"] == "pending"
    assert body["data"]["assigned_by_id"] == users["manager"].id

    history = db_session.query(TaskHistory).one()
    assert history.old_status == "created"
    assert history.new_status == "pending"
    assert history.changed_by == users["manager"].id


def test_employee_cannot_create_task(client, users):
    response = client.post(
        "/api/v1/tasks",
        json=task_payload(users["employee"].id),
        headers=auth_headers(client, users["employee"].email),
    )

    assert response.status_code == 403


def test_employee_can_only_view_assigned_tasks(client, users):
    manager_headers = auth_headers(client, users["manager"].email)
    first = client.post(
        "/api/v1/tasks",
        json=task_payload(users["employee"].id),
        headers=manager_headers,
    ).json()["data"]
    client.post(
        "/api/v1/tasks",
        json=task_payload(users["other_employee"].id),
        headers=manager_headers,
    )

    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers(client, users["employee"].email),
    )

    assert response.status_code == 200
    task_ids = [task["id"] for task in response.json()["data"]]
    assert task_ids == [first["id"]]


def test_status_update_creates_audit_history(client, db_session, users):
    manager_headers = auth_headers(client, users["manager"].email)
    task_id = client.post(
        "/api/v1/tasks",
        json=task_payload(users["employee"].id),
        headers=manager_headers,
    ).json()["data"]["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in-progress"},
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "in-progress"

    history = (
        db_session.query(TaskHistory)
        .filter(TaskHistory.task_id == task_id)
        .order_by(TaskHistory.id.asc())
        .all()
    )
    assert [(row.old_status, row.new_status) for row in history] == [
        ("created", "pending"),
        ("pending", "in-progress"),
    ]


def test_assigned_employee_can_comment_on_task(client, users):
    manager_headers = auth_headers(client, users["manager"].email)
    task_id = client.post(
        "/api/v1/tasks",
        json=task_payload(users["employee"].id),
        headers=manager_headers,
    ).json()["data"]["id"]

    response = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"comment": "I started working on this task."},
        headers=auth_headers(client, users["employee"].email),
    )

    assert response.status_code == 201
    assert response.json()["data"]["comment"] == "I started working on this task."
