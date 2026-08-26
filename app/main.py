from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.contact import router as contact_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.operations import metrics_middleware, router as operations_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.users import router as users_router

app = FastAPI(title="TaskFlow API", version="1.0.0")

app.middleware("http")(metrics_middleware)

app.include_router(operations_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(contact_router, prefix="/api/v1", tags=["Contact"])
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
