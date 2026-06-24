from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.notification_service import NotificationService

ADMIN = "admin"
MANAGER = "manager"
EMPLOYEE = "employee"


class TaskService:

    @staticmethod
    def create_task(
        db: Session,
        payload: TaskCreate,
        current_user: User,
        background_tasks: BackgroundTasks | None = None,
    ) -> Task:
        TaskService._ensure_manager_or_admin(current_user)
        assigned_to = TaskService._get_employee(db, payload.assigned_to_id)

        task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
            assigned_to_id=payload.assigned_to_id,
            assigned_by_id=current_user.id,
        )

        db.add(task)
        db.flush()
        db.add(
            TaskHistory(
                task_id=task.id,
                old_status="created",
                new_status=task.status,
                changed_by=current_user.id,
            )
        )
        db.commit()
        db.refresh(task)

        if background_tasks:
            background_tasks.add_task(
                NotificationService.send_task_assigned_email,
                task,
                assigned_to,
            )

        return task

    @staticmethod
    def list_tasks(db: Session, current_user: User) -> list[Task]:
        query = db.query(Task).order_by(Task.due_date.asc())
        if current_user.role == EMPLOYEE:
            query = query.filter(Task.assigned_to_id == current_user.id)
        return query.all()

    @staticmethod
    def get_task(db: Session, task_id: int, current_user: User) -> Task:
        task = db.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        TaskService._ensure_task_visible(task, current_user)
        return task

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        payload: TaskUpdate,
        current_user: User,
        background_tasks: BackgroundTasks | None = None,
    ) -> Task:
        TaskService._ensure_manager_or_admin(current_user)
        task = TaskService.get_task(db, task_id, current_user)
        update_data = payload.model_dump(exclude_unset=True)

        if "assigned_to_id" in update_data:
            TaskService._get_employee(db, update_data["assigned_to_id"])

        old_status = task.status
        for field, value in update_data.items():
            setattr(task, field, value)

        if "status" in update_data and task.status != old_status:
            db.add(
                TaskHistory(
                    task_id=task.id,
                    old_status=old_status,
                    new_status=task.status,
                    changed_by=current_user.id,
                )
            )

        db.commit()
        db.refresh(task)

        if background_tasks and "status" in update_data and task.status != old_status:
            background_tasks.add_task(
                NotificationService.send_task_status_updated_email,
                task,
                task.assigned_to,
            )

        return task

    @staticmethod
    def delete_task(db: Session, task_id: int, current_user: User) -> None:
        if current_user.role != ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete tasks",
            )
        task = TaskService.get_task(db, task_id, current_user)
        db.delete(task)
        db.commit()

    @staticmethod
    def list_history(db: Session, task_id: int, current_user: User) -> list[TaskHistory]:
        task = TaskService.get_task(db, task_id, current_user)
        return (
            db.query(TaskHistory)
            .filter(TaskHistory.task_id == task.id)
            .order_by(TaskHistory.changed_at.desc())
            .all()
        )

    @staticmethod
    def add_comment(
        db: Session,
        task_id: int,
        payload: CommentCreate,
        current_user: User,
    ) -> Comment:
        task = TaskService.get_task(db, task_id, current_user)
        comment = Comment(
            task_id=task.id,
            user_id=current_user.id,
            comment=payload.comment,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def list_comments(db: Session, task_id: int, current_user: User) -> list[Comment]:
        task = TaskService.get_task(db, task_id, current_user)
        return (
            db.query(Comment)
            .filter(Comment.task_id == task.id)
            .order_by(Comment.created_at.asc())
            .all()
        )

    @staticmethod
    def _ensure_manager_or_admin(current_user: User) -> None:
        if current_user.role not in {ADMIN, MANAGER}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and managers can perform this action",
            )

    @staticmethod
    def _ensure_task_visible(task: Task, current_user: User) -> None:
        if current_user.role == EMPLOYEE and task.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access tasks assigned to you",
            )

    @staticmethod
    def _get_employee(db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )
        if user.role != EMPLOYEE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tasks can only be assigned to employees",
            )
        return user
