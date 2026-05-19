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
    model_config = ConfigDict(from_attributes=True)


CustomerCreate = GuestCreate
CustomerResponse = GuestResponse
