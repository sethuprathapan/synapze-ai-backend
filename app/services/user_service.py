from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def list_users(db: Session) -> list[User]:
        return db.query(User).order_by(User.created_at.desc()).all()

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
        user = UserService.get_user(db, user_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing_user = (
                db.query(User)
                .filter(User.email == update_data["email"], User.id != user_id)
                .first()
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists",
                )

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = UserService.get_user(db, user_id)
        db.delete(user)
        db.commit()
