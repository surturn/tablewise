import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.routers.deps import require_roles
from app.schemas.common import PaginatedResponse
from app.schemas.customer import GuestCreate, GuestResponse
from app.services import customer_service

router = APIRouter()


@router.post("/", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
async def create_guest(guest_in: GuestCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    return await customer_service.create_guest(db, guest_in)


@router.get("/", response_model=PaginatedResponse[GuestResponse])
async def list_guests(phone: Optional[str] = Query(None), page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    return await customer_service.get_guests(db, page=page, limit=limit, phone=phone)


@router.get("/{guest_id}", response_model=GuestResponse)
async def get_guest(guest_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    guest = await customer_service.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest
