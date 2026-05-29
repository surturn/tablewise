import asyncio
import json
import logging
import re
import uuid
from typing import Any
import africastalking
from datetime import datetime, timezone
from anthropic import AsyncAnthropic
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.celery_worker import celery_app
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.inventory_item import InventoryItem
from app.models.operations import AuditLog, StockMovement
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.invite import InviteToken

logger = logging.getLogger(__name__)
africastalking.initialize(settings.AFRICASTALKING_USERNAME or settings.AT_USERNAME, settings.AFRICASTALKING_API_KEY or settings.AT_API_KEY)
sms_service = africastalking.SMS


@celery_app.task(name="app.tasks.send_sms_notification", bind=True, max_retries=3)
def send_sms_notification(self, phone_number: str, message: str):
    try:
        if settings.ENVIRONMENT == "development" and (settings.AFRICASTALKING_API_KEY == "mock_key" or settings.AT_API_KEY == "mock_key"):
            logger.info("[CELERY MOCK SMS] To %s: %s", phone_number, message.replace("GrandPlatform", "GrandPlatform"))
            return {"status": "mock_success", "phone": phone_number}
        response = sms_service.send(message.replace("GrandPlatform", "GrandPlatform"), [phone_number])
        recipients = response.get("SMSMessageData", {}).get("Recipients", []) if isinstance(response, dict) else []
        status_code = recipients[0].get("statusCode") if recipients else 200
        if 400 <= int(status_code) < 500:
            logger.error("Permanent SMS failure for %s: %s", phone_number, response)
            _write_audit_sync("sms_permanent_failure", "sms", None, {"phone_number": phone_number, "response": response})
            return {"status": "permanent_failure", "response": response}
        if int(status_code) >= 500:
            raise RuntimeError(f"Africa's Talking gateway error: {response}")
        return response
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            logger.exception("SMS failed after retries for %s", phone_number)
            raise
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@celery_app.task(name="app.tasks.send_email")
def send_email(entity_id: str, template: str):
    logger.info("Queued GrandPlatform email template %s for %s", template, entity_id)
    return {"status": "queued", "entity_id": entity_id, "template": template}


@celery_app.task(name="app.tasks.schedule_housekeeping")
def schedule_housekeeping(room_id: str):
    logger.info("Housekeeping scheduled for room %s", room_id)
    return {"status": "scheduled", "room_id": room_id}


@celery_app.task(name="app.tasks.deduct_inventory")
def deduct_inventory(order_id: str):
    return asyncio.run(_deduct_inventory_async(order_id))


async def _deduct_inventory_async(order_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).options(selectinload(Order.items).selectinload(OrderItem.menu_item)).where(Order.id == uuid.UUID(order_id)))
        order = result.scalars().first()
        if not order:
            logger.warning("Inventory deduction skipped: order %s not found", order_id)
            return {"status": "missing_order"}
        deductions = []
        for item in order.items:
            menu_item = item.menu_item
            inv_result = await db.execute(
                select(InventoryItem)
                .where(InventoryItem.outlet_id == order.outlet_id, InventoryItem.name == menu_item.name)
                .with_for_update()
            )
            inventory_item = inv_result.scalars().first()
            if not inventory_item:
                logger.warning("No inventory row mapped by name for menu item %s in outlet %s", menu_item.id, order.outlet_id)
                continue
            old_qty = float(inventory_item.quantity)
            new_qty = old_qty - item.quantity
            if new_qty < 0:
                logger.warning("Inventory item %s would go negative (%.2f - %s); clamping to zero", inventory_item.id, old_qty, item.quantity)
                new_qty = 0
            inventory_item.quantity = new_qty
            db.add(StockMovement(inventory_item_id=inventory_item.id, change_quantity=-item.quantity, reason="order_deduction", user_id=order.cashier_id))
            deductions.append({"inventory_item_id": str(inventory_item.id), "old_quantity": old_qty, "new_quantity": new_qty})
        if deductions:
            db.add(AuditLog(action="inventory_deducted", entity_type="order", entity_id=order.id, new_value={"deductions": deductions}))
        await db.commit()
        return {"status": "deducted", "deductions": deductions}


@celery_app.task(name="app.tasks.generate_inventory_forecast")
def generate_inventory_forecast(outlet_id: str, historical_data_summary: str):
    return asyncio.run(_generate_inventory_forecast_async(outlet_id, historical_data_summary))


async def _generate_inventory_forecast_async(outlet_id: str, historical_data_summary: str):
    system_prompt = (
        'Respond only with a JSON array: [{"inventory_item_id":"uuid",'
        '"suggested_order_quantity":int,"unit":"string","reasoning":"string"}]. '
        "No markdown, no prose, no code fences."
    )
    if settings.ENVIRONMENT == "development" and settings.ANTHROPIC_API_KEY == "mock_key":
        return []
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Forecast outlet {outlet_id} from this data: {historical_data_summary}"}],
    )
    raw = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text")
    cleaned = _strip_code_fences(raw)
    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            raise ValueError("Claude forecast output was not a JSON array")
        return parsed
    except Exception:
        logger.exception("Claude forecast output was not parseable JSON: %s", raw)
        return []


def _strip_code_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.IGNORECASE | re.MULTILINE).strip()


def _write_audit_sync(action: str, entity_type: str, entity_id: str | None, new_value: dict[str, Any]):
    async def _write():
        async with AsyncSessionLocal() as db:
            db.add(AuditLog(action=action, entity_type=entity_type, entity_id=uuid.UUID(entity_id) if entity_id else None, new_value=new_value))
            await db.commit()
    asyncio.run(_write())

@celery_app.task(name="app.tasks.cleanup_expired_invites")
def cleanup_expired_invites():
    """Celery beat task that runs hourly to purge expired invite tokens."""
    return asyncio.run(_cleanup_expired_invites_async())

async def _cleanup_expired_invites_async():
    async with AsyncSessionLocal() as db:
        current_time_utc = datetime.now(timezone.utc)
        
        # Delete all tokens where the expiration time is in the past
        query = delete(InviteToken).where(InviteToken.expires_at < current_time_utc)
        result = await db.execute(query)
        
        deleted_count = result.rowcount
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} expired invite tokens.")
        return {"status": "success", "deleted_count": deleted_count}

