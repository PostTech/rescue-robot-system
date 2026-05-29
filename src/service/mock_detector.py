"""Mock detector implementations.

Provides deterministic mock detectors for thermal, RGB, and audio
that implement the IDetector Protocol without real AI models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DetectionLabel(StrEnum):
    """Detection result labels."""

    VICTIM_ALIVE = "VICTIM_ALIVE"
    VICTIM_BODY_PART = "VICTIM_BODY_PART"
    VICTIM_AUDIO = "VICTIM_AUDIO"
    NO_DETECTION = "NO_DETECTION"


@dataclass(frozen=True)
class DetectionResult:
    """Single detection result from a sensor."""

    sensor_type: str
    label: DetectionLabel
    confidence: float
    bounding_box: tuple[float, float, float, float] | None = None  # x, y, w, h
    timestamp_ms: int = 0


class MockDetector:
    """Mock detector that returns fixed results per IDetector Protocol.

    Args:
        sensor_type: Type of sensor (THERMAL, RGB, AUDIO).
        default_label: Detection label to return.
        default_confidence: Confidence score to return.
    """

    def __init__(
        self,
        sensor_type: str,
        default_label: DetectionLabel = DetectionLabel.NO_DETECTION,
        default_confidence: float = 0.0,
    ) -> None:
        self._sensor_type = sensor_type
        self._label = default_label
        self._confidence = default_confidence

    def detect(self, timestamp_ms: int = 0) -> DetectionResult:
        """Run detection and return a fixed result."""
        bbox = (0.25, 0.25, 0.5, 0.5) if self._label != DetectionLabel.NO_DETECTION else None
        return DetectionResult(
            sensor_type=self._sensor_type,
            label=self._label,
            confidence=self._confidence,
            bounding_box=bbox,
            timestamp_ms=timestamp_ms,
        )

    def set_result(self, label: DetectionLabel, confidence: float) -> None:
        """Update the fixed result for subsequent calls."""
        self._label = label
        self._confidence = confidence
