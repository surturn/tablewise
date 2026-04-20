import base64
import logging
from datetime import datetime
import httpx
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.order import Order
from app.models.payment import Payment
from app.models.enums import OrderStatus, PaymentStatus, PaymentMethod
from app.schemas.payment import MpesaWebhookPayload

logger = logging.getLogger(__name__)


def format_phone_number(phone: str) -> str:
    """Formats phone number to the required 2547XXXXXXXX format for Daraja."""
    cleaned = ''.join(filter(str.isdigit, phone))
    if cleaned.startswith('0'):
        return f"254{cleaned[1:]}"
    if cleaned.startswith('254'):
        return cleaned
    if len(cleaned) == 9:
        return f"254{cleaned}"
    return cleaned


async def get_mpesa_access_token() -> str:
    """Generates the OAuth2 token required for Daraja API requests."""
    # In sandbox, the auth URL is different from production
    base_url = "https://sandbox.safaricom.co.ke" if settings.MPESA_ENVIRONMENT == "sandbox" else "https://api.safaricom.co.ke"
    auth_url = f"{base_url}/oauth/v1/generate?grant_type=client_credentials"

    auth_str = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {"Authorization": f"Basic {encoded_auth}"}


    # Use httpx for async HTTP requests
    async with httpx.AsyncClient() as client:
        response = await client.get(auth_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get M-Pesa token: {response.text}")
            raise HTTPException(status_code=500, detail="Payment gateway authentication failed")
        return response.json()["access_token"]


async def initiate_stk_push(db: AsyncSession, order_id: uuid.UUID, phone_number: str) -> dict:
    """Initiates the STK Push prompt on the customer's phone."""
    # 1. Validate Order
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in [OrderStatus.CREATED, OrderStatus.PAYMENT_FAILED]:
        raise HTTPException(status_code=400, detail=f"Cannot initiate payment for order in {order.status.value} state")

    formatted_phone = format_phone_number(phone_number)
    amount = int(order.total_amount)  # M-Pesa expects integer amounts

    # 2. Prepare Daraja Payload
    token = await get_mpesa_access_token()
    base_url = "https://sandbox.safaricom.co.ke" if settings.MPESA_ENVIRONMENT == "sandbox" else "https://api.safaricom.co.ke"
    stk_url = f"{base_url}/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": formatted_phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": formatted_phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": str(order.id)[:12],  # Max 12 chars usually recommended
        "TransactionDesc": "TableWise Order Payment"
    }
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Send Request to Safaricom
    async with httpx.AsyncClient() as client:
        response = await client.post(stk_url, json=payload, headers=headers)

    response_data = response.json()

    if response.status_code != 200 or response_data.get("ResponseCode") != "0":
        logger.error(f"STK Push Failed: {response_data}")
        raise HTTPException(status_code=400, detail="Failed to initiate STK Push. Check phone number.")

    checkout_request_id = response_data["CheckoutRequestID"]

    # 4. Create Pending Payment Record & Update Order
    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=PaymentMethod.MPESA,
        status=PaymentStatus.PENDING,
        checkout_request_id=checkout_request_id,
        payer_phone_number=formatted_phone
    )
    db.add(payment)
    order.status = OrderStatus.PENDING_PAYMENT
    await db.commit()
    await db.refresh(payment)

    return {
        "message": "STK Push initiated successfully. Please enter PIN on your phone.",
        "checkout_request_id": checkout_request_id
    }


async def process_mpesa_webhook(db: AsyncSession, payload: MpesaWebhookPayload) -> dict:
    """Processes the asynchronous callback from Safaricom."""
    stk_callback = payload.Body.stkCallback
    checkout_request_id = stk_callback.CheckoutRequestID
    result_code = stk_callback.ResultCode

    # 1. Find the payment by checkout_request_id
    result = await db.execute(select(Payment).where(Payment.checkout_request_id == checkout_request_id))
    payment = result.scalars().first()

    if not payment:
        logger.warning(f"Webhook received for unknown CheckoutRequestID: {checkout_request_id}")
        return {"status": "ignored", "reason": "Payment not found"}

    # Idempotency check: If already processed, return success immediately
    if payment.status in [PaymentStatus.SUCCESS, PaymentStatus.FAILED]:
        return {"status": "success", "message": "Already processed"}

    # Fetch associated order
    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalars().first()

    # 2. Process Result (0 means Success in Daraja)
    if result_code == 0:
        payment.status = PaymentStatus.SUCCESS
        order.status = OrderStatus.PAID

        # Extract MpesaReceiptNumber from metadata
        if stk_callback.CallbackMetadata:
            for item in stk_callback.CallbackMetadata.Item:
                if item.Name == "MpesaReceiptNumber":
                    payment.mpesa_receipt_number = item.Value
    else:
        # User cancelled, timed out, insufficient funds, etc.
        payment.status = PaymentStatus.FAILED
        order.status = OrderStatus.PAYMENT_FAILED
        logger.info(f"Payment failed: {stk_callback.ResultDesc}")

    await db.commit()

    # Note: In Step 14 (Inventory mapping), this is where we would trigger the Celery
    # task to finalize inventory deduction permanently.

    return {"status": "success", "message": "Webhook processed successfully"}