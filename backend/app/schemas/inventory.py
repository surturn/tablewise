import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class InventoryItemBase(BaseModel):
    name: str
    sku: Optional[str] = None
    quantity: float = 0.0
    unit: str
    low_stock_threshold: float = 10.0
    branch_id: uuid.UUID

class InventoryItemCreate(InventoryItemBase):
    """Schema for creating a new inventory item."""
    pass

class InventoryItemUpdate(BaseModel):
    """Schema for adjusting stock levels manually."""
    quantity_added: float  # Can be negative to subtract

class InventoryItemResponse(InventoryItemBase):
    """Schema for returning inventory data."""
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)