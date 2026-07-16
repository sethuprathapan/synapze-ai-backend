from datetime import datetime
from enum import Enum


from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    password_hash: str | None = None

    model_config = {"from_attributes": True}
