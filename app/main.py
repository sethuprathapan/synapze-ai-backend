from fastapi import FastAPI

# from app.api.v1.endpoints.chat import router as chat_router

from app.api.v1.users import router as users_router

from app.api.v1.auth import router as auth_router

# from app.api.v1.tasks import router as tasks_router

app = FastAPI(title="Synapze --The Task Manager", version="1.0.0")

# app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
# app.include_router(tasks_router, prefix="/api/v1", tags=["Tasks"])
