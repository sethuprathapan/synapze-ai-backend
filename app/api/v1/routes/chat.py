from fastapi import APIRouter
from app.schemas.chat import ChatRequest
from app.services.chat_service import process_chat

router = APIRouter()

@router.post("/")
def chat(req: ChatRequest):
    return process_chat(req)
