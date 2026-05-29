"""Unit tests for StorageSyncService verifying backoff timing, capacity evictions, and determinism."""

from __future__ import annotations

from adapters.storage.in_memory_event_repository import InMemoryEventRepository
from adapters.storage.in_memory_media_repository import InMemoryMediaRepository
from domain_types.events import BaseEvent, EventPriority
from service.storage_sync_service import StorageSyncService


class TestStorageSyncService:
    def test_tc_storage_003_sync_retry_on_failure(self) -> None:
        """TC-STORAGE-003: Verify chronological exponential backoff retry execution via tick engine."""
        event_repo = InMemoryEventRepository(max_capacity=5)
        media_repo = InMemoryMediaRepository(max_capacity=5)
        service = StorageSyncService(event_repo, media_repo, base_delay_ms=100, max_retries=3)

        # Fault injection: force the next 2 remote synchronization attempts to fail
        service.sync_failure_count = 2

        event = BaseEvent(
            event_id="EVT-001",
            mission_id="MSN-001",
            robot_id="RBT-001",
            event_type="GAS_HAZARD",
            timestamp_ms=1000,
            source_module="Safety",
            priority=EventPriority.HIGH,
        )

        # First attempt: Saves locally but remote sync fails and queues backoff
        assert service.save_and_sync_event(event) is True
        assert len(service.remote_synced_events) == 0
        assert len(service.pending_syncs) == 1
        assert service.pending_syncs[0]["attempt"] == 1
        assert service.pending_syncs[0]["remaining_delay_ms"] == 100

        # Tick 50ms: Not expired yet
        service.tick(50)
        assert len(service.remote_synced_events) == 0
        assert service.pending_syncs[0]["remaining_delay_ms"] == 50

        # Tick another 50ms: Expired, retries. This is the 2nd attempt, which fails again
        # Delay scales to: base_delay * 2^(2-1) = 100 * 2 = 200ms
        service.tick(50)
        assert len(service.remote_synced_events) == 0
        assert len(service.pending_syncs) == 1
        assert service.pending_syncs[0]["attempt"] == 2
        assert service.pending_syncs[0]["remaining_delay_ms"] == 200

        # Tick 150ms: Not expired (200 - 150 = 50ms remaining)
        service.tick(150)
        assert len(service.remote_synced_events) == 0
        assert service.pending_syncs[0]["remaining_delay_ms"] == 50

        # Tick 50ms: Expired, retries. This is the 3rd attempt, which succeeds because failure counter is 0
        service.tick(50)
        assert len(service.remote_synced_events) == 1
        assert service.remote_synced_events[0] == event
        assert len(service.pending_syncs) == 0

    def test_tc_storage_004_critical_events_preserved_on_storage_full(self) -> None:
        """TC-STORAGE-004: Ensure low-priority events are evicted to accommodate critical warnings on capacity full."""
        # Mini capacity limits to 2
        event_repo = InMemoryEventRepository(max_capacity=2)
        media_repo = InMemoryMediaRepository(max_capacity=5)
        service = StorageSyncService(event_repo, media_repo)

        e_low1 = BaseEvent(
            event_id="E-001",
            mission_id="M-1",
            robot_id="R-1",
            event_type="RGB_BODY_PART",
            timestamp_ms=100,
            source_module="Perception",
            priority=EventPriority.LOW,
        )
        e_low2 = BaseEvent(
            event_id="E-002",
            mission_id="M-1",
            robot_id="R-1",
            event_type="RGB_BODY_PART",
            timestamp_ms=200,
            source_module="Perception",
            priority=EventPriority.NORMAL,
        )
        e_low3 = BaseEvent(
            event_id="E-003",
            mission_id="M-1",
            robot_id="R-1",
            event_type="RGB_BODY_PART",
            timestamp_ms=300,
            source_module="Perception",
            priority=EventPriority.NORMAL,
        )

        e_critical = BaseEvent(
            event_id="E-004",
            mission_id="M-1",
            robot_id="R-1",
            event_type="EMERGENCY_STOP",
            timestamp_ms=400,
            source_module="Safety",
            priority=EventPriority.CRITICAL,
        )

        # 1. Fill low priority events to full
        assert service.save_and_sync_event(e_low1) is True
        assert service.save_and_sync_event(e_low2) is True
        assert len(event_repo.get_all()) == 2

        # 2. Saving another low-priority event should be discarded due to storage full
        assert service.save_and_sync_event(e_low3) is False
        assert len(event_repo.get_all()) == 2

        # 3. Saving a CRITICAL event should succeed by evicting the oldest low/normal priority event
        assert service.save_and_sync_event(e_critical) is True
        events_left = event_repo.get_all()
        assert len(events_left) == 2
        assert e_critical in events_left
        # e_low1 (the oldest low/normal priority) should have been evicted
        assert e_low1 not in events_left
        assert e_low2 in events_left

    def test_tc_detval_006_deterministic_storage_key(self) -> None:
        """TC-DETVAL-006: Verify deterministic storage and querying key bindings."""
        repo = InMemoryEventRepository(max_capacity=10)
        e1 = BaseEvent(
            event_id="EVT-999",
            mission_id="MSN-1",
            robot_id="RBT-1",
            event_type="SLAM_FAILURE",
            timestamp_ms=100,
            source_module="SLAM",
            priority=EventPriority.HIGH,
        )
        repo.save(e1)

        # Same key always retrieves the identical event
        assert repo.get_by_id("EVT-999") == e1
        assert repo.get_by_id("EVT-999") is repo.get_by_id("EVT-999")

    def test_tc_detval_007_same_failure_same_retry_order(self) -> None:
        """TC-DETVAL-007: Guarantee that same failure input triggers identical retry tick sequence (Determinism)."""
        # Create two isolated servers with identical settings
        repo_a = InMemoryEventRepository(max_capacity=10)
        media_a = InMemoryMediaRepository(max_capacity=10)
        service_a = StorageSyncService(repo_a, media_a, base_delay_ms=100)

        repo_b = InMemoryEventRepository(max_capacity=10)
        media_b = InMemoryMediaRepository(max_capacity=10)
        service_b = StorageSyncService(repo_b, media_b, base_delay_ms=100)

        evt_a = BaseEvent(
            event_id="E-001",
            mission_id="M-1",
            robot_id="R-1",
            event_type="GAS_HAZARD",
            timestamp_ms=100,
            source_module="Safety",
            priority=EventPriority.CRITICAL,
        )
        evt_b = BaseEvent(
            event_id="E-001",
            mission_id="M-1",
            robot_id="R-1",
            event_type="GAS_HAZARD",
            timestamp_ms=100,
            source_module="Safety",
            priority=EventPriority.CRITICAL,
        )

        # Inject same synchronization fault rate
        service_a.sync_failure_count = 3
        service_b.sync_failure_count = 3

        # Push to queue
        service_a.save_and_sync_event(evt_a)
        service_b.save_and_sync_event(evt_b)

        # Apply deterministic chronological ticks side-by-side
        tick_sequence = [50, 50, 100, 100, 200, 200]
        for tick_ms in tick_sequence:
            service_a.tick(tick_ms)
            service_b.tick(tick_ms)
            # Ensure states match perfectly at each step
            assert len(service_a.pending_syncs) == len(service_b.pending_syncs)
            assert len(service_a.remote_synced_events) == len(service_b.remote_synced_events)

        # Final assertion: both succeeded at the exact same tick boundaries
        assert len(service_a.remote_synced_events) == 1
        assert len(service_b.remote_synced_events) == 1
        assert (
            service_a.remote_synced_events[0].event_id == service_b.remote_synced_events[0].event_id
        )
