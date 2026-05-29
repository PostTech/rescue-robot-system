"""TC-FUNC-BND-009: Event types — instantiation, frozen, enum completeness."""

from __future__ import annotations

import pytest

from domain_types.events import BaseEvent, EventPriority, EventType

# ---------------------------------------------------------------------------
# EventPriority enum
# ---------------------------------------------------------------------------


class TestEventPriority:
    def test_has_4_levels(self) -> None:
        expected = {"CRITICAL", "HIGH", "NORMAL", "LOW"}
        assert {p.value for p in EventPriority} == expected

    def test_ordering_by_value(self) -> None:
        assert EventPriority.CRITICAL == "CRITICAL"


# ---------------------------------------------------------------------------
# EventType enum
# ---------------------------------------------------------------------------


class TestEventType:
    def test_has_13_types(self) -> None:
        assert len(EventType) == 13

    def test_safety_events_present(self) -> None:
        safety = {EventType.EMERGENCY_STOP, EventType.GAS_HAZARD, EventType.SLAM_FAILURE}
        assert len(safety) == 3

    def test_mission_events_present(self) -> None:
        mission = {
            EventType.SEARCH_MISSION_CREATED,
            EventType.SEARCH_AREA_UPDATED,
            EventType.SEARCH_METHOD_SELECTED,
            EventType.MISSION_SETUP_APPLIED,
            EventType.MISSION_APPROVAL_REQUESTED,
        }
        assert len(mission) == 5

    def test_terrain_events_present(self) -> None:
        terrain = {EventType.TERRAIN_ANALYZED, EventType.SEARCH_DRIVE_PROFILE_SELECTED}
        assert len(terrain) == 2


# ---------------------------------------------------------------------------
# BaseEvent
# ---------------------------------------------------------------------------


class TestBaseEvent:
    @pytest.fixture()
    def sample_event(self) -> BaseEvent:
        return BaseEvent(
            event_id="EVT-001",
            mission_id="M-001",
            robot_id="R-001",
            event_type=EventType.THERMAL_ALIVE,
            timestamp_ms=1700000000000,
            source_module="detector",
        )

    def test_creation(self, sample_event: BaseEvent) -> None:
        assert sample_event.event_id == "EVT-001"
        assert sample_event.source_module == "detector"

    def test_frozen(self, sample_event: BaseEvent) -> None:
        with pytest.raises(AttributeError):
            sample_event.event_id = "EVT-999"

    def test_event_type_is_str(self, sample_event: BaseEvent) -> None:
        """event_type은 str이므로 EventType enum 값 이외의 문자열도 허용."""
        custom = BaseEvent(
            event_id="EVT-002",
            mission_id="M-001",
            robot_id="R-001",
            event_type="CUSTOM_EVENT",
            timestamp_ms=1700000000001,
            source_module="custom",
        )
        assert custom.event_type == "CUSTOM_EVENT"

    def test_timestamp_ms_is_int(self, sample_event: BaseEvent) -> None:
        assert isinstance(sample_event.timestamp_ms, int)
