from typing import List, cast
from asyncio import Lock
import logging

from fastapi import WebSocket

from project_settings import MAX_CONNECTIONS_TOTAL

logger = logging.getLogger(__name__)


def get_connection_manager(websocket: WebSocket) -> "MultipleConnectionManager":
    return cast(MultipleConnectionManager, websocket.app.state.connection_manager)


class MultipleConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self.lock = Lock()

    async def _send_error_and_close(self, ws: WebSocket, code: int, message: str) -> None:
        try:
            await ws.send_json({"type": "error", "code": code, "message": message})
        except Exception:
            pass
        await ws.close(code=code)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

        async with self.lock:
            if len(self.active_connections) >= MAX_CONNECTIONS_TOTAL:
                error_msg = "Connection limit exceeded"
                logger.error(error_msg)
                await self._send_error_and_close(websocket, code=1013, message=error_msg)
                return

            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
