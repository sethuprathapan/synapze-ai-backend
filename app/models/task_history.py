from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TaskHistory(Base):
    __tablename__ = "task_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)

    old_status: Mapped[str] = mapped_column(String(50))

    new_status: Mapped[str] = mapped_column(String(50))

    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="history")

    changed_by_user = relationship("User", back_populates="status_changes")
