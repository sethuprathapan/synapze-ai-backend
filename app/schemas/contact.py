from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=1, max_length=500)


class ContactResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
