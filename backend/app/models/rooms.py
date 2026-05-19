import uuid
from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import Date, Enum as SQLEnum, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import BookingPaymentStatus, BookingStatus, RoomStatus


class RoomType(Base, BaseModelMixin):
    __tablename__ = "room_types"

    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price_usd_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    amenities: Mapped[List[str]] = mapped_column(JSON, default=list)
    photos: Mapped[List[str]] = mapped_column(JSON, default=list)

    property: Mapped["Property"] = relationship("Property", back_populates="room_types")
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="room_type")


class Room(Base, BaseModelMixin):
    __tablename__ = "rooms"

    room_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("room_types.id", ondelete="CASCADE"), index=True)
    room_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RoomStatus] = mapped_column(SQLEnum(RoomStatus), default=RoomStatus.available, index=True)

    room_type: Mapped["RoomType"] = relationship("RoomType", back_populates="rooms")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="room")


class Booking(Base, BaseModelMixin):
    __tablename__ = "bookings"

    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="RESTRICT"), index=True)
    guest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="RESTRICT"), index=True)
    check_in: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_out: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), default=BookingStatus.pending, index=True)
    total_usd_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_status: Mapped[BookingPaymentStatus] = mapped_column(SQLEnum(BookingPaymentStatus), default=BookingPaymentStatus.unpaid)
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    room: Mapped["Room"] = relationship("Room", back_populates="bookings")
    guest: Mapped["Guest"] = relationship("Guest")
    extras: Mapped[List["BookingExtra"]] = relationship("BookingExtra", back_populates="booking", cascade="all, delete-orphan")


class BookingExtra(Base, BaseModelMixin):
    __tablename__ = "booking_extras"

    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_usd_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="extras")
