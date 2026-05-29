"""Mock SLAM engine.

Implements ISlamEngine Protocol with deterministic fixed outputs.
No ROS/rclpy dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain_types.common import Pose3D


@dataclass(frozen=True)
class SlamMapUpdate:
    """Incremental map update from SLAM."""

    frame_id: str
    timestamp_ms: int
    cells_updated: int
    map_coverage_ratio: float


class MockSlamEngine:
    """Mock SLAM engine returning fixed pose and map updates.

    Simulates ISlamEngine Protocol for Windows testing.
    """

    def __init__(
        self,
        initial_pose: Pose3D | None = None,
        map_coverage: float = 0.0,
    ) -> None:
        self._pose = initial_pose or Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self._map_coverage = map_coverage
        self._is_active = True
        self._failure_injected = False
        self._update_count = 0

    @property
    def is_active(self) -> bool:
        return self._is_active and not self._failure_injected

    def get_pose(self) -> Pose3D:
        """Return current estimated pose.

        Raises:
            RuntimeError: If SLAM has failed.
        """
        if self._failure_injected:
            raise RuntimeError("SLAM failure: localization lost")
        return self._pose

    def update(self, timestamp_ms: int) -> SlamMapUpdate:
        """Simulate a map update step.

        Raises:
            RuntimeError: If SLAM has failed.
        """
        if self._failure_injected:
            raise RuntimeError("SLAM failure: cannot update map")
        self._update_count += 1
        self._map_coverage = min(1.0, self._map_coverage + 0.05)
        return SlamMapUpdate(
            frame_id="map",
            timestamp_ms=timestamp_ms,
            cells_updated=self._update_count * 10,
            map_coverage_ratio=self._map_coverage,
        )

    def set_pose(self, pose: Pose3D) -> None:
        """Override the current pose (for test setup)."""
        self._pose = pose

    def inject_failure(self) -> None:
        """Inject a SLAM failure for testing."""
        self._failure_injected = True

    def recover(self) -> None:
        """Recover from injected failure."""
        self._failure_injected = False

    def reset(self) -> None:
        """Full reset to initial state."""
        self._pose = Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self._map_coverage = 0.0
        self._is_active = True
        self._failure_injected = False
        self._update_count = 0
