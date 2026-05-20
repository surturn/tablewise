import uuid
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Guest

# Added GuestResponse to the import list
from app.schemas.customer import GuestCreate, GuestResponse


async def create_guest(db: AsyncSession, guest_in: GuestCreate) -> Guest:
    result = await db.execute(select(Guest).where(Guest.phone_number == guest_in.phone_number))
    guest = result.scalars().first()
    if guest:
        return guest
    guest = Guest(**guest_in.model_dump())
    db.add(guest)
    await db.commit()
    await db.refresh(guest)
    return guest


async def get_guest(db: AsyncSession, guest_id: uuid.UUID) -> Guest | None:
    return await db.get(Guest, guest_id)


# Changed type hint to use GuestResponse instead of the SQLAlchemy Guest model
async def get_guests(db: AsyncSession, page: int = 1, limit: int = 50, phone: Optional[str] = None) -> tuple[list[Guest], int]:
    query = select(Guest).order_by(Guest.full_name)
    count_query = select(func.count(Guest.id))
    if phone:
        query = query.where(Guest.phone_number == phone)
        count_query = count_query.where(Guest.phone_number == phone)
    total = await db.scalar(count_query) or 0
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    return list(result.scalars().all()), total