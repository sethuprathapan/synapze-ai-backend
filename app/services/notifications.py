from datetime import datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.notification import Notification
from app.models.task import Task, TaskStatus

notification_session_factory = SessionLocal


def set_notification_session_factory(session_factory) -> None:
    global notification_session_factory
    notification_session_factory = session_factory


def create_notification(db: Session, task: Task, notification_type: str, message: str) -> Notification:
    notification = Notification(
        task_id=task.id,
        user_id=task.assignee_id,
        type=notification_type,
        message=message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_status_change_notification(task_id: int, old_status: str, new_status: str) -> None:
    db = notification_session_factory()
    try:
        task = db.get(Task, task_id)
        if task:
            create_notification(
                db,
                task,
                "status_changed",
                f'Task "{task.title}" changed from {old_status} to {new_status}.',
            )
    finally:
        db.close()


def create_reassignment_notification(task_id: int) -> None:
    db = notification_session_factory()
    try:
        task = db.get(Task, task_id)
        if task:
            create_notification(
                db,
                task,
                "task_reassigned",
                f'Task "{task.title}" was assigned to you.',
            )
    finally:
        db.close()


def scan_overdue_tasks() -> int:
    db = notification_session_factory()
    try:
        overdue_tasks = (
            db.query(Task)
            .filter(Task.due_date < datetime.utcnow())
            .filter(Task.status != TaskStatus.DONE.value)
            .filter(Task.overdue_notified_at.is_(None))
            .all()
        )
        for task in overdue_tasks:
            create_notification(
                db,
                task,
                "task_overdue",
                f'Task "{task.title}" is overdue.',
            )
            task.overdue_notified_at = datetime.utcnow()
            db.add(task)
        db.commit()
        return len(overdue_tasks)
    finally:
        db.close()
