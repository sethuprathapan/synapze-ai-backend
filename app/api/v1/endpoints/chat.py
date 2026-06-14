from fastapi import APIRouter

from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()

chat_service = ChatService()


@router.post("/chat")
def chat(request: ChatRequest):

    answer = chat_service.get_response(request.message)

    return {"message": request.message, "answer": answer}
