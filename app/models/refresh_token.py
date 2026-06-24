from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    token: Mapped[str] = mapped_column(String(500), unique=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime)
