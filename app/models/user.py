from datetime import datetime


from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(
        Enum("admin", "manager", "employee", name="user_role_enum")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
