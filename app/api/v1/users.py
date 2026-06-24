from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.permissions import require_roles
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    user = UserService.create_user(db=db, payload=payload)

    return {
        "success": True,
        "message": "User created successfully",
        "data": UserResponse.model_validate(user),
    }


@router.get("", response_model=ApiResponse)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    users = UserService.list_users(db)
    return {
        "success": True,
        "message": "Users fetched successfully",
        "data": [UserResponse.model_validate(user) for user in users],
    }


@router.get("/{user_id}", response_model=ApiResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    user = UserService.get_user(db, user_id)
    return {
        "success": True,
        "message": "User fetched successfully",
        "data": UserResponse.model_validate(user),
    }


@router.patch("/{user_id}", response_model=ApiResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    user = UserService.update_user(db, user_id, payload)
    return {
        "success": True,
        "message": "User updated successfully",
        "data": UserResponse.model_validate(user),
    }


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    UserService.delete_user(db, user_id)
    return {"success": True, "message": "User deleted successfully", "data": None}
