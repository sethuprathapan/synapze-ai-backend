from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("/")
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    token = AuthService.login(db=db, email=payload.email, password=payload.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": token, "token_type": "bearer"}
