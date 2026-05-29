"""Server-3: Storage / DB interface contracts."""

from __future__ import annotations

from typing import Any, Protocol

from domain_types.events import BaseEvent


class IEventRepository(Protocol):
    """Persists domain events."""

    def save(self, event: BaseEvent) -> None: ...


class IMediaRepository(Protocol):
    """Persists robotic media chunks (video, audio, pointclouds)."""

    def save_media(self, media: Any) -> bool: ...
