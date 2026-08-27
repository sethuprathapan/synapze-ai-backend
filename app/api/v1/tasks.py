from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.core.config import settings
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.task import PaginatedTasks, TaskCreate, TaskReplace, TaskResponse, TaskUpdate
from app.services.cache import task_cache
from app.services.notifications import create_reassignment_notification, create_status_change_notification

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, payload.project_id, current_user.id)
    _validate_assignee(db, payload.assignee_id)
    task = Task(
        project_id=project.id,
        title=payload.title,
        description=payload.description,
        status=payload.status.value,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_cache.invalidate_owner(current_user.id)
    if task.assignee_id:
        _enqueue_reassignment(background_tasks, task.id)
    return ApiResponse(message="Task created", data=TaskResponse.model_validate(task))


@router.get("", response_model=ApiResponse)
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    assignee_id: int | None = None,
    due_from: datetime | None = None,
    due_to: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if due_from and due_to and due_from > due_to:
        raise HTTPException(status_code=400, detail="due_from must be before due_to")

    key = ":".join(
        [
            f"tasks:{current_user.id}",
            status_filter.value if status_filter else "",
            str(assignee_id or ""),
            due_from.isoformat() if due_from else "",
            due_to.isoformat() if due_to else "",
            str(limit),
            str(offset),
        ]
    )

    def load() -> dict:
        query = _owned_tasks_query(db, current_user.id)
        if status_filter:
            query = query.filter(Task.status == status_filter.value)
        if assignee_id is not None:
            query = query.filter(Task.assignee_id == assignee_id)
        if due_from:
            query = query.filter(Task.due_date >= due_from)
        if due_to:
            query = query.filter(Task.due_date <= due_to)
        total = query.count()
        tasks = query.order_by(Task.id.asc()).offset(offset).limit(limit).all()
        return PaginatedTasks(
            items=[TaskResponse.model_validate(task) for task in tasks],
            total=total,
            limit=limit,
            offset=offset,
        ).model_dump(mode="json")

    return ApiResponse(message="Tasks retrieved", data=task_cache.get_or_set(key, load))


@router.get("/{task_id}", response_model=ApiResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _owned_task(db, task_id, current_user.id)
    return ApiResponse(message="Task retrieved", data=TaskResponse.model_validate(task))


@router.patch("/{task_id}", response_model=ApiResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _owned_task(db, task_id, current_user.id)
    old_status = task.status
    old_assignee_id = task.assignee_id

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field is required")
    _validate_assignee(db, updates.get("assignee_id"))

    for field, value in updates.items():
        if isinstance(value, TaskStatus):
            value = value.value
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    task_cache.invalidate_owner(current_user.id)

    if old_status != task.status:
        _enqueue_status_change(background_tasks, task.id, old_status, task.status)
    if old_assignee_id != task.assignee_id and task.assignee_id:
        _enqueue_reassignment(background_tasks, task.id)

    return ApiResponse(message="Task updated", data=TaskResponse.model_validate(task))


@router.put("/{task_id}", response_model=ApiResponse)
def replace_task(
    task_id: int,
    payload: TaskReplace,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _owned_task(db, task_id, current_user.id)
    _owned_project(db, payload.project_id, current_user.id)
    _validate_assignee(db, payload.assignee_id)
    old_status = task.status
    old_assignee_id = task.assignee_id

    task.project_id = payload.project_id
    task.title = payload.title
    task.description = payload.description
    task.status = payload.status.value
    task.assignee_id = payload.assignee_id
    task.due_date = payload.due_date

    db.add(task)
    db.commit()
    db.refresh(task)
    task_cache.invalidate_owner(current_user.id)

    if old_status != task.status:
        _enqueue_status_change(background_tasks, task.id, old_status, task.status)
    if old_assignee_id != task.assignee_id and task.assignee_id:
        _enqueue_reassignment(background_tasks, task.id)

    return ApiResponse(message="Task replaced", data=TaskResponse.model_validate(task))


@router.delete("/{task_id}", response_model=ApiResponse)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _owned_task(db, task_id, current_user.id)
    db.delete(task)
    db.commit()
    task_cache.invalidate_owner(current_user.id)
    return ApiResponse(message="Task deleted", data=None)


def _owned_project(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project or project.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _owned_task(db: Session, task_id: int, owner_id: int) -> Task:
    task = _owned_tasks_query(db, owner_id).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _owned_tasks_query(db: Session, owner_id: int):
    return db.query(Task).join(Project).filter(Project.owner_id == owner_id)


def _validate_assignee(db: Session, assignee_id: int | None) -> None:
    if assignee_id is not None and not db.get(User, assignee_id):
        raise HTTPException(status_code=400, detail="Assignee not found")


def _enqueue_reassignment(background_tasks: BackgroundTasks, task_id: int) -> None:
    if settings.BACKGROUND_JOBS == "celery":
        from app.worker import create_reassignment_notification_job

        create_reassignment_notification_job.delay(task_id)
        return
    background_tasks.add_task(create_reassignment_notification, task_id)


def _enqueue_status_change(background_tasks: BackgroundTasks, task_id: int, old_status: str, new_status: str) -> None:
    if settings.BACKGROUND_JOBS == "celery":
        from app.worker import create_status_change_notification_job

        create_status_change_notification_job.delay(task_id, old_status, new_status)
        return
    background_tasks.add_task(create_status_change_notification, task_id, old_status, new_status)
