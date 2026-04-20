from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
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