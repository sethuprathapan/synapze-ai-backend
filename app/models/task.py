from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), index=True)

    description: Mapped[str] = mapped_column(Text)

    priority: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", name="task_priority_enum")
    )

    status: Mapped[str] = mapped_column(
        Enum("pending", "in_progress", "completed", name="task_status_enum"),
        default="pending",
    )

    due_date: Mapped[datetime] = mapped_column(DateTime)

    assigned_to_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    assigned_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assigned_to = relationship(
        "User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks"
    )

    assigned_by = relationship(
        "User", foreign_keys=[assigned_by_id], back_populates="created_tasks"
    )

    comments = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )

    history = relationship(
        "TaskHistory", back_populates="task", cascade="all, delete-orphan"
    )
