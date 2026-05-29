"""Common value objects shared across the domain.

Contains timestamp wrapper, spatial pose, priority enum, and communication status.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

TimestampMs = NewType("TimestampMs", int)


@dataclass(frozen=True)
class Pose3D:
    """Six-degree-of-freedom pose in 3-D space."""

    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float


class Priority(StrEnum):
    """Domain-wide priority levels (highest → lowest)."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


@dataclass(frozen=True)
class CommunicationStatus:
    """Snapshot of communication link health."""

    webrtc_connected: bool
    fiveg_connected: bool
    packet_loss_rate: float
