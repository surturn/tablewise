from math import ceil
from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=200)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    pages: int


def paginate_response(items: list[T], total: int, page: int, limit: int) -> PaginatedResponse[T]:
    return PaginatedResponse(items=items, total=total, page=page, pages=ceil(total / limit) if total else 0)
