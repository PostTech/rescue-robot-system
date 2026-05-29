"""Terrain status ViewModel.

Presents terrain analysis and drive profile status to the operator.
No direct DB, ROS, Robot SDK, or Storage access.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from domain_types.terrain import (
    LocomotionMode,
    SearchDriveProfile,
    TerrainAnalysisResult,
    TerrainClass,
    TraversabilityLevel,
)


@dataclass
class TerrainStatusState:
    """Observable state for terrain status display."""

    terrain_class: TerrainClass | None = None
    traversability_level: TraversabilityLevel | None = None
    traversable: bool = True
    slope_degree: float = 0.0
    locomotion_mode: LocomotionMode | None = None
    speed_scale: float = 1.0
    replan_required: bool = False
    warnings: list[str] = field(default_factory=list)


class TerrainStatusViewModel:
    """ViewModel for terrain status display.

    Receives terrain analysis results from the service layer
    and formats them for UI display.
    """

    def __init__(self) -> None:
        self.state = TerrainStatusState()

    def update_terrain(self, result: TerrainAnalysisResult) -> None:
        """Update state from a new terrain analysis result."""
        self.state.terrain_class = result.terrain_class
        self.state.traversability_level = result.traversability_level
        self.state.traversable = result.traversable
        self.state.slope_degree = result.slope_degree

        warnings: list[str] = []
        if result.traversability_level == TraversabilityLevel.BLOCKED:
            warnings.append("BLOCKED: replan required")
        if result.traversability_level == TraversabilityLevel.REPLAN_REQUIRED:
            warnings.append("CAUTION: replan may be needed")
        if result.terrain_class == TerrainClass.CLIFF_OR_DROP:
            warnings.append("DANGER: cliff detected")
        self.state.warnings = warnings

    def update_drive_profile(self, profile: SearchDriveProfile) -> None:
        """Update state from a new drive profile decision."""
        self.state.locomotion_mode = profile.locomotion_mode
        self.state.speed_scale = profile.speed_scale
        self.state.replan_required = profile.replan_required

    def is_safe(self) -> bool:
        """Check if current terrain is considered safe."""
        return self.state.traversable and not self.state.replan_required
