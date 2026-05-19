from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.config import settings


class ReorderLine(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=120)
    recommended_quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    confidence_score: float = Field(..., ge=0, le=1)
    reason: str = Field(..., min_length=5, max_length=240)


class InventoryForecast(BaseModel):
    branch_id: str = Field(..., min_length=8)
    horizon_days: int = Field(7, ge=1, le=30)
    currency: Literal["USD"] = "USD"
    recommendations: list[ReorderLine] = Field(default_factory=list, max_length=50)
    data_quality_notes: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("recommendations")
    @classmethod
    def require_confident_recommendations(cls, value: list[ReorderLine]) -> list[ReorderLine]:
        low_confidence = [line.item_name for line in value if line.confidence_score < settings.AI_MIN_CONFIDENCE_SCORE]
        if low_confidence:
            raise ValueError(f"Low-confidence AI recommendations require manager review: {', '.join(low_confidence)}")
        return value


def validate_inventory_forecast(payload: dict) -> InventoryForecast:
    """Validate AI output before it can be emailed or used for reorder workflows."""
    try:
        return InventoryForecast.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"AI forecast failed validation: {exc}") from exc
