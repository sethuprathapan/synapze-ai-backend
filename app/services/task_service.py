from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate


class TaskService:

    @staticmethod
    def create_task(db: Session, payload: TaskCreate, assigned_by_id: int) -> Task:

        task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
            assigned_to_id=payload.assigned_to_id,
            assigned_by_id=assigned_by_id,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return task
