from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = UserService.create_user(db=db, payload=payload)

    return {"success": True, "message": "User created successfully", "data": user}
