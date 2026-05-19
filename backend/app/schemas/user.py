import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, model_validator
from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    role: UserRole
    is_active: bool = True
    outlet_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def validate_outlet_for_staff(self):
        if self.role not in [UserRole.owner, UserRole.hotel_manager] and self.outlet_id is None:
            raise ValueError("outlet_id is required for outlet-scoped staff roles")
        return self


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
