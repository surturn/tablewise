import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.enums import BookingStatus, UserRole
from app.models.user import User
from app.models.customer import Guest
from typing import Union
from app.routers.deps import require_roles, get_optional_current_account, get_current_user_or_customer
from app.schemas.booking import BookingCreate, BookingExtraCreate, BookingResponse, BookingStatusUpdate
from app.schemas.common import PaginatedResponse, paginate_response
from app.schemas.payment import PaymentIntentResponse
from app.services import booking_service, payment_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def list_bookings(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), status_filter: Optional[BookingStatus] = Query(None, alias="status"), date_from: Optional[date] = None, date_to: Optional[date] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    items, total = await booking_service.list_bookings(db, page, limit, status_filter, date_from, date_to)
    return paginate_response(items, total, page, limit)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_account: Optional[Union[User, Guest]] = Depends(get_optional_current_account),
    x_captcha_token: Optional[str] = Header(None, alias="X-Captcha-Token")
):
    from app.utils.captcha import verify_hcaptcha
    if isinstance(current_account, Guest):
        payload.guest.full_name = current_account.full_name
        payload.guest.email = current_account.email
        payload.guest.phone_number = current_account.phone_number
    else:
        await verify_hcaptcha(x_captcha_token)
    return await booking_service.create_booking(db, payload.room_type_id, payload.guest.model_dump(), payload.check_in, payload.check_out, [e.model_dump() for e in payload.extras], payload.notes)


@router.get("/{booking_id}/", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_account: Union[User, Guest] = Depends(get_current_user_or_customer)
):
    from fastapi import HTTPException
    booking = await booking_service.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if isinstance(current_account, Guest):
        if booking.guest_id != current_account.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    else:
        if current_account.role not in [UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]:
            raise HTTPException(status_code=403, detail="Not authorized to view bookings")
            
    return booking


@router.put("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(booking_id: uuid.UUID, payload: BookingStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    return await booking_service.update_booking_status(db, booking_id, payload.status, current_user.id)


@router.post("/{booking_id}/extras", response_model=BookingResponse)
async def add_booking_extra(booking_id: uuid.UUID, extra: BookingExtraCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    from app.models.rooms import BookingExtra
    booking = await booking_service.get_booking(db, booking_id)
    db.add(BookingExtra(booking_id=booking_id, **extra.model_dump()))
    booking.total_usd_cents += extra.price_usd_cents
    await db.commit()
    return await booking_service.get_booking(db, booking_id)


@router.post("/{booking_id}/payment-intent", response_model=PaymentIntentResponse)
async def create_booking_payment_intent(
    booking_id: uuid.UUID, 
    customer_email: str, 
    db: AsyncSession = Depends(get_db),
    current_account: Union[User, Guest] = Depends(get_current_user_or_customer)
):
    from app.models.enums import PaymentEntityType
    from fastapi import HTTPException
    
    booking = await booking_service.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if isinstance(current_account, Guest) and booking.guest_id != current_account.id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")
        
    return await payment_service.create_payment_intent_for_entity(db, PaymentEntityType.booking, booking_id, customer_email, {})


@router.get("/calendar", response_model=PaginatedResponse[BookingResponse])
async def booking_calendar(date_from: date, date_to: date, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.receptionist]))):
    items, total = await booking_service.list_bookings(db, 1, 200, None, date_from, date_to)
    return paginate_response(items, total, 1, 200)
