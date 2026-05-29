"""Remote Control Service implementation.

Routes control commands from the operator UI to the low-level robot controller,
handles real-time event routing, and manages connectivity failover via local queueing
and FIFO replay upon reconnection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain_types.mission import ControlCommandType
from domain_types.terrain import LocomotionMode

if TYPE_CHECKING:
    from domain_types.events import BaseEvent
    from domain_types.mission import ControlCommand
    from domain_types.search.protocols import IRobotController


class RemoteControlService:
    """Manages remote operation commands, system event routing, and link connectivity state."""

    def __init__(self, robot_controller: IRobotController) -> None:
        self.robot_controller = robot_controller
        self.connected = True
        self.queued_events: list[BaseEvent] = []
        self.sent_events: list[BaseEvent] = []
        self.received_commands: list[ControlCommand] = []

    def connect(self) -> None:
        """Restores connectivity link and replays queued events in FIFO order."""
        self.connected = True
        # FIFO replay of buffered events
        events_to_replay = list(self.queued_events)
        self.queued_events.clear()
        for event in events_to_replay:
            self.send_event(event)

    def disconnect(self) -> None:
        """Simulates connectivity loss, forcing all future events into local buffer."""
        self.connected = False

    def send_event(self, event: BaseEvent) -> bool:
        """Sends an autonomous event to the operator. Buffers it locally if link is down."""
        if self.connected:
            self.sent_events.append(event)
            return True
        else:
            self.queued_events.append(event)
            return False

    def receive_remote_command(self, command: ControlCommand) -> bool:
        """Processes a control command received from remote operator panel and routes it.

        Control commands are executed on the low-level robot controller.
        Returns False if the link is disconnected or routing fails.
        """
        if not self.connected:
            return False

        try:
            if command.command_type == ControlCommandType.MOVE:
                payload = command.payload
                mode_str = payload.get("mode", "WHEEL")
                try:
                    mode = LocomotionMode(mode_str)
                except ValueError:
                    mode = LocomotionMode.WHEEL

                speed = float(payload.get("speed", 1.0))
                self.robot_controller.move(mode, speed)

            elif (
                command.command_type == ControlCommandType.STOP
                or command.command_type == ControlCommandType.EMERGENCY_STOP
            ):
                self.robot_controller.stop()

            elif command.command_type == ControlCommandType.SET_MODE:
                payload = command.payload
                mode_str = payload.get("mode", "STOP")
                try:
                    mode = LocomotionMode(mode_str)
                except ValueError:
                    mode = LocomotionMode.STOP

                self.robot_controller.move(mode, 0.0)

            self.received_commands.append(command)
            return True
        except Exception:
            return False
