"""Event types — immutable event contracts for the system.

Events are the primary cross-module communication contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventPriority(StrEnum):
    """Priority levels for event processing (highest → lowest)."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class EventType(StrEnum):
    """Enumeration of all system event types."""

    THERMAL_ALIVE = "THERMAL_ALIVE"
    RGB_BODY_PART = "RGB_BODY_PART"
    GAS_HAZARD = "GAS_HAZARD"
    SLAM_FAILURE = "SLAM_FAILURE"
    WEBRTC_DISCONNECTED = "WEBRTC_DISCONNECTED"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    SEARCH_MISSION_CREATED = "SEARCH_MISSION_CREATED"
    SEARCH_AREA_UPDATED = "SEARCH_AREA_UPDATED"
    SEARCH_METHOD_SELECTED = "SEARCH_METHOD_SELECTED"
    MISSION_SETUP_APPLIED = "MISSION_SETUP_APPLIED"
    MISSION_APPROVAL_REQUESTED = "MISSION_APPROVAL_REQUESTED"
    TERRAIN_ANALYZED = "TERRAIN_ANALYZED"
    SEARCH_DRIVE_PROFILE_SELECTED = "SEARCH_DRIVE_PROFILE_SELECTED"


@dataclass(frozen=True)
class BaseEvent:
    """Immutable base event — the system-wide event contract."""

    event_id: str
    mission_id: str
    robot_id: str
    event_type: str
    timestamp_ms: int
    source_module: str
    priority: EventPriority = EventPriority.NORMAL
    payload: dict[str, Any] = field(default_factory=dict)
