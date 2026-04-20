from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


async def get_or_create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
    """
    Looks up a customer by phone number. If they don't exist, creates them.
    This is perfect for an M-Pesa first flow where the phone number is the primary identity.
    """
    result = await db.execute(select(Customer).where(Customer.phone_number == customer_in.phone_number))
    existing_customer = result.scalars().first()

    if existing_customer:
        # Optionally update name/email if provided
        return existing_customer

    new_customer = Customer(**customer_in.model_dump())
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer