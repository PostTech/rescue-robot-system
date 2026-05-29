"""Unit tests for RemoteControlService verifying command routing and event buffering."""

from __future__ import annotations

from domain_types.events import BaseEvent
from domain_types.mission import ControlCommand, ControlCommandType
from domain_types.terrain import LocomotionMode
from service.remote_control_service import RemoteControlService


class SpyRobotController:
    """Spy implementation of the IRobotController protocol to verify routed commands."""

    def __init__(self) -> None:
        self.move_calls: list[tuple[LocomotionMode, float]] = []
        self.stop_called = False

    def move(self, mode: LocomotionMode, speed: float) -> None:
        """Tracks low-level motion commands."""
        self.move_calls.append((mode, speed))

    def stop(self) -> None:
        """Tracks stop triggers."""
        self.stop_called = True


class TestRemoteControlService:
    def test_tc_webrtc_003_control_command_roundtrip(self) -> None:
        """TC-WEBRTC-003: Verify end-to-end command routing to the robot controller."""
        robot_spy = SpyRobotController()
        service = RemoteControlService(robot_spy)

        # 1. Test MOVE command routing
        move_command = ControlCommand(
            command_id="CMD-001",
            mission_id="MSN-001",
            robot_id="RBT-001",
            command_type=ControlCommandType.MOVE,
            issued_by="OP-001",
            timestamp_ms=1000,
            payload={"mode": "OBSTACLE_CLIMB", "speed": 1.5},
        )
        assert service.receive_remote_command(move_command) is True
        assert len(robot_spy.move_calls) == 1
        assert robot_spy.move_calls[0] == (LocomotionMode.OBSTACLE_CLIMB, 1.5)

        # 2. Test STOP command routing
        stop_command = ControlCommand(
            command_id="CMD-002",
            mission_id="MSN-001",
            robot_id="RBT-001",
            command_type=ControlCommandType.STOP,
            issued_by="OP-001",
            timestamp_ms=2000,
            payload={},
        )
        assert service.receive_remote_command(stop_command) is True
        assert robot_spy.stop_called is True

        # 3. Test EMERGENCY_STOP routing
        robot_spy.stop_called = False
        estop_command = ControlCommand(
            command_id="CMD-003",
            mission_id="MSN-001",
            robot_id="RBT-001",
            command_type=ControlCommandType.EMERGENCY_STOP,
            issued_by="OP-001",
            timestamp_ms=3000,
            payload={},
        )
        assert service.receive_remote_command(estop_command) is True
        assert robot_spy.stop_called is True

        # 4. Command rejection when offline
        service.disconnect()
        assert service.receive_remote_command(move_command) is False

    def test_tc_webrtc_004_disconnection_queues_events(self) -> None:
        """TC-WEBRTC-004: Loss of link forces system events into internal failover buffer."""
        robot_spy = SpyRobotController()
        service = RemoteControlService(robot_spy)

        event = BaseEvent(
            event_id="EVT-001",
            mission_id="MSN-001",
            robot_id="RBT-001",
            event_type="GAS_HAZARD",
            timestamp_ms=1500,
            source_module="SafetyManager",
        )

        # Disconnect link
        service.disconnect()
        assert service.connected is False

        # Dispatch event while offline
        success = service.send_event(event)
        assert success is False
        assert len(service.sent_events) == 0
        assert len(service.queued_events) == 1
        assert service.queued_events[0] == event

    def test_tc_webrtc_005_reconnect_replays_queued_events(self) -> None:
        """TC-WEBRTC-005: Reconnection triggers chronological FIFO replay of all buffered events."""
        robot_spy = SpyRobotController()
        service = RemoteControlService(robot_spy)

        evt_1 = BaseEvent("EVT-001", "MSN-001", "RBT-001", "THERMAL_ALIVE", 1000, "Perception")
        evt_2 = BaseEvent("EVT-002", "MSN-001", "RBT-001", "GAS_HAZARD", 2000, "Safety")
        evt_3 = BaseEvent("EVT-003", "MSN-001", "RBT-001", "SLAM_FAILURE", 3000, "SLAM")

        # Disconnect and queue events
        service.disconnect()
        service.send_event(evt_1)
        service.send_event(evt_2)
        service.send_event(evt_3)

        assert len(service.queued_events) == 3
        assert len(service.sent_events) == 0

        # Reconnect
        service.connect()
        assert service.connected is True
        assert len(service.queued_events) == 0
        assert len(service.sent_events) == 3

        # Verify FIFO ordering
        assert service.sent_events[0] == evt_1
        assert service.sent_events[1] == evt_2
        assert service.sent_events[2] == evt_3
