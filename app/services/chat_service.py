from sqlalchemy.orm import Session

from app.models.chat import ChatMessage
from app.services.gemini_service import GeminiService


class ChatService:

    def __init__(self):
        self.gemini_service = GeminiService()

    def get_response(
        self,
        message: str,
        db: Session,
    ) -> str:

        ai_response = self.gemini_service.generate_response(message)

        chat_message = ChatMessage(
            user_message=message,
            ai_response=ai_response,
        )

        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)

        return ai_response
