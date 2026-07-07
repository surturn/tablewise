import base64
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.enums import PaymentEntityType, PaymentMethod, PaymentStatus
from app.models.payment import Payment

logger = logging.getLogger(__name__)

_DARAJA_HOSTS = {
    "sandbox": "https://sandbox.safaricom.co.ke",
    "production": "https://api.safaricom.co.ke",
}

_token_cache: dict[str, Any] = {"token": None, "expires_at": 0.0}


def _is_mock_mode() -> bool:
    return settings.ENVIRONMENT == "development" and settings.MPESA_CONSUMER_KEY == "mock_key"


def _base_url() -> str:
    return _DARAJA_HOSTS.get(settings.MPESA_ENV, _DARAJA_HOSTS["sandbox"])


async def _get_access_token() -> str:
    if _token_cache["token"] and _token_cache["expires_at"] > time.monotonic():
        return _token_cache["token"]

    async with httpx.AsyncClient(base_url=_base_url()) as client:
        response = await client.get(
            "/oauth/v1/generate",
            params={"grant_type": "client_credentials"},
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        )
        response.raise_for_status()
        data = response.json()

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.monotonic() + int(data.get("expires_in", 3599)) - 60
    return _token_cache["token"]


async def initiate_stk_push(
    db: AsyncSession,
    phone_number: str,
    amount_kes_cents: int,
    entity_type: PaymentEntityType,
    entity_id: uuid.UUID,
) -> dict[str, Any]:
    if amount_kes_cents <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")

    amount = max(1, round(amount_kes_cents / 100))

    if _is_mock_mode():
        checkout_request_id = f"mock_ws_CO_{uuid.uuid4().hex[:16]}"
        merchant_request_id = f"mock_{uuid.uuid4().hex[:12]}"
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        token = await _get_access_token()

        async with httpx.AsyncClient(base_url=_base_url()) as client:
            response = await client.post(
                "/mpesa/stkpush/v1/processrequest",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "BusinessShortCode": settings.MPESA_SHORTCODE,
                    "Password": password,
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": amount,
                    "PartyA": phone_number,
                    "PartyB": settings.MPESA_SHORTCODE,
                    "PhoneNumber": phone_number,
                    "CallBackURL": settings.MPESA_CALLBACK_URL,
                    "AccountReference": str(entity_id),
                    "TransactionDesc": f"TableWise {entity_type.value} payment",
                },
            )
            response.raise_for_status()
            data = response.json()

        checkout_request_id = data["CheckoutRequestID"]
        merchant_request_id = data["MerchantRequestID"]

    payment = Payment(
        entity_type=entity_type,
        entity_id=entity_id,
        amount_kes_cents=amount_kes_cents,
        method=PaymentMethod.mpesa,
        status=PaymentStatus.pending,
        mpesa_checkout_request_id=checkout_request_id,
        mpesa_merchant_request_id=merchant_request_id,
        phone_number=phone_number,
    )
    db.add(payment)
    await db.commit()

    return {
        "checkout_request_id": checkout_request_id,
        "merchant_request_id": merchant_request_id,
        "amount_kes_cents": amount_kes_cents,
    }


def _callback_items(callback: dict[str, Any]) -> dict[str, Any]:
    items = (callback.get("CallbackMetadata") or {}).get("Item") or []
    return {item.get("Name"): item.get("Value") for item in items if "Name" in item}


async def handle_mpesa_callback(db: AsyncSession, payload: dict[str, Any]) -> dict[str, Any]:
    """Handle a Safaricom Daraja STK push callback.

    Unlike Stripe, Daraja callbacks don't echo back arbitrary metadata, so the
    Payment row (and its entity_type/entity_id) is looked up by the
    CheckoutRequestID we generated and stored during initiate_stk_push.
    """
    from app.services import payment_service  # local import: avoid a service<->service import cycle

    callback = ((payload.get("Body") or {}).get("stkCallback")) or {}
    checkout_request_id = callback.get("CheckoutRequestID")
    result_code = callback.get("ResultCode")
    ack = {"ResultCode": 0, "ResultDesc": "Accepted"}

    if checkout_request_id is None or result_code is None:
        logger.warning("Unparseable M-Pesa callback payload: %s", payload)
        return ack

    result = await db.execute(select(Payment).where(Payment.mpesa_checkout_request_id == checkout_request_id))
    payment = result.scalars().first()
    if payment is None:
        logger.warning("M-Pesa callback for unknown CheckoutRequestID: %s", checkout_request_id)
        return ack

    if result_code == 0:
        items = _callback_items(callback)
        callback_amount = items.get("Amount")
        expected_amount = max(1, round(payment.amount_kes_cents / 100))

        if callback_amount is not None and round(float(callback_amount)) != expected_amount:
            logger.error(
                "M-Pesa callback amount mismatch for CheckoutRequestID=%s: expected %s, got %s. "
                "Payment left pending for manual reconciliation.",
                checkout_request_id,
                expected_amount,
                callback_amount,
            )
            return ack

        await payment_service.handle_payment_success(
            db, payment, mpesa_receipt_number=items.get("MpesaReceiptNumber")
        )
    else:
        await payment_service.handle_payment_failure(db, payment, reason=callback.get("ResultDesc"))

    return ack
