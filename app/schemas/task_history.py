from datetime import datetime

from pydantic import BaseModel


class TaskHistoryResponse(BaseModel):
    id: int

    task_id: int

    old_status: str

    new_status: str

    changed_by: int

    changed_at: datetime

    model_config = {"from_attributes": True}
