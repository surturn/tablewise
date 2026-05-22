from typing import List, Callable, Union
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pydantic

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.customer import Guest
from app.models.enums import UserRole
from app.utils.jwt import decode_access_token
from app.schemas.token import TokenPayload

# OAuth2 scheme configures Swagger UI to send tokens automatically
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)
optional_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)


async def get_current_account(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(reusable_oauth2)
) -> Union[User, Guest]:
    """Dependency to extract and validate the account from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    try:
        token_data = TokenPayload(**payload)
    except pydantic.ValidationError:
        raise credentials_exception

    if token_data.sub is None or token_data.account_type is None:
        raise credentials_exception

    if token_data.account_type == "staff":
        result = await db.execute(select(User).where(User.id == uuid.UUID(token_data.sub)))
        account = result.scalars().first()
    elif token_data.account_type == "guest":
        result = await db.execute(select(Guest).where(Guest.id == uuid.UUID(token_data.sub)))
        account = result.scalars().first()
    else:
        raise credentials_exception

    if not account:
        raise credentials_exception

    return account


async def get_current_user(
        account: Union[User, Guest] = Depends(get_current_account)
) -> User:
    """Dependency to extract and validate the user from the JWT token."""
    if not isinstance(account, User):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return account


async def get_optional_current_user(
        db: AsyncSession = Depends(get_db),
        token: str | None = Depends(optional_oauth2)
) -> User | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if payload is None or payload.get("sub") is None:
        return None
    result = await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))
    return result.scalars().first()


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure the current user's account is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """
    Dependency factory for RBAC (Role-Based Access Control).
    Usage: Depends(require_roles([UserRole.owner, UserRole.restaurant_manager]))
    """

    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user

    return role_checker