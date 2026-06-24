from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserService:

    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash="hashed_password",
            role=payload.role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
