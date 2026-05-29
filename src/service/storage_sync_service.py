"""Storage Sync Service implementation.

Orchestrates local-first database/file routing, network failover queueing,
and deterministic exponential backoff execution with FakeClock tick integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from domain_types.events import EventPriority

if TYPE_CHECKING:
    from domain_types.db.protocols import IEventRepository, IMediaRepository
    from domain_types.events import BaseEvent


class StorageSyncService:
    """Orchestrates local-first persistence and remote sync queues using exponential backoff."""

    def __init__(
        self,
        event_repo: IEventRepository,
        media_repo: IMediaRepository,
        base_delay_ms: int = 100,
        max_retries: int = 5,
    ) -> None:
        self.event_repo = event_repo
        self.media_repo = media_repo
        self.base_delay_ms = base_delay_ms
        self.max_retries = max_retries

        # Simulated remote servers
        self.remote_synced_events: list[BaseEvent] = []
        self.remote_synced_media: list[Any] = []

        # Synchronization retry queue
        # Each item: {"type": "event"|"media", "data": obj, "attempt": int, "remaining_delay_ms": int}
        self.pending_syncs: list[dict[str, Any]] = []

        # Fault injection trigger for tests
        self.sync_failure_count = 0

    def save_and_sync_event(self, event: BaseEvent) -> bool:
        """Saves event locally first, then attempts to stream it to remote control center.

        If network fails, schedules a deterministic backoff retry task.
        Returns False if local storage fails.
        """
        # 1. Local-first persistence
        local_saved = self.event_repo.save(event)
        if not local_saved:
            return False

        # 2. Remote synchronization attempt
        if self._attempt_sync_event(event):
            self.remote_synced_events.append(event)
        else:
            # Enqueue for chronological retry
            self.pending_syncs.append(
                {
                    "type": "event",
                    "data": event,
                    "attempt": 1,
                    "remaining_delay_ms": self.base_delay_ms,
                }
            )

        return True

    def save_and_sync_media(self, media: Any) -> bool:
        """Saves media chunk locally first, then attempts to stream it to remote storage.

        If network fails, schedules a backoff retry task.
        Returns False if local storage fails.
        """
        # 1. Local-first persistence
        local_saved = self.media_repo.save_media(media)
        if not local_saved:
            return False

        # 2. Remote synchronization attempt
        if self._attempt_sync_media(media):
            self.remote_synced_media.append(media)
        else:
            self.pending_syncs.append(
                {
                    "type": "media",
                    "data": media,
                    "attempt": 1,
                    "remaining_delay_ms": self.base_delay_ms,
                }
            )

        return True

    def tick(self, delta_time_ms: int) -> None:
        """Advances simulated timeline, trigger chronological retries for expired items."""
        still_pending: list[dict[str, Any]] = []

        for item in self.pending_syncs:
            item["remaining_delay_ms"] -= delta_time_ms

            if item["remaining_delay_ms"] <= 0:
                # Time to retry synchronization
                success = False
                if item["type"] == "event":
                    success = self._attempt_sync_event(item["data"])
                    if success:
                        self.remote_synced_events.append(item["data"])
                elif item["type"] == "media":
                    success = self._attempt_sync_media(item["data"])
                    if success:
                        self.remote_synced_media.append(item["data"])

                if not success:
                    # Increment attempt count
                    attempt = item["attempt"] + 1

                    # Check retries limit
                    is_critical = False
                    if item["type"] == "event":
                        is_critical = item["data"].priority in (
                            EventPriority.CRITICAL,
                            EventPriority.HIGH,
                        )

                    if attempt > self.max_retries and not is_critical:
                        # Non-critical items are discarded after reaching max retries limit
                        continue

                    # Exponential backoff delay calculation: base_delay * 2^(attempt - 1)
                    next_delay = self.base_delay_ms * (2 ** (attempt - 1))
                    item["attempt"] = attempt
                    item["remaining_delay_ms"] = next_delay
                    still_pending.append(item)
            else:
                still_pending.append(item)

        self.pending_syncs = still_pending

    # --- Simulated Telemetry Gateway Private Methods ---

    def _attempt_sync_event(self, event: BaseEvent) -> bool:
        if self.sync_failure_count > 0:
            self.sync_failure_count -= 1
            return False
        return True

    def _attempt_sync_media(self, media: Any) -> bool:
        if self.sync_failure_count > 0:
            self.sync_failure_count -= 1
            return False
        return True
