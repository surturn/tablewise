import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import Branch, Customer
from app.models.order import Order
from app.models.payment import Payment
from app.models.enums import OrderStatus, PaymentStatus, PaymentMethod


@pytest.mark.asyncio
async def test_mpesa_webhook_success(async_client: AsyncClient, db_session: AsyncSession):
    """Integration test: Simulate Daraja Webhook and verify DB updates."""

    # 1. Setup raw DB records
    test_branch = Branch(name="Webhook Branch", location="Nairobi", contact_number="0700000000")
    db_session.add(test_branch)

    test_customer = Customer(phone_number="0700111222", full_name="Webhook User")
    db_session.add(test_customer)

    # Flush HERE so branch.id and customer.id are populated before Order references them
    await db_session.flush()

    test_order = Order(
        branch_id=test_branch.id,
        customer_id=test_customer.id,
        total_amount=100.0,
        status=OrderStatus.PENDING_PAYMENT
    )
    db_session.add(test_order)
    await db_session.flush()  # Populate test_order.id before Payment references it

    checkout_req_id = "ws_CO_1234567890"

    test_payment = Payment(
        order_id=test_order.id,
        amount=100.0,
        method=PaymentMethod.MPESA,
        status=PaymentStatus.PENDING,
        checkout_request_id=checkout_req_id
    )
    db_session.add(test_payment)
    await db_session.commit()

    # 2. Simulate Safaricom's successful STK push callback
    webhook_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": checkout_req_id,
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 100},
                        {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"}
                    ]
                }
            }
        }
    }

    # 3. Hit the webhook endpoint
    response = await async_client.post(f"{settings.API_V1_STR}/payments/webhook", json=webhook_payload)
    assert response.status_code == 200

    # 4. Verify DB state updated correctly
    await db_session.refresh(test_payment)
    await db_session.refresh(test_order)

    assert test_payment.status == PaymentStatus.SUCCESS
    assert test_payment.mpesa_receipt_number == "NLJ7RT61SV"
    assert test_order.status == OrderStatus.PAID