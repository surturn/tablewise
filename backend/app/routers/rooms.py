import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.enums import RoomStatus, UserRole
from app.models.rooms import Booking, Room, RoomType
from app.models.user import User
from app.routers.deps import require_roles
from app.schemas.booking import RoomResponse, RoomStatusUpdate, RoomTypeCreate, RoomTypeResponse
from app.services.booking_service import get_available_rooms
from app.services.audit_service import write_audit_log

router = APIRouter()


@router.get("/room-types/", response_model=list[RoomTypeResponse])
async def list_room_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RoomType).order_by(RoomType.base_price_kes_cents))
    room_types = list(result.scalars().all())
    responses = []
    for room_type in room_types:
        available_count = await db.scalar(select(func.count(Room.id)).where(Room.room_type_id == room_type.id, Room.status == RoomStatus.available)) or 0
        responses.append(RoomTypeResponse.model_validate(room_type).model_copy(update={"available_count": available_count}))
    return responses


@router.get("/room-types/{room_type_id}/availability", response_model=list[RoomResponse])
async def room_type_availability(room_type_id: uuid.UUID, check_in: date, check_out: date, db: AsyncSession = Depends(get_db)):
    return await get_available_rooms(db, room_type_id, check_in, check_out)


@router.post("/room-types/", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(payload: RoomTypeCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager]))):
    room_type = RoomType(**payload.model_dump())
    db.add(room_type)
    await db.commit()
    await db.refresh(room_type)
    return RoomTypeResponse.model_validate(room_type).model_copy(update={"available_count": 0})


@router.put("/room-types/{room_type_id}/", response_model=RoomTypeResponse)
async def update_room_type(room_type_id: uuid.UUID, payload: RoomTypeCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager]))):
    room_type = await db.get(RoomType, room_type_id)
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    for key, value in payload.model_dump().items():
        setattr(room_type, key, value)
    await db.commit()
    await db.refresh(room_type)
    count = await db.scalar(select(func.count(Room.id)).where(Room.room_type_id == room_type.id, Room.status == RoomStatus.available)) or 0
    return RoomTypeResponse.model_validate(room_type).model_copy(update={"available_count": count})


@router.get("/rooms/", response_model=list[RoomResponse])
async def list_rooms(status_filter: RoomStatus | None = Query(None, alias="status"), db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    query = select(Room).order_by(Room.floor, Room.room_number)
    if status_filter:
        query = query.where(Room.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.put("/rooms/{room_id}/status", response_model=RoomResponse)
async def update_room_status(room_id: uuid.UUID, payload: RoomStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    old = room.status
    room.status = payload.status
    await write_audit_log(db, "room_status_changed", "room", room.id, current_user.id, old_value={"status": old.value}, new_value={"status": room.status.value})
    await db.commit()
    await db.refresh(room)
    return room
