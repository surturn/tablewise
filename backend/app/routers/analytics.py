from fastapi import APIRouter, Depends, status
from app.schemas.analytics import ForecastRequest, TaskResponse
from app.tasks import generate_inventory_forecast
from app.routers.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter()


@router.post("/forecast", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_demand_forecast(
        request: ForecastRequest,
        current_user: User = Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
):
    """
    Trigger an AI-driven inventory demand forecast.
    Because AI generation takes time, this returns a task ID immediately,
    while Claude processes the data in the background via Celery.
    """
    # .delay() is how we send the task to Redis/Celery
    task = generate_inventory_forecast.delay(str(request.branch_id), request.historical_data_summary)

    return {
        "task_id": task.id,
        "message": "AI Forecast generation has been queued successfully."
    }