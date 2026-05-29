"""In-process event bus.

Synchronous publish/subscribe for domain events.
No external message broker dependency.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from domain_types.events import BaseEvent

EventHandler = Callable[[BaseEvent], None]


class EventBus:
    """Simple synchronous event bus for in-process event delivery.

    Usage::

        bus = EventBus()
        bus.subscribe("THERMAL_DETECTED", handler_fn)
        bus.publish(event)
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._global_handlers: list[EventHandler] = []
        self._history: list[BaseEvent] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type."""
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler to all event types."""
        self._global_handlers.append(handler)

    def publish(self, event: BaseEvent) -> None:
        """Publish an event to all matching subscribers.

        Events are delivered synchronously in subscription order.
        All events are recorded in history.
        """
        self._history.append(event)

        for h in self._global_handlers:
            h(event)

        for h in self._handlers.get(event.event_type, []):
            h(event)

    def get_history(self) -> list[BaseEvent]:
        """Return all published events in order."""
        return list(self._history)

    def clear(self) -> None:
        """Clear all subscriptions and history."""
        self._handlers.clear()
        self._global_handlers.clear()
        self._history.clear()
