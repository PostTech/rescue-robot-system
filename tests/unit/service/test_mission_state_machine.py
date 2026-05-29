"""TC-STATE-001/002/003: Mission state machine tests."""

from __future__ import annotations

import pytest

from service.mission_state_machine import MissionState, MissionStateMachine


class TestMissionStateMachine:
    def test_tc_state_001_valid_transitions(self) -> None:
        """TC-STATE-001: Valid state transitions through full lifecycle."""
        sm = MissionStateMachine()
        assert sm.state == MissionState.DRAFT

        sm.transition(MissionState.PENDING_APPROVAL)
        assert sm.state == MissionState.PENDING_APPROVAL

        sm.transition(MissionState.APPROVED)
        assert sm.state == MissionState.APPROVED

        sm.transition(MissionState.ACTIVE)
        assert sm.state == MissionState.ACTIVE

        sm.transition(MissionState.COMPLETED)
        assert sm.state == MissionState.COMPLETED
        assert sm.is_terminal is True

    def test_tc_state_002_forbidden_transition_rejected(self) -> None:
        """TC-STATE-002: Forbidden transition raises ValueError."""
        sm = MissionStateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(MissionState.ACTIVE)  # DRAFT -> ACTIVE not allowed

    def test_tc_state_003_emergency_stop_overrides(self) -> None:
        """TC-STATE-003: Emergency stop overrides any non-terminal state."""
        for initial in [
            MissionState.DRAFT,
            MissionState.PENDING_APPROVAL,
            MissionState.APPROVED,
            MissionState.ACTIVE,
            MissionState.PAUSED,
        ]:
            sm = MissionStateMachine(initial)
            sm.emergency_stop()
            assert sm.state == MissionState.EMERGENCY_STOPPED

    def test_emergency_stop_from_terminal_raises(self) -> None:
        sm = MissionStateMachine(MissionState.COMPLETED)
        with pytest.raises(ValueError):
            sm.emergency_stop()

    def test_reject_path(self) -> None:
        sm = MissionStateMachine()
        sm.transition(MissionState.PENDING_APPROVAL)
        sm.transition(MissionState.REJECTED)
        assert sm.is_terminal is True
        with pytest.raises(ValueError):
            sm.transition(MissionState.APPROVED)

    def test_pause_resume(self) -> None:
        sm = MissionStateMachine(MissionState.ACTIVE)
        sm.transition(MissionState.PAUSED)
        assert sm.state == MissionState.PAUSED
        sm.transition(MissionState.ACTIVE)
        assert sm.state == MissionState.ACTIVE

    def test_abort_from_active(self) -> None:
        sm = MissionStateMachine(MissionState.ACTIVE)
        sm.transition(MissionState.ABORTED)
        assert sm.is_terminal is True

    def test_abort_from_paused(self) -> None:
        sm = MissionStateMachine(MissionState.PAUSED)
        sm.transition(MissionState.ABORTED)
        assert sm.is_terminal is True

    def test_history_tracking(self) -> None:
        sm = MissionStateMachine()
        sm.transition(MissionState.PENDING_APPROVAL)
        sm.transition(MissionState.APPROVED)
        assert sm.history == [
            (MissionState.DRAFT, MissionState.PENDING_APPROVAL),
            (MissionState.PENDING_APPROVAL, MissionState.APPROVED),
        ]

    def test_can_transition_check(self) -> None:
        sm = MissionStateMachine()
        assert sm.can_transition(MissionState.PENDING_APPROVAL) is True
        assert sm.can_transition(MissionState.COMPLETED) is False
        assert sm.can_transition(MissionState.EMERGENCY_STOPPED) is True
