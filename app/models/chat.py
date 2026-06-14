from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_message: Mapped[str] = mapped_column(String(1000))

    ai_response: Mapped[str] = mapped_column(Text())

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
