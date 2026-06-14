from fastapi import FastAPI

from app.api.v1.endpoints.chat import router as chat_router

app = FastAPI(title="Synapze AI", version="1.0.0")

app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
