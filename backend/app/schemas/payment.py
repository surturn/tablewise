import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import PaymentEntityType, PaymentMethod, PaymentStatus


class PaymentIntentRequest(BaseModel):
    entity_type: PaymentEntityType
    entity_id: uuid.UUID
    phone_number: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class PaymentIntentResponse(BaseModel):
    checkout_request_id: str
    merchant_request_id: str
    amount_kes_cents: int


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
    amount_kes_cents: int
    method: PaymentMethod
    status: PaymentStatus
    mpesa_checkout_request_id: Optional[str] = None
    mpesa_merchant_request_id: Optional[str] = None
    mpesa_receipt_number: Optional[str] = None
    phone_number: Optional[str] = None
    receipt_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
