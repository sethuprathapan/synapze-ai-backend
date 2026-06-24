from sqlalchemy.orm import Session

from app.models.chat import ChatMessage


class ChatService:
    def get_response(self, message: str, db: Session) -> str:
        try:
            from app.services.gemini_service import GeminiService

            answer = GeminiService().generate_response(message)
        except Exception:
            answer = "AI service is temporarily unavailable. Please try again later."

        chat_message = ChatMessage(user_message=message, ai_response=answer)
        db.add(chat_message)
        db.commit()

        return answer
