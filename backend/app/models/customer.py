from typing import Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import BaseModelMixin

class Customer(Base, BaseModelMixin):
    __tablename__ = "customers"

    # M-Pesa priority: Phone number is the primary identifier
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships to Orders will be defined in the Order model via back_populates