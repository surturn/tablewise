from typing import Optional
from pydantic import BaseModel
from app.models.enums import UserRole

class Token(BaseModel):
    """Schema for the JWT token response sent to the client."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Schema for validating the decoded JWT payload."""
    sub: Optional[str] = None
    role: Optional[UserRole] = None
    branch_id: Optional[str] = None