from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        payload: UserCreate,
    ) -> User:

        existing_user = db.query(User).filter(User.email == payload.email).first()

        if existing_user:
            raise ValueError("User with this email already exists")

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:

        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:

        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[User]:

        return db.query(User).order_by(User.id.desc()).all()

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        payload: UserUpdate,
    ) -> User:

        user = UserService.get_by_id(
            db=db,
            user_id=user_id,
        )

        if not user:
            raise ValueError("User not found")

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)

            return user

        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def delete_user(
        db: Session,
        user_id: int,
    ) -> bool:

        user = UserService.get_by_id(
            db=db,
            user_id=user_id,
        )

        if not user:
            raise ValueError("User not found")

        db.delete(user)
        db.commit()

        return True
