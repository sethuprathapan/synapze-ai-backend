from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.auth import TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    token = AuthService.login(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )
