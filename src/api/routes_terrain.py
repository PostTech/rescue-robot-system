"""FastAPI router for Terrain Analysis and drive updates."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_application_service
from api.schemas import TerrainAnalyzeRequest
from service.application_service import ApplicationService

router = APIRouter(prefix="/api/terrain", tags=["terrain"])


@router.post("/{mission_id}/analyze", status_code=status.HTTP_200_OK)
def analyze_mission_terrain(
    mission_id: str,
    payload: TerrainAnalyzeRequest,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Process real-time terrain telemetry for a mission and adapt robot locomotion."""
    try:
        t = app.process_terrain(
            mission_id=mission_id,
            slope=payload.slope,
            step_height=payload.step_height,
            roughness=payload.roughness,
            obstacle_density=payload.obstacle_density,
            traversability=payload.traversability,
        )
        return {
            "terrain_class": t.terrain_class.value,
            "slope_degree": t.slope_degree,
            "step_height_cm": t.step_height_cm,
            "roughness_score": t.roughness_score,
            "obstacle_density": t.obstacle_density,
            "traversability_score": t.traversability_score,
            "traversability_level": t.traversability_level.value,
            "traversable": t.traversable,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/{mission_id}/history", status_code=status.HTTP_200_OK)
def get_terrain_history(
    mission_id: str,
    app: ApplicationService = Depends(get_application_service),
) -> list[dict[str, Any]]:
    """Retrieve logged terrain analysis events for a mission."""
    try:
        ctx = app.get_mission_context(mission_id)
        history = []
        for t in ctx.terrain_results:
            history.append(
                {
                    "terrain_class": t.terrain_class.value,
                    "slope_degree": t.slope_degree,
                    "step_height_cm": t.step_height_cm,
                    "roughness_score": t.roughness_score,
                    "obstacle_density": t.obstacle_density,
                    "traversability_score": t.traversability_score,
                    "traversability_level": t.traversability_level.value,
                    "traversable": t.traversable,
                }
            )
        return history
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
