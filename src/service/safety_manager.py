"""Safety manager.

Handles emergency stop, gas alerts, and safe mode transitions.
Priority: EMERGENCY_STOP > SAFE_MODE > MISSION
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from domain_types.events import BaseEvent, EventType
from domain_types.terrain import LocomotionMode


class SafetyLevel(IntEnum):
    """Safety levels in priority order (higher = more urgent)."""

    NORMAL = 0
    CAUTION = 1
    SAFE_MODE = 2
    EMERGENCY_STOP = 3


@dataclass
class SafetyState:
    """Current safety system state."""

    level: SafetyLevel = SafetyLevel.NORMAL
    gas_alert_active: bool = False
    emergency_stopped: bool = False
    reason: str = ""
    recommended_locomotion: LocomotionMode = LocomotionMode.WHEEL


class SafetyManager:
    """Manages safety state and produces safety decisions.

    Priority: EMERGENCY_STOP > GAS_ALERT > SAFE_MODE > NORMAL
    """

    def __init__(self) -> None:
        self.state = SafetyState()
        self._event_log: list[BaseEvent] = []

    def handle_event(self, event: BaseEvent) -> SafetyState:
        """Process a safety-relevant event and update state.

        Returns the updated SafetyState.
        """
        self._event_log.append(event)

        if event.event_type == EventType.EMERGENCY_STOP:
            self.state = SafetyState(
                level=SafetyLevel.EMERGENCY_STOP,
                emergency_stopped=True,
                reason=f"Emergency stop: {event.event_id}",
                recommended_locomotion=LocomotionMode.STOP_AND_REPLAN,
            )
        elif event.event_type == EventType.GAS_HAZARD:
            if not self.state.emergency_stopped:
                self.state = SafetyState(
                    level=SafetyLevel.SAFE_MODE,
                    gas_alert_active=True,
                    reason=f"Gas alert: {event.event_id}",
                    recommended_locomotion=LocomotionMode.STOP_AND_REPLAN,
                )
        elif event.event_type == EventType.SLAM_FAILURE:
            if self.state.level < SafetyLevel.SAFE_MODE:
                self.state = SafetyState(
                    level=SafetyLevel.CAUTION,
                    reason=f"SLAM failure: {event.event_id}",
                    recommended_locomotion=LocomotionMode.SLOW_SAFE,
                )
        elif event.event_type == EventType.WEBRTC_DISCONNECTED:
            if self.state.level < SafetyLevel.SAFE_MODE:
                self.state = SafetyState(
                    level=SafetyLevel.CAUTION,
                    reason=f"Network disconnected: {event.event_id}",
                    recommended_locomotion=LocomotionMode.SLOW_SAFE,
                )

        return self.state

    def reset(self) -> None:
        """Reset to normal state (only if not emergency stopped)."""
        if not self.state.emergency_stopped:
            self.state = SafetyState()

    def is_safe_to_operate(self) -> bool:
        """Check if normal operation is allowed."""
        return self.state.level <= SafetyLevel.CAUTION

    def get_event_log(self) -> list[BaseEvent]:
        """Return all processed safety events."""
        return list(self._event_log)
