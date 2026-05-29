"""WebSocket connection manager for real-time telemetry streaming."""

from __future__ import annotations

import asyncio

from fastapi import WebSocket


class WebSocketManager:
    """Manages active WebSocket connections and thread-safe broadcasts."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        # Loop reference for thread-safe cross-thread scheduling
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and track a new client connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Discard a closed client connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, event_type: str, data: dict[str, object]) -> None:
        """Broadcast JSON message to all active clients (async)."""
        payload = {"event_type": event_type, "data": data}
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead sockets
        for dead in dead_connections:
            self.disconnect(dead)

    def broadcast_json_sync(self, event_type: str, data: dict[str, object]) -> None:
        """Thread-safe synchronous broadcast wrapper."""
        if not self.active_connections:
            return
        try:
            if self._loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast_json(event_type, data), self._loop)
            else:
                # Fallback if loop is not running yet
                asyncio.run(self.broadcast_json(event_type, data))
        except Exception as e:
            print(f"[WebSocketManager] Broadcast error: {e}")


# Global WebSocket connection manager instance
manager = WebSocketManager()
