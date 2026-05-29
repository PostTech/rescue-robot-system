"""TC-CTRL-001/002: Mock robot controller tests."""

from __future__ import annotations

from domain_types.terrain import LocomotionMode
from service.mock_robot_controller import MockRobotController, RobotCommand


class TestMockRobotController:
    def test_tc_ctrl_001_receive_commands(self) -> None:
        """TC-CTRL-001: Robot controller receives commands."""
        ctrl = MockRobotController()
        result = ctrl.execute(RobotCommand.MOVE_FORWARD, timestamp_ms=1000)
        assert result.success is True
        assert result.command == RobotCommand.MOVE_FORWARD
        assert len(ctrl.get_command_history()) == 1

    def test_tc_ctrl_002_emergency_stop_overrides(self) -> None:
        """TC-CTRL-002: Emergency stop overrides all commands."""
        ctrl = MockRobotController()
        ctrl.execute(RobotCommand.MOVE_FORWARD, 100)
        result = ctrl.execute(RobotCommand.EMERGENCY_STOP, 200)
        assert result.success is True
        assert ctrl.is_emergency_stopped is True
        assert ctrl.locomotion_mode == LocomotionMode.STOP_AND_REPLAN

        # Subsequent commands are rejected
        result2 = ctrl.execute(RobotCommand.MOVE_FORWARD, 300)
        assert result2.success is False
        assert "emergency stopped" in result2.error.lower()

    def test_stop_command(self) -> None:
        ctrl = MockRobotController()
        result = ctrl.execute(RobotCommand.STOP)
        assert result.success is True
        assert ctrl.locomotion_mode == LocomotionMode.STOP_AND_REPLAN

    def test_set_locomotion(self) -> None:
        ctrl = MockRobotController()
        result = ctrl.set_locomotion(LocomotionMode.OBSTACLE_CLIMB, 1000)
        assert result.success is True
        assert ctrl.locomotion_mode == LocomotionMode.OBSTACLE_CLIMB

    def test_set_locomotion_blocked_after_emergency(self) -> None:
        ctrl = MockRobotController()
        ctrl.execute(RobotCommand.EMERGENCY_STOP)
        result = ctrl.set_locomotion(LocomotionMode.WHEEL)
        assert result.success is False

    def test_command_history(self) -> None:
        ctrl = MockRobotController()
        ctrl.execute(RobotCommand.MOVE_FORWARD, 100)
        ctrl.execute(RobotCommand.TURN_LEFT, 200)
        ctrl.execute(RobotCommand.STOP, 300)
        history = ctrl.get_command_history()
        assert len(history) == 3
        assert history[0].command == RobotCommand.MOVE_FORWARD
        assert history[2].command == RobotCommand.STOP

    def test_reset(self) -> None:
        ctrl = MockRobotController()
        ctrl.execute(RobotCommand.EMERGENCY_STOP)
        ctrl.reset()
        assert ctrl.is_emergency_stopped is False
        assert ctrl.locomotion_mode == LocomotionMode.WHEEL
        assert len(ctrl.get_command_history()) == 0

    def test_deterministic(self) -> None:
        c1 = MockRobotController()
        c2 = MockRobotController()
        r1 = c1.execute(RobotCommand.MOVE_FORWARD, 1000)
        r2 = c2.execute(RobotCommand.MOVE_FORWARD, 1000)
        assert r1 == r2
