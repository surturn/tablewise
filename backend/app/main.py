import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, branches, menu, inventory, customers, orders, payments, analytics, rooms, bookings
from app.websocket_manager import order_ws_manager

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT, "project": settings.PROJECT_NAME}


@app.websocket("/ws/orders/{outlet_id}")
async def orders_websocket_root(outlet_id: uuid.UUID, websocket: WebSocket):
    await order_ws_manager.connect(outlet_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        order_ws_manager.disconnect(outlet_id, websocket)


app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
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
