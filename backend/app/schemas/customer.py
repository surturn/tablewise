import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class CustomerBase(BaseModel):
    phone_number: str
    full_name: str
    email: Optional[EmailStr] = None

class CustomerCreate(CustomerBase):
    """Schema for creating or registering a new customer."""
    pass

class CustomerResponse(CustomerBase):
    """Schema for returning customer data."""
    id: uuid.UUID
    loyalty_points: int
    model_config = ConfigDict(from_attributes=True)