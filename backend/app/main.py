import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.config import settings
from app.rate_limit import limiter
from app.routers import auth, customer_auth, branches, menu, inventory, customers, orders, payments, analytics, rooms, bookings
from app.websocket_manager import order_ws_manager

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", docs_url="/docs", redoc_url="/redoc")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health-check endpoint used by Render to verify the service is alive.
    Performs a lightweight SELECT 1 to prove DB connectivity.
    """
    from app.database import AsyncSessionLocal
    from sqlalchemy import text

    db_status = "healthy"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {exc}"

    payload = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "project": settings.PROJECT_NAME,
    }

    if db_status != "healthy":
        from fastapi.responses import JSONResponse
        return JSONResponse(content=payload, status_code=503)

    return payload





app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(customer_auth.router, prefix=f"{settings.API_V1_STR}/auth/customer", tags=["Customer Authentication"])
app.include_router(branches.router, prefix=f"{settings.API_V1_STR}/outlets", tags=["Outlets"])
app.include_router(branches.router, prefix=f"{settings.API_V1_STR}/branches", tags=["Legacy Branches"])
app.include_router(menu.router, prefix=f"{settings.API_V1_STR}/menu", tags=["Menu"])
app.include_router(inventory.router, prefix=f"{settings.API_V1_STR}/inventory", tags=["Inventory"])
app.include_router(customers.router, prefix=f"{settings.API_V1_STR}/guests", tags=["Guests"])
app.include_router(customers.router, prefix=f"{settings.API_V1_STR}/customers", tags=["Legacy Customers"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["Orders"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["Payments"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics & AI"])
app.include_router(rooms.router, prefix=f"{settings.API_V1_STR}", tags=["Rooms"])
app.include_router(bookings.router, prefix=f"{settings.API_V1_STR}/bookings", tags=["Bookings"])
