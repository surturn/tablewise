from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select

from app.database import get_db
from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services import customer_service

router = APIRouter()

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_200_OK)
async def register_or_login_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint for customers to identify themselves before checkout.
    Uses phone number as the primary identifier for M-Pesa.
    """
    return await customer_service.get_or_create_customer(db, customer_in)
@router.get("/", response_model=List[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    """
    List all registered customers for the dashboard.
    """
    result = await db.execute(select(Customer))
    return list(result.scalars().all())