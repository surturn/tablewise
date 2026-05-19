import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import PaymentEntityType, PaymentMethod, PaymentStatus


class PaymentIntentRequest(BaseModel):
    entity_type: PaymentEntityType
    entity_id: uuid.UUID
    customer_email: EmailStr
    metadata: Dict[str, str] = Field(default_factory=dict)


class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount_usd_cents: int


class CashMarkPaidResponse(BaseModel):
    entity_id: uuid.UUID
    entity_type: PaymentEntityType
    status: PaymentStatus
    method: PaymentMethod
    audit_logged: bool


class PaymentResponse(BaseModel):
    id: uuid.UUID
    entity_type: PaymentEntityType
    entity_id: uuid.UUID
    amount_usd_cents: int
    method: PaymentMethod
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    receipt_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
