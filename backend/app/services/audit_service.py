import uuid
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.operations import AuditLog


async def write_audit_log(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    old_value: Optional[dict[str, Any]] = None,
    new_value: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
    return entry
