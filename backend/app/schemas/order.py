import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import OrderStatus

class OrderItemCreate(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int
    special_instructions: Optional[str] = None

class OrderCreate(BaseModel):
    branch_id: uuid.UUID
    customer_id: uuid.UUID
    items: List[OrderItemCreate]
    is_delivery: bool = False
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: uuid.UUID
    menu_item_id: uuid.UUID
    quantity: int
    unit_price: float
    subtotal: float
    special_instructions: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: uuid.UUID
    branch_id: uuid.UUID
    customer_id: uuid.UUID
    cashier_id: Optional[uuid.UUID] = None
    status: OrderStatus
    total_amount: float
    is_delivery: bool
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse] =[]
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus