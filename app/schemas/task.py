from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    project_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    assignee_id: int | None = Field(default=None, gt=0)
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    assignee_id: int | None = Field(default=None, gt=0)
    due_date: datetime | None = None


class TaskReplace(TaskCreate):
    pass


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    assignee_id: int | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    items: list[TaskResponse]
    total: int
    limit: int
    offset: int
