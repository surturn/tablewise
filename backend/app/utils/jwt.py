from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from app.config import settings
from app.models.enums import UserRole


def create_access_token(subject: str | Any, role: UserRole, outlet_id: Optional[str] = None, expires_delta: Optional[timedelta] = None, **legacy) -> str:
    if outlet_id is None:
        outlet_id = legacy.get("branch_id")
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "role": role.value, "outlet_id": str(outlet_id) if outlet_id else None}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if "outlet_id" not in payload and "branch_id" in payload:
            payload["outlet_id"] = payload["branch_id"]
        return payload
    except JWTError:
        return None
