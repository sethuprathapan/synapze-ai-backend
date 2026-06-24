from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    comment: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")

    user = relationship("User", back_populates="comments")
