from datetime import datetime

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(
        Enum(
            "admin",
            "manager",
            "employee",
            name="user_role_enum"
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    assigned_tasks = relationship(
        "Task",
        foreign_keys="Task.assigned_to_id",
        back_populates="assigned_to"
    )

    created_tasks = relationship(
        "Task",
        foreign_keys="Task.assigned_by_id",
        back_populates="assigned_by"
    )

    comments = relationship(
        "Comment",
        back_populates="user"
    )

    status_changes = relationship(
        "TaskHistory",
        back_populates="changed_by_user"
    )