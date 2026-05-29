"""Mission domain types ??search areas, methods, drafts, plans, and SOP recommendations.

Covers the full mission-creation lifecycle from request through approved plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from domain_types.common import Pose3D

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SearchAreaType(StrEnum):
    """Supported search-area geometry types."""

    POLYGON = "POLYGON"
    WAYPOINT_ROUTE = "WAYPOINT_ROUTE"
    GRID = "GRID"
    GEOFENCE = "GEOFENCE"


class SearchMethod(StrEnum):
    """SAR / robot-exploration search patterns (IAMSAR + Land SAR + frontier)."""

    AREA_SWEEP = "AREA_SWEEP"
    PARALLEL_SWEEP = "PARALLEL_SWEEP"
    CREEPING_LINE = "CREEPING_LINE"
    EXPANDING_SQUARE = "EXPANDING_SQUARE"
    SECTOR_SEARCH = "SECTOR_SEARCH"
    TRACKLINE_SEARCH = "TRACKLINE_SEARCH"
    CONTOUR_SEARCH = "CONTOUR_SEARCH"
    TRACK_SWEEP = "TRACK_SWEEP"
    SINGLE_FILE = "SINGLE_FILE"
    GRID_COVERAGE = "GRID_COVERAGE"
    FRONTIER_EXPLORATION = "FRONTIER_EXPLORATION"
    WAYPOINT_ROUTE = "WAYPOINT_ROUTE"
    SPIRAL_SEARCH = "SPIRAL_SEARCH"
    PERIMETER_SEARCH = "PERIMETER_SEARCH"
    MANUAL_ASSISTED = "MANUAL_ASSISTED"


class MissionStatus(StrEnum):
    """Lifecycle states for a search mission."""

    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SearchArea:
    """Geometric definition of a search region."""

    area_type: SearchAreaType
    coordinates: tuple[Pose3D, ...]
    frame_id: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchMissionRequest:
    """Operator-submitted request to create a new search mission."""

    request_id: str
    operator_id: str
    mission_name: str
    search_area: SearchArea
    search_method: SearchMethod
    sop_profile_id: str
    priority: str
    created_at_ms: int


@dataclass(frozen=True)
class MissionDraft:
    """Unconfirmed mission draft awaiting validation and approval."""

    mission_id: str
    request: SearchMissionRequest
    validation_status: str
    sop_constraints: dict[str, object] = field(default_factory=dict)
    draft_snapshot_id: str = ""


@dataclass(frozen=True)
class SearchMissionPlan:
    """Approved, frozen mission plan ready for execution."""

    mission_id: str
    search_area: SearchArea
    search_method: SearchMethod
    approved_by: str
    approved_at_ms: int
    plan_snapshot_id: str


@dataclass(frozen=True)
class MissionSetupRecommendation:
    """SOP-generated recommendation (never directly executes a mission)."""

    recommended_method: SearchMethod
    constraints: dict[str, object] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    recommendation_only: bool = True


# ---------------------------------------------------------------------------
# Control Command Types
# ---------------------------------------------------------------------------


class ControlCommandType(StrEnum):
    """Supported control command types."""

    MOVE = "MOVE"
    STOP = "STOP"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    SET_MODE = "SET_MODE"


@dataclass(frozen=True)
class ControlCommand:
    """Remote control command routed from operator to robot controller."""

    command_id: str
    mission_id: str
    robot_id: str
    command_type: ControlCommandType
    issued_by: str
    timestamp_ms: int
    payload: dict[str, Any]
