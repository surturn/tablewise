import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import BookingPaymentStatus, BookingStatus, RoomStatus


class GuestBookingCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone_number: str
    nationality: Optional[str] = None
    id_document_type: Optional[str] = None


class BookingExtraCreate(BaseModel):
    name: str
    price_kes_cents: int = Field(ge=0)


class BookingCreate(BaseModel):
    room_type_id: uuid.UUID
    guest: GuestBookingCreate
    check_in: date
    check_out: date
    extras: list[BookingExtraCreate] = []
    notes: Optional[str] = None


class BookingExtraResponse(BookingExtraCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    guest_id: uuid.UUID
    check_in: date
    check_out: date
    status: BookingStatus
    total_kes_cents: int
    payment_status: BookingPaymentStatus
    mpesa_checkout_request_id: Optional[str] = None
    notes: Optional[str] = None
    extras: list[BookingExtraResponse] = []
    model_config = ConfigDict(from_attributes=True)


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class RoomTypeCreate(BaseModel):
    property_id: uuid.UUID
    name: str
    description: str = ""
    capacity: int = Field(gt=0)
    base_price_kes_cents: int = Field(gt=0)
    amenities: list[str] = []
    photos: list[str] = []


class RoomTypeResponse(RoomTypeCreate):
    id: uuid.UUID
    available_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class RoomResponse(BaseModel):
    id: uuid.UUID
    room_type_id: uuid.UUID
    room_number: str
    floor: int
    status: RoomStatus
    model_config = ConfigDict(from_attributes=True)


class RoomStatusUpdate(BaseModel):
    status: RoomStatus
