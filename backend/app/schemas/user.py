import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
    outlet_id: Optional[uuid.UUID] = None
    
    model_config = ConfigDict(from_attributes=True)
