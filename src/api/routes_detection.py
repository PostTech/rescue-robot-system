"""FastAPI router for Multi-Sensor Fusion victim detections."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_application_service
from api.schemas import DetectionAnalyzeRequest
from service.application_service import ApplicationService
from service.mock_detector import DetectionLabel, DetectionResult

router = APIRouter(prefix="/api/detection", tags=["detection"])


@router.post("/{mission_id}/analyze", status_code=status.HTTP_200_OK)
def analyze_mission_detections(
    mission_id: str,
    payload: DetectionAnalyzeRequest,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, Any]:
    """Fuse a set of multi-sensor detections and produce a single decision."""
    try:
        results = []
        for r in payload.results:
            # Map string to DetectionLabel Enum
            label_val = DetectionLabel.NO_DETECTION
            for enum_val in DetectionLabel:
                if enum_val.value == r.label:
                    label_val = enum_val
                    break

            results.append(
                DetectionResult(
                    sensor_type=r.sensor_type,
                    label=label_val,
                    confidence=r.confidence,
                    bounding_box=r.bounding_box,
                    timestamp_ms=r.timestamp_ms,
                )
            )

        decision = app.process_detections(
            mission_id=mission_id,
            results=results,
            confidence_threshold=payload.confidence_threshold,
        )

        return {
            "detected": decision.detected,
            "primary_sensor": decision.primary_sensor,
            "label": decision.label,
            "confidence": decision.confidence,
            "decision_level": decision.decision_level.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
