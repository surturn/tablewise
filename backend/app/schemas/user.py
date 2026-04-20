import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.enums import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    role: UserRole
    is_active: bool = True
    branch_id: Optional[uuid.UUID] = None

class UserCreate(UserBase):
    """Schema for creating a new user. Includes plaintext password."""
    password: str

class UserResponse(UserBase):
    """Schema for returning user data (never includes password!)."""
    id: uuid.UUID

    # Pydantic v2 syntax to allow reading from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)