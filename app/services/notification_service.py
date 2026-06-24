import logging

from app.core.config import settings
from app.models.task import Task
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send_task_assigned_email(task: Task, assigned_to: User) -> None:
        logger.info(
            "Task assignment email queued",
            extra={
                "to": assigned_to.email,
                "from": settings.MAIL_FROM,
                "task_id": task.id,
                "task_title": task.title,
            },
        )

    @staticmethod
    def send_task_status_updated_email(task: Task, assigned_to: User) -> None:
        logger.info(
            "Task status update email queued",
            extra={
                "to": assigned_to.email,
                "from": settings.MAIL_FROM,
                "task_id": task.id,
                "task_status": task.status,
            },
        )
