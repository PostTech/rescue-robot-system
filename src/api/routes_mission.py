"""FastAPI router for Search Mission lifecycle management."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_application_service
from api.schemas import ApproveMissionRequest, MissionRequestModel
from service.application_service import ApplicationService

router = APIRouter(prefix="/api/missions", tags=["missions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_mission(
    payload: MissionRequestModel,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Create a new mission draft from an operator request."""
    try:
        req = payload.to_domain()
        draft = app.create_mission(req)
        return {
            "mission_id": draft.mission_id,
            "validation_status": draft.validation_status,
            "sop_constraints": draft.sop_constraints,
            "draft_snapshot_id": draft.draft_snapshot_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("", status_code=status.HTTP_200_OK)
def get_missions(
    app: ApplicationService = Depends(get_application_service),
) -> list[dict[str, Any]]:
    """List all mission summaries for the dashboard."""
    return cast(list[dict[str, Any]], app.get_mission_summary_list())


@router.get("/{mission_id}", status_code=status.HTTP_200_OK)
def get_mission_details(
    mission_id: str,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Get the complete details of a single mission context."""
    try:
        return cast(dict[str, Any], app.get_mission_details(mission_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{mission_id}/approve", status_code=status.HTTP_200_OK)
def approve_mission(
    mission_id: str,
    payload: ApproveMissionRequest,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Approve a mission draft and lock in a plan."""
    try:
        plan = app.approve_mission(mission_id, payload.approver)
        return {
            "mission_id": plan.mission_id,
            "approved_by": plan.approved_by,
            "approved_at_ms": plan.approved_at_ms,
            "plan_snapshot_id": plan.plan_snapshot_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/{mission_id}/start", status_code=status.HTTP_200_OK)
def start_mission(
    mission_id: str,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Transition approved mission into active execution."""
    try:
        state = app.start_mission(mission_id)
        return {"mission_id": mission_id, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/{mission_id}/complete", status_code=status.HTTP_200_OK)
def complete_mission(
    mission_id: str,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Mark an active mission as completed."""
    try:
        state = app.complete_mission(mission_id)
        return {"mission_id": mission_id, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/{mission_id}/emergency-stop", status_code=status.HTTP_200_OK)
def emergency_stop_mission(
    mission_id: str,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Trigger Low-Level emergency stop and halt the mission."""
    try:
        state = app.emergency_stop(mission_id)
        return {"mission_id": mission_id, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/{mission_id}/tick", status_code=status.HTTP_200_OK)
def tick_mission(
    mission_id: str,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Advance the active mission by one simulation step (Tick)."""
    try:
        return cast(dict[str, Any], app.tick_mission(mission_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# A simple auxiliary router for fetching SOP profile metadata
sop_router = APIRouter(prefix="/api/sop", tags=["sop"])


@sop_router.get("/profiles", status_code=status.HTTP_200_OK)
def get_sop_profiles(
    app: ApplicationService = Depends(get_application_service),
) -> list[dict[str, str]]:
    """Get the active list of predefined SOP profiles."""
    return cast(list[dict[str, str]], app.get_available_sop_profiles())
