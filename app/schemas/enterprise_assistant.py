from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Business question or action request for the assistant.",
    )


class AssistantAction(BaseModel):
    name: str
    status: str
    data: dict[str, Any] | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    action: AssistantAction | None = None
    source: str = "database-enterprise-assistant"
