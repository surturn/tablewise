from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from app.config import settings
from app.models.enums import UserRole

def create_access_token(
    subject: str | Any, 
    role: UserRole, 
    branch_id: Optional[str] = None, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a JWT access token containing the user's ID, role, and branch_id.
    This enables fast RBAC and branch-scoped verification without hitting the DB.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role.value,
        "branch_id": str(branch_id) if branch_id else None
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes the JWT token. Returns the payload dictionary if valid, None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None