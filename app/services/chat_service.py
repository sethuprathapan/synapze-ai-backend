from app.schemas.chat import ChatRequest
from app.utils.prompts import INTERVIEWER_PROMPT

def process_chat(req: ChatRequest):
    # LLM logic will come later
    return {
        "mode": req.mode,
        "reply": f"Interview question for: {req.message}"
    }
