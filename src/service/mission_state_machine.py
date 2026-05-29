"""Mission lifecycle state machine.

Valid transitions:
    DRAFT -> PENDING_APPROVAL
    PENDING_APPROVAL -> APPROVED | REJECTED
    APPROVED -> ACTIVE
    ACTIVE -> COMPLETED | ABORTED | PAUSED
    PAUSED -> ACTIVE | ABORTED
    * (any) -> EMERGENCY_STOPPED  (emergency override)
"""

from __future__ import annotations

from enum import StrEnum


class MissionState(StrEnum):
    """Mission lifecycle states."""

    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"


# Valid transitions: source -> set of allowed targets
_TRANSITIONS: dict[MissionState, set[MissionState]] = {
    MissionState.DRAFT: {MissionState.PENDING_APPROVAL},
    MissionState.PENDING_APPROVAL: {MissionState.APPROVED, MissionState.REJECTED},
    MissionState.APPROVED: {MissionState.ACTIVE},
    MissionState.ACTIVE: {MissionState.COMPLETED, MissionState.ABORTED, MissionState.PAUSED},
    MissionState.PAUSED: {MissionState.ACTIVE, MissionState.ABORTED},
    MissionState.REJECTED: set(),
    MissionState.COMPLETED: set(),
    MissionState.ABORTED: set(),
    MissionState.EMERGENCY_STOPPED: set(),
}

# Terminal states — no further transitions allowed (except emergency already handled)
_TERMINAL = {
    MissionState.COMPLETED,
    MissionState.ABORTED,
    MissionState.REJECTED,
    MissionState.EMERGENCY_STOPPED,
}


class MissionStateMachine:
    """Manages mission state transitions with validation.

    Emergency stop can override any non-terminal state.
    """

    def __init__(self, initial: MissionState = MissionState.DRAFT) -> None:
        self._state = initial
        self._history: list[tuple[MissionState, MissionState]] = []

    @property
    def state(self) -> MissionState:
        return self._state

    @property
    def history(self) -> list[tuple[MissionState, MissionState]]:
        return list(self._history)

    @property
    def is_terminal(self) -> bool:
        return self._state in _TERMINAL

    def can_transition(self, target: MissionState) -> bool:
        """Check if transition to target state is allowed."""
        if target == MissionState.EMERGENCY_STOPPED:
            return self._state not in _TERMINAL
        return target in _TRANSITIONS.get(self._state, set())

    def transition(self, target: MissionState) -> MissionState:
        """Execute a state transition.

        Args:
            target: The desired next state.

        Returns:
            The new state after transition.

        Raises:
            ValueError: If the transition is not allowed.
        """
        if not self.can_transition(target):
            raise ValueError(f"Invalid transition: {self._state} -> {target}")
        prev = self._state
        self._state = target
        self._history.append((prev, target))
        return self._state

    def emergency_stop(self) -> MissionState:
        """Force transition to EMERGENCY_STOPPED from any non-terminal state.

        Raises:
            ValueError: If already in a terminal state.
        """
        return self.transition(MissionState.EMERGENCY_STOPPED)
