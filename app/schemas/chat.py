from pydantic import BaseModel

class ChatRequest(BaseModel):
    mode: str
    message: str
