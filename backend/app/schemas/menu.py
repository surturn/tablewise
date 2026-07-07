import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MenuCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class MenuCategoryCreate(MenuCategoryBase):
    pass


class MenuCategoryResponse(MenuCategoryBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_kes_cents: int = Field(gt=0, description="KES price in cents")
    image_url: Optional[str] = None
    is_available: bool = True
    category_id: uuid.UUID
    outlet_id: uuid.UUID


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemResponse(MenuItemBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
