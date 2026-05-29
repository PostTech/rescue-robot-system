"""Multi-sensor fusion logic.

Combines detection results from multiple sensors with priority:
    THERMAL > RGB > AUDIO

Produces a single VictimDecision.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from service.mock_detector import DetectionLabel, DetectionResult

# Sensor priority (lower index = higher priority)
SENSOR_PRIORITY = ("THERMAL", "RGB", "AUDIO")


class DecisionLevel(StrEnum):
    """Fusion decision confidence levels."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


@dataclass(frozen=True)
class VictimDecision:
    """Final fused decision about victim presence."""

    detected: bool
    primary_sensor: str
    label: DetectionLabel
    confidence: float
    decision_level: DecisionLevel
    contributing_results: tuple[DetectionResult, ...]


def fuse_detections(
    results: list[DetectionResult],
    confidence_threshold: float = 0.5,
) -> VictimDecision:
    """Fuse multiple detection results into a single victim decision.

    Rules:
        1. Filter results above confidence_threshold
        2. Sort by sensor priority (THERMAL > RGB > AUDIO)
        3. Primary result is the highest-priority above-threshold detection
        4. If no result above threshold, return no detection
    """
    # Filter above threshold with actual detection
    valid = [
        r
        for r in results
        if r.confidence >= confidence_threshold and r.label != DetectionLabel.NO_DETECTION
    ]

    if not valid:
        return VictimDecision(
            detected=False,
            primary_sensor="",
            label=DetectionLabel.NO_DETECTION,
            confidence=0.0,
            decision_level=DecisionLevel.NONE,
            contributing_results=tuple(results),
        )

    # Sort by priority
    priority_map = {s: i for i, s in enumerate(SENSOR_PRIORITY)}
    valid.sort(key=lambda r: priority_map.get(r.sensor_type, 99))

    primary = valid[0]

    # Determine decision level
    if primary.confidence >= 0.9:
        level = DecisionLevel.HIGH
    elif primary.confidence >= 0.7:
        level = DecisionLevel.MEDIUM
    else:
        level = DecisionLevel.LOW

    return VictimDecision(
        detected=True,
        primary_sensor=primary.sensor_type,
        label=primary.label,
        confidence=primary.confidence,
        decision_level=level,
        contributing_results=tuple(results),
    )
