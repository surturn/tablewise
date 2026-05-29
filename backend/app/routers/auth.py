from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.services.auth_service import authenticate_user
from app.utils.jwt import create_access_token
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.schemas.customer import CustomerResponse
from app.schemas.invite import InviteCreate, InviteResponse, RegisterWithToken
from app.routers.deps import get_current_active_user, get_current_account
from app.models.user import User
from app.models.enums import UserRole
from app.services.invite_service import create_invite, approve_invite, consume_invite, validate_invite
from app.services.email_verification_service import create_verification_token, verify_email_token
from app.utils.security import get_password_hash
from sqlalchemy import select
from typing import Union

router = APIRouter()

import logging
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
async def login_access_token(
        db: AsyncSession = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login. Get an access token for future requests.
    Note: OAuth2PasswordRequestForm uses 'username' field, which we map to 'email'.
    """
    logger.warning(f"AUTH TRACE: Incoming login request. Parsed form_data.username='{form_data.username}'")
    
    result = await db.execute(select(User).where(User.email == form_data.username))
    user_obj = result.scalars().first()
    
    logger.warning(f"AUTH TRACE: User DB lookup result: {user_obj}")
    
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if user is None:
        if user_obj is None:
            logger.error("AUTH TRACE: 401 Unauthorized - User not found in database.")
        else:
            logger.error("AUTH TRACE: 401 Unauthorized - User found, but password verification failed.")
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        logger.error("AUTH TRACE: 400 Bad Request - User is inactive.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    logger.warning("AUTH TRACE: Authentication successful. Generating token.")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Generate JWT containing ID, Role, and Outlet
    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
        outlet_id=str(user.outlet_id) if user.outlet_id else None,
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=Union[UserResponse, CustomerResponse])
async def get_logged_in_account(
        current_account: Union[UserResponse, CustomerResponse] = Depends(get_current_account) # type: ignore
):
    """
    Test access token and return the currently logged-in account's profile.
    """
    if not current_account.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive account")
    return current_account


@router.post("/invite", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_new_invite(
    invite_data: InviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new invite token.
    Managers can create them (pending approval). Owners create them auto-approved.
    """
    if current_user.role not in [UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create invites")
        
    return await create_invite(db, invite_data, current_user)


@router.put("/invite/{token}/approve", response_model=InviteResponse)
async def approve_pending_invite(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Approve a pending invite token (Owner only).
    """
    return await approve_invite(db, token, current_user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_with_invite(
    data: RegisterWithToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new staff member using a valid, approved invite token.
    Role and outlet_id are strictly derived from the token.
    Account is created as inactive until email verification.
    """
    # 1. Validate the invite token (this ensures it exists, is approved, unused, and not expired)
    invite = await validate_invite(db, data.token)
    
    # 2. Ensure email is not already taken
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
    # 3. Create the user
    new_user = User(
        email=data.email,
        full_name=data.full_name,
        phone_number=data.phone_number,
        hashed_password=get_password_hash(data.password),
        role=invite.role,
        outlet_id=invite.outlet_id,
        is_active=False  # Requires email verification
    )
    db.add(new_user)
    
    # 4. Consume the invite token
    invite.is_used = True
    
    await db.commit()
    await db.refresh(new_user)
    
    # 5. Generate email verification token (in a real app, send this via email)
    verification_token = create_verification_token(new_user.email)
    logger.info(f"Verification token generated for {new_user.email}: {verification_token}")
    
    return new_user


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email via the signed token sent to their inbox.
    """
    user = await verify_email_token(db, token)
    return {"msg": "Email successfully verified. You can now log in."}