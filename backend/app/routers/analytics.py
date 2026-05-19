from fastapi import APIRouter, Depends, status
from app.schemas.analytics import ForecastRequest, TaskResponse
from app.tasks import generate_inventory_forecast
from app.routers.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter()


@router.post("/forecast", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_demand_forecast(request: ForecastRequest, current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.bartender]))):
    outlet_id = current_user.outlet_id if current_user.role not in [UserRole.owner, UserRole.hotel_manager] and current_user.outlet_id else request.branch_id
    task = generate_inventory_forecast.delay(str(outlet_id), request.historical_data_summary)
    return {"task_id": task.id, "message": "GrandPlatform AI forecast generation has been queued successfully."}
