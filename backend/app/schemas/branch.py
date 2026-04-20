import uuid
from pydantic import BaseModel, ConfigDict

class BranchBase(BaseModel):
    name: str
    location: str
    contact_number: str
    is_active: bool = True
    opening_time: str = "08:00"
    closing_time: str = "22:00"

class BranchCreate(BranchBase):
    """Schema for creating a new branch."""
    pass

class BranchResponse(BranchBase):
    """Schema for returning branch data (includes generated ID)."""
    id: uuid.UUID

    # Pydantic v2 syntax to allow reading from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)