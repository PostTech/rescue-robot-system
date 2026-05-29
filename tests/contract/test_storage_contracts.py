"""Contract tests for Storage Repositories verifying signature match and simple workflows."""

from __future__ import annotations

import inspect

from adapters.storage.in_memory_event_repository import InMemoryEventRepository
from adapters.storage.in_memory_media_repository import InMemoryMediaRepository
from domain_types.events import BaseEvent, EventPriority


class TestStorageContracts:
    def test_tc_storage_001_event_repository_contract(self) -> None:
        """TC-STORAGE-001: Validate InMemoryEventRepository satisfies the IEventRepository contract."""
        repo = InMemoryEventRepository()

        # 1. Structural duck typing check
        assert hasattr(repo, "save")
        sig = inspect.signature(repo.save)
        assert "event" in sig.parameters

        # 2. Workflow verify
        event = BaseEvent(
            event_id="EVT-100",
            mission_id="MSN-100",
            robot_id="RBT-100",
            event_type="THERMAL_ALIVE",
            timestamp_ms=1000,
            source_module="Perception",
            priority=EventPriority.NORMAL,
        )
        assert repo.save(event) is True

        # Verify retrieve helpers
        assert len(repo.get_all()) == 1
        assert repo.get_by_id("EVT-100") == event
        assert repo.get_by_id("EVT-999") is None

    def test_tc_storage_002_media_repository_contract(self) -> None:
        """TC-STORAGE-002: Validate InMemoryMediaRepository satisfies the IMediaRepository contract."""
        repo = InMemoryMediaRepository()

        # 1. Structural duck typing check
        assert hasattr(repo, "save_media")
        sig = inspect.signature(repo.save_media)
        assert "media" in sig.parameters

        # 2. Workflow verify
        mock_media = {"codec": "h264", "chunk_id": 1, "bytes": b"\x00\x01\x02"}
        assert repo.save_media(mock_media) is True

        assert len(repo.get_all()) == 1
        assert repo.get_all()[0] == mock_media
