from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "taskflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.beat_schedule = {
    "scan-overdue-tasks-every-minute": {
        "task": "app.worker.scan_overdue_tasks_job",
        "schedule": 60.0,
    }
}
