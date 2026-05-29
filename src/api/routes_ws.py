"""FastAPI WebSocket endpoint for telemetry broadcasts."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.websocket_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Endpoint accepting telemetry client socket connections."""
    await manager.connect(websocket)
    try:
        # Keep the connection open and process incoming pings
        while True:
            # We don't expect messages from client, but we must listen to detect close events
            data = await websocket.receive_text()
            # Basic keep-alive pong response if client pings
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
