from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.payment import CashPaymentRequest, MobileMoneyRequest, MpesaWebhookPayload, STKPushRequest, StripeCheckoutRequest
from app.services import payment_service

router = APIRouter()


@router.post("/stripe/checkout", status_code=status.HTTP_200_OK)
async def initiate_stripe_checkout(
    request: StripeCheckoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe Checkout session for USD card payment.
    Cash and mobile-money endpoints remain available if Stripe is unavailable.
    """
    return await payment_service.initiate_stripe_checkout(
        db,
        request.order_id,
        str(request.success_url),
        str(request.cancel_url),
    )


@router.post("/mobile-money", status_code=status.HTTP_200_OK)
async def initiate_mobile_money(
    request: MobileMoneyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a mobile-money collection via the configured aggregator.
    Useful for South Sudan mobile wallet rollout and as a Stripe availability hedge.
    """
    return await payment_service.initiate_mobile_money_payment(
        db,
        request.order_id,
        request.phone_number,
        request.provider,
    )


@router.post("/cash", status_code=status.HTTP_200_OK)
async def select_cash_payment(
    request: CashPaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Select cash on delivery/front-desk settlement so orders can continue offline."""
    return await payment_service.record_cash_payment(db, request.order_id, request.collection_note)


@router.post("/stk-push", status_code=status.HTTP_200_OK)
async def initiate_payment(
    request: STKPushRequest,
    db: AsyncSession = Depends(get_db),
):
    """Backward-compatible M-Pesa STK endpoint routed through the mobile-money abstraction."""
    return await payment_service.initiate_stk_push(db, request.order_id, request.phone_number)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def mpesa_callback(
    payload: MpesaWebhookPayload,
    db: AsyncSession = Depends(get_db),
):
    """Legacy Safaricom Daraja callback endpoint; kept for existing integrations/tests."""
    return await payment_service.process_mpesa_webhook(db, payload)
