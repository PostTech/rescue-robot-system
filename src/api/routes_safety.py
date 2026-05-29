"""FastAPI router for Safety Manager status and domain Event Logs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status

from api.deps import get_application_service
from service.application_service import ApplicationService

router = APIRouter(tags=["safety"])


@router.get("/api/safety/status", status_code=status.HTTP_200_OK)
def get_safety_status(
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Retrieve the global safety state, alert statuses, and recommendations."""
    # Read the internal safety state from application_service
    s = app._safety.state
    return {
        "level": s.level.name,
        "gas_alert_active": s.gas_alert_active,
        "emergency_stopped": s.emergency_stopped,
        "reason": s.reason,
        "recommended_locomotion": s.recommended_locomotion.value,
        "is_safe_to_operate": app._safety.is_safe_to_operate(),
        "robot_locomotion": app._robot.locomotion_mode.value,
    }


@router.get("/api/events", status_code=status.HTTP_200_OK)
def get_domain_events(
    app: ApplicationService = Depends(get_application_service),
) -> list[dict[str, Any]]:
    """Retrieve the full historical list of published domain events."""
    events = app.get_event_history()
    result = []
    for e in events:
        result.append(
            {
                "event_id": e.event_id,
                "mission_id": e.mission_id,
                "robot_id": e.robot_id,
                "event_type": e.event_type,
                "timestamp_ms": e.timestamp_ms,
                "source_module": e.source_module,
            }
        )
    return result
