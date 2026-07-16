from pydantic import BaseModel, EmailStr


class ContactRequest(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
