from app.celery_app import celery_app
from app.services.notifications import (
    create_reassignment_notification,
    create_status_change_notification,
    scan_overdue_tasks,
)


@celery_app.task(name="app.worker.create_reassignment_notification_job")
def create_reassignment_notification_job(task_id: int) -> None:
    create_reassignment_notification(task_id)


@celery_app.task(name="app.worker.create_status_change_notification_job")
def create_status_change_notification_job(task_id: int, old_status: str, new_status: str) -> None:
    create_status_change_notification(task_id, old_status, new_status)


@celery_app.task(name="app.worker.scan_overdue_tasks_job")
def scan_overdue_tasks_job() -> int:
    return scan_overdue_tasks()
