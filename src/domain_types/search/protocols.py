"""Client-3: SLAM + Navigation + Robot Control interface contracts."""

from __future__ import annotations

from typing import Any, Protocol

from domain_types.common import Pose3D
from domain_types.mission import SearchMethod
from domain_types.terrain import (
    LocomotionMode,
    SearchDriveProfile,
    TerrainAnalysisResult,
)


class ISlamEngine(Protocol):
    """SLAM localisation engine."""

    def get_pose(self) -> Pose3D: ...

    def get_map(self) -> Any: ...


class ITerrainAnalyzer(Protocol):
    """3-D LiDAR terrain analysis."""

    def analyze(self, point_cloud: Any) -> TerrainAnalysisResult: ...


class ISearchDrivePolicy(Protocol):
    """Selects drive profile based on terrain + search method."""

    def decide(
        self, terrain: TerrainAnalysisResult, method: SearchMethod
    ) -> SearchDriveProfile: ...


class INavigationEngine(Protocol):
    """Path-planning engine."""

    def plan_path(self, target: Pose3D) -> Any: ...


class IRobotController(Protocol):
    """Low-level robot motion control."""

    def move(self, mode: LocomotionMode, speed: float) -> None: ...

    def stop(self) -> None: ...
