import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class GuestBase(BaseModel):
    phone_number: str
    full_name: str
    email: Optional[EmailStr] = None
    nationality: Optional[str] = None
    id_document_type: Optional[str] = None


class GuestCreate(GuestBase):
    pass


class GuestResponse(GuestBase):
    id: uuid.UUID
    loyalty_points: int
    total_spend_usd_cents: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# Auth schemas
class CustomerRegister(BaseModel):
    phone_number: str
    full_name: str
    email: EmailStr
    password: str


class CustomerLogin(BaseModel):
    email: EmailStr
    password: str


# Aliases for semantic clarity elsewhere in the codebase
CustomerCreate = GuestCreate
CustomerResponse = GuestResponse