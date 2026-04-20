import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class MenuCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class MenuCategoryCreate(MenuCategoryBase):
    """Schema for creating a new menu category."""
    pass

class MenuCategoryResponse(MenuCategoryBase):
    """Schema for returning menu category data."""
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than zero")
    image_url: Optional[str] = None
    is_active: bool = True
    category_id: uuid.UUID

class MenuItemCreate(MenuItemBase):
    """Schema for creating a new menu item."""
    pass

class MenuItemResponse(MenuItemBase):
    """Schema for returning menu item data."""
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)