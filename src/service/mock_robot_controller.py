"""Mock robot controller.

Implements IRobotController Protocol with command tracking.
No ROS/rclpy dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from domain_types.terrain import LocomotionMode


class RobotCommand(StrEnum):
    """Robot control commands."""

    MOVE_FORWARD = "MOVE_FORWARD"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"
    STOP = "STOP"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    SET_LOCOMOTION = "SET_LOCOMOTION"


@dataclass(frozen=True)
class CommandResult:
    """Result of executing a robot command."""

    command: RobotCommand
    success: bool
    locomotion_mode: LocomotionMode
    timestamp_ms: int
    error: str = ""


class MockRobotController:
    """Mock robot controller that tracks commands.

    Simulates IRobotController Protocol for Windows testing.
    Emergency stop overrides all other commands.
    """

    def __init__(self) -> None:
        self._locomotion_mode = LocomotionMode.WHEEL
        self._emergency_stopped = False
        self._command_history: list[CommandResult] = []

    @property
    def locomotion_mode(self) -> LocomotionMode:
        return self._locomotion_mode

    @property
    def is_emergency_stopped(self) -> bool:
        return self._emergency_stopped

    def execute(self, command: RobotCommand, timestamp_ms: int = 0) -> CommandResult:
        """Execute a robot command.

        Emergency stop is always accepted. Other commands are rejected
        if emergency stopped.
        """
        if command == RobotCommand.EMERGENCY_STOP:
            self._emergency_stopped = True
            self._locomotion_mode = LocomotionMode.STOP_AND_REPLAN
            result = CommandResult(command, True, self._locomotion_mode, timestamp_ms)
            self._command_history.append(result)
            return result

        if self._emergency_stopped:
            result = CommandResult(
                command,
                False,
                self._locomotion_mode,
                timestamp_ms,
                error="Robot is emergency stopped",
            )
            self._command_history.append(result)
            return result

        if command == RobotCommand.STOP:
            self._locomotion_mode = LocomotionMode.STOP_AND_REPLAN

        result = CommandResult(command, True, self._locomotion_mode, timestamp_ms)
        self._command_history.append(result)
        return result

    def set_locomotion(self, mode: LocomotionMode, timestamp_ms: int = 0) -> CommandResult:
        """Change locomotion mode."""
        if self._emergency_stopped:
            result = CommandResult(
                RobotCommand.SET_LOCOMOTION,
                False,
                self._locomotion_mode,
                timestamp_ms,
                error="Robot is emergency stopped",
            )
            self._command_history.append(result)
            return result

        self._locomotion_mode = mode
        result = CommandResult(RobotCommand.SET_LOCOMOTION, True, mode, timestamp_ms)
        self._command_history.append(result)
        return result

    def get_command_history(self) -> list[CommandResult]:
        """Return all executed commands."""
        return list(self._command_history)

    def reset(self) -> None:
        """Reset controller to initial state."""
        self._locomotion_mode = LocomotionMode.WHEEL
        self._emergency_stopped = False
        self._command_history.clear()
