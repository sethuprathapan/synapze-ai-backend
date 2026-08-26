from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.permissions import require_roles
from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import UserAdminCreate, UserCreate, UserResponse
from app.schemas.common import ApiResponse

router = APIRouter(tags=["Users"])


@router.post("/signup", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    return _create_user(payload, db, role="user")


@router.post(
    "/users",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
def create_user(payload: UserAdminCreate, db: Session = Depends(get_db)):
    return _create_user(payload, db, role=payload.role)


def _create_user(payload: UserCreate, db: Session, role: str) -> ApiResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")

    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(message="User created", data=UserResponse.model_validate(user))
