import uuid
from collections import defaultdict
from fastapi import WebSocket


class OrderWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)
        # IP connection limiting
        self._ip_connections: dict[str, int] = defaultdict(int)

    def check_ip_limit(self, client_ip: str, limit: int = 10) -> bool:
        """Returns True if the IP is allowed to connect, False if over limit."""
        return self._ip_connections.get(client_ip, 0) < limit

    def connect(self, outlet_id: uuid.UUID, websocket: WebSocket, client_ip: str) -> None:
        # Note: websocket.accept() is NOT called here. It will be called in the route if auth passes.
        self._connections[outlet_id].add(websocket)
        self._ip_connections[client_ip] += 1

    def disconnect(self, outlet_id: uuid.UUID, websocket: WebSocket, client_ip: str) -> None:
        self._connections[outlet_id].discard(websocket)
        if not self._connections[outlet_id]:
            del self._connections[outlet_id]
            
        if self._ip_connections[client_ip] > 0:
            self._ip_connections[client_ip] -= 1
        if self._ip_connections[client_ip] == 0:
            del self._ip_connections[client_ip]

    async def broadcast_order_update(self, outlet_id: uuid.UUID, payload: dict) -> None:
        dead: list[WebSocket] = []
        for websocket in list(self._connections.get(outlet_id, set())):
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                dead.append(websocket)
        for websocket in dead:
            client_ip = websocket.client.host if websocket.client else "unknown"
            self.disconnect(outlet_id, websocket, client_ip)


order_ws_manager = OrderWebSocketManager()
