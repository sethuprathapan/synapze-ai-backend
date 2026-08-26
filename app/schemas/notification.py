from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int | None
    task_id: int
    type: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
