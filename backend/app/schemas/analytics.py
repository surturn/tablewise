import uuid
from pydantic import BaseModel, Field

class ForecastRequest(BaseModel):
    branch_id: uuid.UUID
    historical_data_summary: str = Field(..., max_length=20000)

class TaskResponse(BaseModel):
    task_id: str
    message: str