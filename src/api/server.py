"""FastAPI Server initialization, CORS middleware setup, and router integration."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import bindings for reactive event broadcasting
from api.deps import get_application_service
from api.routes_demo import router as demo_router

# Import routes
from api.routes_detection import router as detection_router
from api.routes_mission import router as mission_router
from api.routes_mission import sop_router
from api.routes_safety import router as safety_router
from api.routes_terrain import router as terrain_router
from api.routes_ws import router as ws_router
from api.websocket_manager import manager
from domain_types.events import BaseEvent

# Create app
app = FastAPI(
    title="Rescue Robot System REST API",
    description="REST API mapping structural domain models and simulation interfaces for rescue missions.",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dynamic development flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(mission_router)
app.include_router(sop_router)
app.include_router(terrain_router)
app.include_router(detection_router)
app.include_router(safety_router)
app.include_router(ws_router)  # Register WebSocket router
app.include_router(demo_router)  # Register Demo router


@app.get("/api/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "GREEN",
        "message": "Rescue Robot System API is online.",
        "version": "1.0.0",
    }


# Mount the Web Frontend static directory to serve index.html on "/"
app.mount("/", StaticFiles(directory="src/web", html=True), name="web")


# ── Reactive Event Bus → WebSocket Broadcaster Linkage ──────────────────────

app_service = get_application_service()


def on_domain_event(event: BaseEvent) -> None:
    """Synchronously captures EventBus changes and pipes them to all WebSockets."""
    payload = {
        "event_id": event.event_id,
        "mission_id": event.mission_id,
        "robot_id": event.robot_id,
        "event_type": event.event_type,
        "timestamp_ms": event.timestamp_ms,
        "source_module": event.source_module,
    }
    manager.broadcast_json_sync("event.published", payload)


# Setup global subscription to domain EventBus
app_service.event_bus.subscribe_all(on_domain_event)
