import uuid
from collections import defaultdict
from fastapi import WebSocket


class OrderWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, outlet_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[outlet_id].add(websocket)

    def disconnect(self, outlet_id: uuid.UUID, websocket: WebSocket) -> None:
        self._connections[outlet_id].discard(websocket)
        if not self._connections[outlet_id]:
            del self._connections[outlet_id]

    async def broadcast_order_update(self, outlet_id: uuid.UUID, payload: dict) -> None:
        dead: list[WebSocket] = []
        for websocket in list(self._connections.get(outlet_id, set())):
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(outlet_id, websocket)


order_ws_manager = OrderWebSocketManager()
