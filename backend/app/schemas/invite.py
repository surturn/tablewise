from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.enums import UserRole


class InviteCreate(BaseModel):
    role: UserRole
    outlet_id: Optional[uuid.UUID] = None


class InviteResponse(BaseModel):
    token: str
    role: UserRole
    outlet_id: Optional[uuid.UUID]
    expires_at: datetime
    is_used: bool
    is_approved: bool

    model_config = ConfigDict(from_attributes=True)


class RegisterWithToken(BaseModel):
    token: str
    email: EmailStr
    full_name: str
    phone_number: str
    password: str
