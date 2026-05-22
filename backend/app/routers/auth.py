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
from app.routers.deps import get_current_active_user, get_current_account
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
    logger.info("Login attempt for %s", form_data.username)
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

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