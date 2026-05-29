"""Client-2: Thermal/RGB + AI Detection (Perception) interface contracts."""

from __future__ import annotations

from typing import Any, Protocol


class IDetector(Protocol):
    """AI detector interface (YOLO, thermal, etc.)."""

    def infer(self, frame: Any) -> Any: ...
