from fastapi import APIRouter
from app.api.v1.routes import auth, chat, resume, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
