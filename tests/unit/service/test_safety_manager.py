"""TC-SAFETY-001/002: Safety manager tests."""

from __future__ import annotations

from domain_types.events import BaseEvent, EventType
from domain_types.terrain import LocomotionMode
from service.safety_manager import SafetyLevel, SafetyManager


def _evt(event_type: str, eid: str = "E-1", ts: int = 1000) -> BaseEvent:
    return BaseEvent(
        event_id=eid,
        mission_id="M-001",
        robot_id="R-001",
        event_type=event_type,
        timestamp_ms=ts,
        source_module="test",
    )


class TestSafetyManager:
    def test_tc_safety_001_emergency_stop(self) -> None:
        """TC-SAFETY-001: Emergency stop triggers STOP_AND_REPLAN."""
        mgr = SafetyManager()
        state = mgr.handle_event(_evt(EventType.EMERGENCY_STOP))
        assert state.level == SafetyLevel.EMERGENCY_STOP
        assert state.emergency_stopped is True
        assert state.recommended_locomotion == LocomotionMode.STOP_AND_REPLAN
        assert mgr.is_safe_to_operate() is False

    def test_tc_safety_002_gas_hazard_retreat(self) -> None:
        """TC-SAFETY-002: Gas hazard triggers safe mode."""
        mgr = SafetyManager()
        state = mgr.handle_event(_evt(EventType.GAS_HAZARD))
        assert state.level == SafetyLevel.SAFE_MODE
        assert state.gas_alert_active is True
        assert state.recommended_locomotion == LocomotionMode.STOP_AND_REPLAN
        assert mgr.is_safe_to_operate() is False

    def test_slam_failure_caution(self) -> None:
        mgr = SafetyManager()
        state = mgr.handle_event(_evt(EventType.SLAM_FAILURE))
        assert state.level == SafetyLevel.CAUTION
        assert state.recommended_locomotion == LocomotionMode.SLOW_SAFE
        assert mgr.is_safe_to_operate() is True

    def test_webrtc_disconnect_caution(self) -> None:
        mgr = SafetyManager()
        state = mgr.handle_event(_evt(EventType.WEBRTC_DISCONNECTED))
        assert state.level == SafetyLevel.CAUTION

    def test_emergency_overrides_gas(self) -> None:
        mgr = SafetyManager()
        mgr.handle_event(_evt(EventType.GAS_HAZARD, "G1", 100))
        state = mgr.handle_event(_evt(EventType.EMERGENCY_STOP, "E1", 200))
        assert state.level == SafetyLevel.EMERGENCY_STOP

    def test_gas_does_not_override_emergency(self) -> None:
        mgr = SafetyManager()
        mgr.handle_event(_evt(EventType.EMERGENCY_STOP, "E1", 100))
        state = mgr.handle_event(_evt(EventType.GAS_HAZARD, "G1", 200))
        assert state.level == SafetyLevel.EMERGENCY_STOP
        assert state.emergency_stopped is True

    def test_reset_from_caution(self) -> None:
        mgr = SafetyManager()
        mgr.handle_event(_evt(EventType.SLAM_FAILURE))
        mgr.reset()
        assert mgr.state.level == SafetyLevel.NORMAL

    def test_reset_blocked_after_emergency(self) -> None:
        mgr = SafetyManager()
        mgr.handle_event(_evt(EventType.EMERGENCY_STOP))
        mgr.reset()
        assert mgr.state.level == SafetyLevel.EMERGENCY_STOP

    def test_event_log(self) -> None:
        mgr = SafetyManager()
        mgr.handle_event(_evt(EventType.GAS_HAZARD, "G1"))
        mgr.handle_event(_evt(EventType.EMERGENCY_STOP, "E1"))
        log = mgr.get_event_log()
        assert len(log) == 2
        assert log[0].event_id == "G1"

    def test_normal_state_is_safe(self) -> None:
        mgr = SafetyManager()
        assert mgr.is_safe_to_operate() is True
