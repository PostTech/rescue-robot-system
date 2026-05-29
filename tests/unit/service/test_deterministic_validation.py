"""TC-DETVAL-001/003/004/006/008/009: Deterministic validation tests."""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.events import BaseEvent, EventType
from domain_types.mission import (
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionRequest,
)
from domain_types.terrain import TerrainAnalysisResult, TerrainClass, TraversabilityLevel
from service.deterministic_validation import (
    create_deterministic_draft,
    create_deterministic_storage_key,
)
from service.search_drive_policy import decide_drive_profile
from service.terrain_analyzer import analyze_terrain


def _fixed_request() -> SearchMissionRequest:
    return SearchMissionRequest(
        request_id="REQ-DET-001",
        operator_id="OP-001",
        mission_name="deterministic test",
        search_area=SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(
                Pose3D(0, 0, 0, 0, 0, 0),
                Pose3D(1, 0, 0, 0, 0, 0),
                Pose3D(1, 1, 0, 0, 0, 0),
            ),
            frame_id="map",
        ),
        search_method=SearchMethod.PARALLEL_SWEEP,
        sop_profile_id="mountain_missing_person",
        priority="HIGH",
        created_at_ms=1_700_000_000_000,
    )


def _fixed_terrain() -> TerrainAnalysisResult:
    return TerrainAnalysisResult(
        terrain_class=TerrainClass.STEEP_SLOPE,
        slope_degree=40.0,
        step_height_cm=10.0,
        roughness_score=0.3,
        obstacle_density=0.1,
        traversability_score=0.5,
        traversability_level=TraversabilityLevel.CAUTION,
        traversable=True,
    )


class TestDeterministicClock:
    def test_tc_detval_001_fixed_clock(self) -> None:
        """TC-DETVAL-001: Event timestamp does not depend on real time."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        evt1 = BaseEvent(
            event_id="E1",
            mission_id="M1",
            robot_id="R1",
            event_type=EventType.TERRAIN_ANALYZED,
            timestamp_ms=clock.now_ms(),
            source_module="test",
        )
        clock2 = FakeClock(base_ms=1_700_000_000_000)
        evt2 = BaseEvent(
            event_id="E1",
            mission_id="M1",
            robot_id="R1",
            event_type=EventType.TERRAIN_ANALYZED,
            timestamp_ms=clock2.now_ms(),
            source_module="test",
        )
        assert evt1.timestamp_ms == evt2.timestamp_ms
        assert evt1 == evt2


class TestDeterministicEventOrdering:
    def test_tc_detval_003_event_ordering(self) -> None:
        """TC-DETVAL-003: Same event list => same processing order."""
        clock = FakeClock(base_ms=0)
        events: list[BaseEvent] = []
        for i, et in enumerate(
            [
                EventType.SEARCH_MISSION_CREATED,
                EventType.TERRAIN_ANALYZED,
                EventType.SEARCH_DRIVE_PROFILE_SELECTED,
            ]
        ):
            clock.advance(100)
            events.append(
                BaseEvent(
                    event_id=f"E-{i}",
                    mission_id="M1",
                    robot_id="R1",
                    event_type=et,
                    timestamp_ms=clock.now_ms(),
                    source_module="test",
                )
            )
        sorted_events = sorted(events, key=lambda e: e.timestamp_ms)

        clock2 = FakeClock(base_ms=0)
        events2: list[BaseEvent] = []
        for i, et in enumerate(
            [
                EventType.SEARCH_MISSION_CREATED,
                EventType.TERRAIN_ANALYZED,
                EventType.SEARCH_DRIVE_PROFILE_SELECTED,
            ]
        ):
            clock2.advance(100)
            events2.append(
                BaseEvent(
                    event_id=f"E-{i}",
                    mission_id="M1",
                    robot_id="R1",
                    event_type=et,
                    timestamp_ms=clock2.now_ms(),
                    source_module="test",
                )
            )
        sorted_events2 = sorted(events2, key=lambda e: e.timestamp_ms)
        assert sorted_events == sorted_events2


class TestDeterministicMissionDraft:
    def test_tc_detval_004_state_snapshot(self) -> None:
        """TC-DETVAL-004: Same scenario => same Mission State Snapshot."""
        req = _fixed_request()
        d1 = create_deterministic_draft(
            req, FakeClock(base_ms=1_700_000_000_000), DeterministicIdGenerator("M", 0)
        )
        d2 = create_deterministic_draft(
            req, FakeClock(base_ms=1_700_000_000_000), DeterministicIdGenerator("M", 0)
        )
        assert d1.mission_id == d2.mission_id
        assert d1.draft_snapshot_id == d2.draft_snapshot_id
        assert d1.validation_status == d2.validation_status

    def test_tc_detval_008_draft_snapshot(self) -> None:
        """TC-DETVAL-008: Same request + SOP => same draft_snapshot_id."""
        req = _fixed_request()
        constraints = {"max_slope": 30.0}
        d1 = create_deterministic_draft(
            req, FakeClock(base_ms=1_700_000_000_000), DeterministicIdGenerator("M", 0), constraints
        )
        d2 = create_deterministic_draft(
            req, FakeClock(base_ms=1_700_000_000_000), DeterministicIdGenerator("M", 0), constraints
        )
        assert d1.draft_snapshot_id == d2.draft_snapshot_id
        assert d1.sop_constraints == d2.sop_constraints


class TestDeterministicStorageKey:
    def test_tc_detval_006_storage_key(self) -> None:
        """TC-DETVAL-006: Same event => same storage key."""
        k1 = create_deterministic_storage_key("MissionDraft", "M-000001", 1_700_000_000_000)
        k2 = create_deterministic_storage_key("MissionDraft", "M-000001", 1_700_000_000_000)
        assert k1 == k2
        assert k1 == "MissionDraft:M-000001:1700000000000"


class TestDeterministicDriveProfile:
    def test_tc_detval_009_drive_profile(self) -> None:
        """TC-DETVAL-009: Same terrain + method => same SearchDriveProfile."""
        terrain = _fixed_terrain()
        p1 = decide_drive_profile(terrain, SearchMethod.CONTOUR_SEARCH)
        p2 = decide_drive_profile(terrain, SearchMethod.CONTOUR_SEARCH)
        assert p1 == p2
        assert p1.locomotion_mode == p2.locomotion_mode
        assert p1.speed_scale == p2.speed_scale

    def test_tc_detval_009_analyzer_deterministic(self) -> None:
        """TC-DETVAL-009: Same raw features => same TerrainAnalysisResult."""
        r1 = analyze_terrain(40.0, 10.0, 0.3, 0.1, 0.5)
        r2 = analyze_terrain(40.0, 10.0, 0.3, 0.1, 0.5)
        assert r1 == r2
