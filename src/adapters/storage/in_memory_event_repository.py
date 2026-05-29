"""In-memory event repository implementation.

Implements IEventRepository protocol, providing maximum capacity thresholds,
low-priority discard policies on storage overflow, and deterministic query helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain_types.events import EventPriority

if TYPE_CHECKING:
    from domain_types.events import BaseEvent


class InMemoryEventRepository:
    """In-memory persistence for BaseEvent logs.

    Implements a strict capacity-based eviction policy:
    If capacity is full, CRITICAL/HIGH events evict the oldest NORMAL/LOW event.
    NORMAL/LOW events are discarded on capacity exhaustion.
    """

    def __init__(self, max_capacity: int = 100) -> None:
        self.max_capacity = max_capacity
        self.events: list[BaseEvent] = []

    def save(self, event: BaseEvent) -> bool:
        """Persists a domain event, enforcing priority-based space eviction rules."""
        if len(self.events) < self.max_capacity:
            self.events.append(event)
            return True

        # Storage capacity full: attempt eviction of lower priority events
        if event.priority in (EventPriority.CRITICAL, EventPriority.HIGH):
            # Find the oldest event that is NORMAL or LOW
            for existing_event in self.events:
                if existing_event.priority in (EventPriority.NORMAL, EventPriority.LOW):
                    self.events.remove(existing_event)
                    self.events.append(event)
                    return True

        # Eviction failed or incoming event is low-priority
        return False

    def get_all(self) -> list[BaseEvent]:
        """Returns all persisted events in insertion order."""
        return list(self.events)

    def get_by_id(self, event_id: str) -> BaseEvent | None:
        """Finds a single event by its unique ID."""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None
