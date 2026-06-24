from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    token = AuthService.login(db=db, email=payload.email, password=payload.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "success": True,
        "message": "Login successful",
        "data": TokenResponse(access_token=token),
    }
