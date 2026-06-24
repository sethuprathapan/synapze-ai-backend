from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = TaskService.create_task(db=db, payload=payload, assigned_by_id=1)

    return {"success": True, "message": "Task created successfully", "data": task}
