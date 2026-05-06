import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class STKPushRequest(BaseModel):
    order_id: uuid.UUID
    phone_number: str = Field(..., description="Phone number to receive the mobile-money prompt.")


class StripeCheckoutRequest(BaseModel):
    order_id: uuid.UUID
    success_url: HttpUrl
    cancel_url: HttpUrl


class MobileMoneyRequest(BaseModel):
    order_id: uuid.UUID
    phone_number: str = Field(..., description="South Sudan/East Africa mobile number to receive a payment prompt.")
    provider: str = Field("africas_talking", description="Configured mobile-money provider, e.g. africas_talking or mpesa.")


class CashPaymentRequest(BaseModel):
    order_id: uuid.UUID
    collection_note: Optional[str] = Field(None, description="Optional till, rider, room, or table reference for reconciliation.")


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    status: str
    message: str


# M-Pesa Webhook Schemas (legacy compatibility for Safaricom/Daraja payloads)
class MpesaCallbackItem(BaseModel):
    Name: str
    Value: Optional[Any] = None


class MpesaCallbackMetadata(BaseModel):
    Item: List[MpesaCallbackItem]


class MpesaStkCallback(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: int
    ResultDesc: str
    CallbackMetadata: Optional[MpesaCallbackMetadata] = None


class MpesaWebhookBody(BaseModel):
    stkCallback: MpesaStkCallback


class MpesaWebhookPayload(BaseModel):
    Body: MpesaWebhookBody


class GenericPaymentWebhook(BaseModel):
    provider: str
    reference: str
    status: str
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
