from typing import Optional
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import BaseModelMixin


class Guest(Base, BaseModelMixin):
    __tablename__ = "guests"

    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    nationality: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    id_document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    total_spend_kes_cents: Mapped[int] = mapped_column(Integer, default=0)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


Customer = Guest
