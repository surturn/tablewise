import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import OutletType


class OutletBase(BaseModel):
    property_id: Optional[uuid.UUID] = None
    type: OutletType = OutletType.restaurant
    name: str
    location: str
    contact_number: str
    is_active: bool = True
    opening_time: str = "08:00"
    closing_time: str = "22:00"


class OutletCreate(OutletBase):
    pass


class OutletResponse(OutletBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


BranchBase = OutletBase
BranchCreate = OutletCreate
BranchResponse = OutletResponse