"""Terrain analysis and locomotion types for 3-D LiDAR-based navigation.

Defines terrain classification, traversability, locomotion modes,
and the search-drive profile that ties terrain to search-method execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from domain_types.mission import SearchMethod

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TerrainClass(StrEnum):
    """Terrain classification derived from elevation-grid analysis."""

    FLAT_OPEN = "FLAT_OPEN"
    MILD_SLOPE = "MILD_SLOPE"
    STEEP_SLOPE = "STEEP_SLOPE"
    ROUGH_RUBBLE = "ROUGH_RUBBLE"
    NARROW_PASSAGE = "NARROW_PASSAGE"
    OBSTACLE_DENSE = "OBSTACLE_DENSE"
    CLIFF_OR_DROP = "CLIFF_OR_DROP"
    UNKNOWN = "UNKNOWN"


class TraversabilityLevel(StrEnum):
    """Qualitative traversability assessment."""

    PASSABLE = "PASSABLE"
    CAUTION = "CAUTION"
    REPLAN_REQUIRED = "REPLAN_REQUIRED"
    BLOCKED = "BLOCKED"


class LocomotionMode(StrEnum):
    """Robot locomotion modes selected by the drive policy."""

    WHEEL = "WHEEL"
    OBSTACLE_CLIMB = "OBSTACLE_CLIMB"
    SLOW_SAFE = "SLOW_SAFE"
    EDGE_FOLLOW = "EDGE_FOLLOW"
    STOP_AND_REPLAN = "STOP_AND_REPLAN"
    STOP = "STOP"


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TerrainAnalysisResult:
    """Output of 3-D LiDAR terrain analysis."""

    terrain_class: TerrainClass
    slope_degree: float
    step_height_cm: float
    roughness_score: float
    obstacle_density: float
    traversability_score: float
    traversability_level: TraversabilityLevel
    traversable: bool


@dataclass(frozen=True)
class LocomotionDecision:
    """Decision on which locomotion mode and speed to use."""

    target_mode: LocomotionMode
    recommended_speed: float
    reason: str


@dataclass(frozen=True)
class SearchDriveProfile:
    """Combined search-method + terrain-aware drive parameters."""

    search_method: SearchMethod
    locomotion_mode: LocomotionMode
    speed_scale: float
    min_clearance_cm: float
    replan_required: bool
    scan_density: str
    reason: str
