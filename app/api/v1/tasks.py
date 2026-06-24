from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import ApiResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.task_history import TaskHistoryResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskService.create_task(
        db=db,
        payload=payload,
        current_user=current_user,
        background_tasks=background_tasks,
    )

    return {
        "success": True,
        "message": "Task created successfully",
        "data": TaskResponse.model_validate(task),
    }


@router.get("", response_model=ApiResponse)
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = TaskService.list_tasks(db=db, current_user=current_user)
    return {
        "success": True,
        "message": "Tasks fetched successfully",
        "data": [TaskResponse.model_validate(task) for task in tasks],
    }


@router.get("/{task_id}", response_model=ApiResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskService.get_task(db=db, task_id=task_id, current_user=current_user)
    return {
        "success": True,
        "message": "Task fetched successfully",
        "data": TaskResponse.model_validate(task),
    }


@router.patch("/{task_id}", response_model=ApiResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskService.update_task(
        db=db,
        task_id=task_id,
        payload=payload,
        current_user=current_user,
        background_tasks=background_tasks,
    )

    return {
        "success": True,
        "message": "Task updated successfully",
        "data": TaskResponse.model_validate(task),
    }


@router.delete("/{task_id}", response_model=ApiResponse)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TaskService.delete_task(db=db, task_id=task_id, current_user=current_user)
    return {"success": True, "message": "Task deleted successfully", "data": None}


@router.get("/{task_id}/history", response_model=ApiResponse)
def list_task_history(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = TaskService.list_history(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )
    return {
        "success": True,
        "message": "Task history fetched successfully",
        "data": [TaskHistoryResponse.model_validate(item) for item in history],
    }


@router.post(
    "/{task_id}/comments",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = TaskService.add_comment(
        db=db,
        task_id=task_id,
        payload=payload,
        current_user=current_user,
    )
    return {
        "success": True,
        "message": "Comment added successfully",
        "data": CommentResponse.model_validate(comment),
    }


@router.get("/{task_id}/comments", response_model=ApiResponse)
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comments = TaskService.list_comments(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )

    return {
        "success": True,
        "message": "Comments fetched successfully",
        "data": [CommentResponse.model_validate(comment) for comment in comments],
    }
