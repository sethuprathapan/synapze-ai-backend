from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    comment: str


class CommentResponse(BaseModel):
    id: int

    task_id: int

    user_id: int

    comment: str

    created_at: datetime

    model_config = {"from_attributes": True}
