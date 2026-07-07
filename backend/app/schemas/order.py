import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from app.models.enums import OrderStatus, OrderType, PaymentMethod


class OrderItemCreate(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int = Field(gt=0)
    unit_price: Optional[float] = None  # Ignored: server fetches authoritative DB price.
    special_instructions: Optional[str] = None


class OrderGuestCreate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    nationality: Optional[str] = None


class OrderCreate(BaseModel):
    outlet_id: uuid.UUID
    guest_id: Optional[uuid.UUID] = None
    guest: Optional[OrderGuestCreate] = None
    items: List[OrderItemCreate]
    payment_method: PaymentMethod = PaymentMethod.mpesa
    order_type: OrderType = OrderType.takeaway
    table_number: Optional[str] = None
    room_id: Optional[uuid.UUID] = None
    is_delivery: bool = False
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

    @property
    def branch_id(self) -> uuid.UUID:
        return self.outlet_id

    @property
    def customer_id(self) -> uuid.UUID:
        return self.guest_id


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    menu_item_id: uuid.UUID
    quantity: int
    unit_price_kes_cents: int
    subtotal_kes_cents: int
    special_instructions: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    outlet_id: uuid.UUID
    guest_id: uuid.UUID
    cashier_id: Optional[uuid.UUID] = None
    status: OrderStatus
    total_kes_cents: int
    payment_client_secret: Optional[str] = None
    order_type: OrderType
    table_number: Optional[str] = None
    room_id: Optional[uuid.UUID] = None
    is_delivery: bool
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
