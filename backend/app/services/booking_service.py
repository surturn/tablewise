import uuid
from datetime import date
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.customer import Guest
from app.models.enums import BookingPaymentStatus, BookingStatus, RoomStatus
from app.models.rooms import Booking, BookingExtra, Room, RoomType
from app.services.audit_service import write_audit_log
from app.tasks import schedule_housekeeping, send_sms_notification


async def get_available_rooms(db: AsyncSession, room_type_id: uuid.UUID, check_in: date, check_out: date) -> list[Room]:
    if check_in >= check_out:
        raise HTTPException(status_code=400, detail="check_in must be before check_out")
    overlapping = select(Booking.room_id).where(
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.checked_in]),
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )
    result = await db.execute(
        select(Room)
        .where(Room.room_type_id == room_type_id, Room.status != RoomStatus.maintenance, Room.id.not_in(overlapping))
        .order_by(Room.room_number)
    )
    return list(result.scalars().all())


async def create_booking(db: AsyncSession, room_type_id: uuid.UUID, guest: dict, check_in: date, check_out: date, extras: list[dict], notes: str | None = None) -> Booking:
    rooms = await get_available_rooms(db, room_type_id, check_in, check_out)
    if not rooms:
        raise HTTPException(status_code=409, detail="No rooms available for the requested date range")
    room_type = await db.get(RoomType, room_type_id)
    nights = (check_out - check_in).days
    total = room_type.base_price_usd_cents * nights + sum(int(extra["price_usd_cents"]) for extra in extras)

    result = await db.execute(select(Guest).where(Guest.email == guest.get("email")) if guest.get("email") else select(Guest).where(Guest.phone_number == guest["phone_number"]))
    db_guest = result.scalars().first()
    if not db_guest:
        db_guest = Guest(**guest)
        db.add(db_guest)
        await db.flush()

    booking = Booking(room_id=rooms[0].id, guest_id=db_guest.id, check_in=check_in, check_out=check_out, status=BookingStatus.pending, payment_status=BookingPaymentStatus.unpaid, total_usd_cents=total, notes=notes)
    db.add(booking)
    await db.flush()
    for extra in extras:
        db.add(BookingExtra(booking_id=booking.id, name=extra["name"], price_usd_cents=int(extra["price_usd_cents"])))
    await db.commit()
    return await get_booking(db, booking.id)


async def list_bookings(db: AsyncSession, page: int, limit: int, status: Optional[BookingStatus] = None, date_from: Optional[date] = None, date_to: Optional[date] = None) -> tuple[list[Booking], int]:
    query = select(Booking).options(selectinload(Booking.extras), selectinload(Booking.room)).order_by(Booking.check_in.desc())
    count_query = select(func.count(Booking.id))
    filters = []
    if status:
        filters.append(Booking.status == status)
    if date_from:
        filters.append(Booking.check_out > date_from)
    if date_to:
        filters.append(Booking.check_in < date_to)
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    total = await db.scalar(count_query) or 0
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    return list(result.scalars().all()), total


async def get_booking(db: AsyncSession, booking_id: uuid.UUID) -> Booking | None:
    result = await db.execute(select(Booking).options(selectinload(Booking.extras), selectinload(Booking.room)).where(Booking.id == booking_id))
    return result.scalars().first()


async def update_booking_status(db: AsyncSession, booking_id: uuid.UUID, target: BookingStatus, user_id: uuid.UUID | None = None) -> Booking:
    booking = await get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    old = booking.status
    if target == BookingStatus.checked_in and old != BookingStatus.confirmed:
        raise HTTPException(status_code=400, detail="Only confirmed bookings can be checked in")
    booking.status = target
    room = await db.get(Room, booking.room_id)
    if target == BookingStatus.checked_in:
        room.status = RoomStatus.occupied
    elif target == BookingStatus.checked_out:
        room.status = RoomStatus.cleaning
        schedule_housekeeping.delay(str(room.id))
    await write_audit_log(db, "booking_status_changed", "booking", booking.id, user_id=user_id, old_value={"status": old.value}, new_value={"status": target.value})
    await db.commit()
    await db.refresh(booking)
    return await get_booking(db, booking_id)
