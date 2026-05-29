"""Mock WebRTC DataChannel for Windows testing.

Simulates bidirectional message exchange without real WebRTC.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MockDataChannel:
    """Simulates a WebRTC DataChannel for control/event messages."""

    channel_id: str
    is_open: bool = True
    sent_messages: list[dict[str, object]] = field(default_factory=list)
    received_messages: list[dict[str, object]] = field(default_factory=list)

    def send(self, message: dict[str, object]) -> bool:
        """Send a message through the channel.

        Returns True if sent successfully, False if channel is closed.
        """
        if not self.is_open:
            return False
        self.sent_messages.append(message)
        return True

    def receive(self, message: dict[str, object]) -> None:
        """Simulate receiving a message from the remote peer."""
        self.received_messages.append(message)

    def close(self) -> None:
        """Close the channel."""
        self.is_open = False

    def reset(self) -> None:
        """Reset channel state for reuse in tests."""
        self.is_open = True
        self.sent_messages.clear()
        self.received_messages.clear()
