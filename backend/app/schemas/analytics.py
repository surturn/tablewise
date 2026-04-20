import uuid
from pydantic import BaseModel

class ForecastRequest(BaseModel):
    branch_id: uuid.UUID
    historical_data_summary: str

class TaskResponse(BaseModel):
    task_id: str
    message: str