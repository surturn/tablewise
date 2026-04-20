from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pydantic

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.enums import UserRole
from app.utils.jwt import decode_access_token
from app.schemas.token import TokenPayload

# OAuth2 scheme configures Swagger UI to send tokens automatically
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(reusable_oauth2)
) -> User:
    """Dependency to extract and validate the user from the JWT token."""
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

    if token_data.sub is None:
        raise credentials_exception

    # Query the user from the DB to ensure they still exist
    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()

    if not user:
        raise credentials_exception

    return user


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
    Usage: Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
    """

    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user

    return role_checker