"""In-memory media repository implementation.

Implements IMediaRepository protocol, simulating storage limitations for high-bandwidth
robotic telemetry media streams (videos, audio frames, point clouds).
"""

from __future__ import annotations

from typing import Any


class InMemoryMediaRepository:
    """In-memory persistence for robotic media packets (e.g. LiDAR pointclouds or RGB chunks)."""

    def __init__(self, max_capacity: int = 10) -> None:
        self.max_capacity = max_capacity
        self.media_store: list[Any] = []

    def save_media(self, media: Any) -> bool:
        """Saves a media chunk. Rejects storage when maximum capacity is exhausted."""
        if len(self.media_store) < self.max_capacity:
            self.media_store.append(media)
            return True
        return False

    def get_all(self) -> list[Any]:
        """Returns all saved media chunks."""
        return list(self.media_store)
