from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.models.chat import ChatMessage
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()

chat_service = ChatService()


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    answer = chat_service.get_response(
        request.message,
        db,
    )

    return {
        "message": request.message,
        "answer": answer,
    }


@router.get("/chat/history")
def get_chat_history(db: Session = Depends(get_db)):
    chats = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).all()

    return chats
