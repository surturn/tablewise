from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.payment import STKPushRequest, MpesaWebhookPayload
from app.services import payment_service

router = APIRouter()

@router.post("/stk-push", status_code=status.HTTP_200_OK)
async def initiate_payment(
    request: STKPushRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger an M-Pesa STK Push to the customer's phone for a specific order.
    Changes order status to PENDING_PAYMENT.
    """
    return await payment_service.initiate_stk_push(db, request.order_id, request.phone_number)

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def mpesa_callback(
    payload: MpesaWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Safaricom Daraja API Webhook Callback Endpoint.
    Receives the result of the STK Push and updates Order/Payment status idempotently.
    Note: Safaricom requires a 200 OK response quickly, or they will retry.
    """
    return await payment_service.process_mpesa_webhook(db, payload)