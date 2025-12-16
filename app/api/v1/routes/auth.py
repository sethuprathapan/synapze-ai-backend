from fastapi import APIRouter
from app.schemas.auth import UserCreate
from app.services.auth_service import register_user

router = APIRouter()

@router.post("/register")
def register(user: UserCreate):
    return register_user(user)
