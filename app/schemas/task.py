from enum import Enum
from datetime import datetime

from pydantic import BaseModel


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskCreate(BaseModel):
    title: str
    description: str

    priority: TaskPriority

    due_date: datetime

    assigned_to_id: int


class TaskResponse(BaseModel):
    id: int

    title: str

    description: str

    priority: TaskPriority

    status: TaskStatus

    due_date: datetime

    assigned_to_id: int

    assigned_by_id: int

    created_at: datetime

    model_config = {"from_attributes": True}
