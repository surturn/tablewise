from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.config import settings
from app.rate_limit import limiter
from app.models.customer import Guest
from app.models.enums import UserRole
from app.schemas.token import Token
from app.schemas.customer import CustomerRegister, CustomerLogin, CustomerResponse
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer
import pydantic

router = APIRouter()

# Reusing token extraction logic specifically for guests (since deps.py get_current_user expects a User)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/customer/login")

async def get_current_customer(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Guest:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
        
    result = await db.execute(select(Guest).where(Guest.id == sub))
    guest = result.scalars().first()
    
    if not guest:
        raise credentials_exception
        
    if not guest.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    return guest

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def customer_register(
    payload: CustomerRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new customer account and return a JWT."""
    # Check for existing email
    result = await db.execute(select(Guest).where(Guest.email == payload.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Check for existing phone
    result = await db.execute(select(Guest).where(Guest.phone_number == payload.phone_number))
    existing_by_phone = result.scalars().first()
    
    if existing_by_phone and existing_by_phone.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists",
        )

    if existing_by_phone:
        # Guest exists from a staff-created order but has no password — upgrade to registered
        existing_by_phone.email = payload.email
        existing_by_phone.full_name = payload.full_name
        existing_by_phone.hashed_password = get_password_hash(payload.password)
        guest = existing_by_phone
    else:
        guest = Guest(
            phone_number=payload.phone_number,
            full_name=payload.full_name,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
        )
        db.add(guest)

    await db.commit()
    await db.refresh(guest)

    access_token = create_access_token(
        subject=str(guest.id),
        role=UserRole.customer,
        account_type="guest",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
@limiter.limit("5/15minutes")
async def customer_login(
    request: Request,
    payload: CustomerLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a customer and return a JWT."""
    result = await db.execute(select(Guest).where(Guest.email == payload.email))
    guest = result.scalars().first()

    if not guest or not guest.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(payload.password, guest.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not guest.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account disabled")

    access_token = create_access_token(
        subject=str(guest.id),
        role=UserRole.customer,
        account_type="guest",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=CustomerResponse)
async def get_logged_in_customer(
    current_customer: Guest = Depends(get_current_customer)
):
    """
    Test access token and return the currently logged-in customer's profile.
    """
    return current_customer
