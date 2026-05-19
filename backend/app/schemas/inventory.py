import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InventoryItemBase(BaseModel):
    name: str
    sku: Optional[str] = None
    quantity: float = 0.0
    unit: str
    low_stock_threshold: float = 10.0
    outlet_id: uuid.UUID


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    quantity_added: float
    reason: str = "manual_adjustment"


class InventoryItemResponse(InventoryItemBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
