import logging
import uuid
from typing import Optional

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.schemas.payment import MpesaWebhookPayload

logger = logging.getLogger(__name__)


def _amount_to_cents(amount) -> int:
    """Convert a persisted USD amount into integer cents for external gateways."""
    return int(round(float(amount) * 100))


async def _get_payable_order(db: AsyncSession, order_id: uuid.UUID) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in [OrderStatus.CREATED, OrderStatus.PAYMENT_FAILED, OrderStatus.PENDING_PAYMENT]:
        raise HTTPException(status_code=400, detail=f"Cannot initiate payment for order in {order.status.value} state")
    return order


async def _find_payment_for_order(db: AsyncSession, order_id: uuid.UUID) -> Optional[Payment]:
    result = await db.execute(select(Payment).where(Payment.order_id == order_id))
    return result.scalars().first()


async def _upsert_payment(
    db: AsyncSession,
    order: Order,
    *,
    amount,
    method: PaymentMethod,
    status: PaymentStatus,
    checkout_request_id: Optional[str] = None,
    payer_phone_number: Optional[str] = None,
    stripe_checkout_session_id: Optional[str] = None,
    stripe_payment_intent_id: Optional[str] = None,
    mobile_money_provider: Optional[str] = None,
    external_reference: Optional[str] = None,
) -> Payment:
    payment = await _find_payment_for_order(db, order.id)
    if not payment:
        payment = Payment(order_id=order.id, amount=amount, method=method, status=status)
        db.add(payment)

    payment.amount = amount
    payment.method = method
    payment.status = status
    payment.checkout_request_id = checkout_request_id or payment.checkout_request_id
    payment.payer_phone_number = payer_phone_number or payment.payer_phone_number
    payment.stripe_checkout_session_id = stripe_checkout_session_id or payment.stripe_checkout_session_id
    payment.stripe_payment_intent_id = stripe_payment_intent_id or payment.stripe_payment_intent_id
    payment.mobile_money_provider = mobile_money_provider or payment.mobile_money_provider
    payment.external_reference = external_reference or payment.external_reference
    return payment


async def initiate_stripe_checkout(
    db: AsyncSession,
    order_id: uuid.UUID,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout Session without making Stripe a hard availability dependency."""
    order = await _get_payable_order(db, order_id)
    amount_cents = _amount_to_cents(order.total_amount)

    if amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Order total must be greater than zero")

    if settings.ENVIRONMENT == "development" and settings.STRIPE_SECRET_KEY == "mock_key":
        session_id = f"cs_test_mock_{order.id.hex[:24]}"
        checkout_url = f"{settings.PUBLIC_APP_URL}/checkout/mock-stripe?session_id={session_id}"
    else:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.stripe.com/v1/checkout/sessions",
                auth=(settings.STRIPE_SECRET_KEY, ""),
                data={
                    "mode": "payment",
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "currency": "usd",
                    "line_items[0][quantity]": "1",
                    "line_items[0][price_data][currency]": "usd",
                    "line_items[0][price_data][unit_amount]": str(amount_cents),
                    "line_items[0][price_data][product_data][name]": f"Grand Platform Order {str(order.id)[:8]}",
                    "metadata[order_id]": str(order.id),
                },
            )
        if response.status_code >= 400:
            logger.error("Stripe Checkout failed: %s", response.text)
            raise HTTPException(status_code=502, detail="Card payment provider is temporarily unavailable")
        session = response.json()
        session_id = session["id"]
        checkout_url = session["url"]

    await _upsert_payment(
        db,
        order,
        amount=order.total_amount,
        method=PaymentMethod.STRIPE,
        status=PaymentStatus.PENDING,
        stripe_checkout_session_id=session_id,
        external_reference=session_id,
    )
    order.status = OrderStatus.PENDING_PAYMENT
    await db.commit()

    return {
        "message": "Stripe Checkout session created.",
        "payment_method": PaymentMethod.STRIPE.value,
        "checkout_session_id": session_id,
        "checkout_url": checkout_url,
    }


async def initiate_mobile_money_payment(
    db: AsyncSession,
    order_id: uuid.UUID,
    phone_number: str,
    provider: str = "africas_talking",
) -> dict:
    """Start a mobile-money collection through a configured aggregator or return a safe mock response."""
    order = await _get_payable_order(db, order_id)
    normalized_provider = provider.lower().strip()
    if normalized_provider not in settings.MOBILE_MONEY_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported mobile money provider: {provider}")

    reference = f"mm_{normalized_provider}_{order.id.hex[:20]}"
    if settings.ENVIRONMENT != "development" and settings.MOBILE_MONEY_COLLECTION_URL:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                settings.MOBILE_MONEY_COLLECTION_URL,
                json={
                    "provider": normalized_provider,
                    "amount_cents": _amount_to_cents(order.total_amount),
                    "currency": "USD",
                    "phone_number": phone_number,
                    "external_reference": reference,
                    "callback_url": settings.MOBILE_MONEY_CALLBACK_URL,
                },
                headers={"Authorization": f"Bearer {settings.MOBILE_MONEY_API_KEY}"},
            )
        if response.status_code >= 400:
            logger.error("Mobile money initiation failed: %s", response.text)
            raise HTTPException(status_code=502, detail="Mobile money provider is temporarily unavailable")
        reference = response.json().get("reference", reference)

    await _upsert_payment(
        db,
        order,
        amount=order.total_amount,
        method=PaymentMethod.MOBILE_MONEY,
        status=PaymentStatus.PENDING,
        checkout_request_id=reference,
        payer_phone_number=phone_number,
        mobile_money_provider=normalized_provider,
        external_reference=reference,
    )
    order.status = OrderStatus.PENDING_PAYMENT
    await db.commit()

    return {
        "message": "Mobile money payment initiated. Confirm the prompt on your phone.",
        "payment_method": PaymentMethod.MOBILE_MONEY.value,
        "provider": normalized_provider,
        "reference": reference,
    }


async def record_cash_payment(db: AsyncSession, order_id: uuid.UUID, collection_note: Optional[str] = None) -> dict:
    """Allow cash on delivery/front-desk payment so operations continue when gateways are offline."""
    order = await _get_payable_order(db, order_id)
    await _upsert_payment(
        db,
        order,
        amount=order.total_amount,
        method=PaymentMethod.CASH,
        status=PaymentStatus.PENDING,
        external_reference=collection_note or f"cash_{order.id.hex[:20]}",
    )
    order.status = OrderStatus.CONFIRMED
    await db.commit()

    return {
        "message": "Cash payment selected. Collect and reconcile at delivery, table close, or reception.",
        "payment_method": PaymentMethod.CASH.value,
        "status": PaymentStatus.PENDING.value,
    }


# Backward-compatible aliases for the previous M-Pesa API surface.
async def initiate_stk_push(db: AsyncSession, order_id: uuid.UUID, phone_number: str) -> dict:
    return await initiate_mobile_money_payment(db, order_id, phone_number, provider="mpesa")


async def process_mpesa_webhook(db: AsyncSession, payload: MpesaWebhookPayload) -> dict:
    """Processes asynchronous mobile-money callbacks using the legacy Daraja payload shape."""
    stk_callback = payload.Body.stkCallback
    checkout_request_id = stk_callback.CheckoutRequestID
    result_code = stk_callback.ResultCode

    result = await db.execute(select(Payment).where(Payment.checkout_request_id == checkout_request_id))
    payment = result.scalars().first()

    if not payment:
        logger.warning("Webhook received for unknown CheckoutRequestID: %s", checkout_request_id)
        return {"status": "ignored", "reason": "Payment not found"}

    if payment.status in [PaymentStatus.SUCCESS, PaymentStatus.FAILED]:
        return {"status": "success", "message": "Already processed"}

    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalars().first()

    if result_code == 0:
        payment.status = PaymentStatus.SUCCESS
        order.status = OrderStatus.PAID
        if stk_callback.CallbackMetadata:
            for item in stk_callback.CallbackMetadata.Item:
                if item.Name == "MpesaReceiptNumber":
                    payment.mpesa_receipt_number = item.Value
                    payment.external_reference = item.Value
    else:
        payment.status = PaymentStatus.FAILED
        order.status = OrderStatus.PAYMENT_FAILED
        logger.info("Payment failed: %s", stk_callback.ResultDesc)

    await db.commit()
    return {"status": "success", "message": "Webhook processed successfully"}
