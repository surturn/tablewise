import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class STKPushRequest(BaseModel):
    order_id: uuid.UUID
    phone_number: str = Field(..., description="Phone number to receive the prompt. E.g., 254712345678 or 0712345678")

class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    status: str
    message: str

# M-Pesa Webhook Schemas (Mapping Safaricom's exact JSON structure)
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