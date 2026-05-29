"""TC-INTEG-001~005: Application service unit tests."""

from __future__ import annotations

import pytest

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.mission import (
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionRequest,
)
from service.application_service import ApplicationService
from service.mission_state_machine import MissionState
from service.mock_detector import DetectionLabel, MockDetector


def _clock() -> FakeClock:
    return FakeClock(base_ms=1_700_000_000_000)


def _id_gen() -> DeterministicIdGenerator:
    return DeterministicIdGenerator("M", 0)


def _request(rid: str = "REQ-001") -> SearchMissionRequest:
    return SearchMissionRequest(
        request_id=rid,
        operator_id="OP-001",
        mission_name="integration test",
        search_area=SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(
                Pose3D(0, 0, 0, 0, 0, 0),
                Pose3D(10, 0, 0, 0, 0, 0),
                Pose3D(10, 10, 0, 0, 0, 0),
            ),
            frame_id="map",
        ),
        search_method=SearchMethod.PARALLEL_SWEEP,
        sop_profile_id="mountain_missing_person",
        priority="HIGH",
        created_at_ms=1_700_000_000_000,
    )


class TestApplicationServiceCreation:
    def test_tc_integ_001_create_to_approval(self) -> None:
        """TC-INTEG-001: Full mission creation to approval flow."""
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())
        assert draft.mission_id == "M-000001"
        assert app.get_mission_state(draft.mission_id) == MissionState.DRAFT

        plan = app.approve_mission(draft.mission_id, "CMDR-001")
        assert plan.approved_by == "CMDR-001"
        assert app.get_mission_state(draft.mission_id) == MissionState.APPROVED

    def test_create_populates_context(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())
        ctx = app.get_mission_context(draft.mission_id)
        assert ctx.request.operator_id == "OP-001"
        assert ctx.draft is draft

    def test_nonexistent_mission_raises(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        with pytest.raises(ValueError, match="not found"):
            app.get_mission_state("NONEXISTENT")


class TestApplicationServiceExecution:
    def _setup(self) -> tuple[ApplicationService, str]:
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())
        app.approve_mission(draft.mission_id, "CMDR")
        app.start_mission(draft.mission_id)
        return app, draft.mission_id

    def test_tc_integ_002_terrain_during_execution(self) -> None:
        """TC-INTEG-002: Terrain analysis during mission execution."""
        app, mid = self._setup()
        result = app.process_terrain(mid, 5.0, 2.0, 0.1, 0.05, 0.9)
        assert result.terrain_class.value is not None
        ctx = app.get_mission_context(mid)
        assert len(ctx.terrain_results) == 1

    def test_detection_during_execution(self) -> None:
        app, mid = self._setup()
        det = MockDetector("THERMAL", DetectionLabel.VICTIM_ALIVE, 0.95)
        decision = app.process_detections(mid, [det.detect()])
        assert decision.detected is True
        ctx = app.get_mission_context(mid)
        assert len(ctx.detections) == 1

    def test_complete_mission(self) -> None:
        app, mid = self._setup()
        state = app.complete_mission(mid)
        assert state == MissionState.COMPLETED

    def test_abort_mission(self) -> None:
        app, mid = self._setup()
        state = app.abort_mission(mid)
        assert state == MissionState.ABORTED


class TestApplicationServiceSafety:
    def test_tc_integ_003_emergency_stop(self) -> None:
        """TC-INTEG-003: Emergency stop aborts active mission."""
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())
        app.approve_mission(draft.mission_id, "CMDR")
        app.start_mission(draft.mission_id)

        state = app.emergency_stop(draft.mission_id)
        assert state == MissionState.EMERGENCY_STOPPED


class TestApplicationServiceSOP:
    def test_tc_integ_004_sop_applied(self) -> None:
        """TC-INTEG-004: SOP recommendation applied at creation."""
        app = ApplicationService(_clock(), _id_gen())
        req = _request()
        draft = app.create_mission(req)
        # Draft created with validation_status PENDING_APPROVAL
        assert draft.validation_status == "PENDING_APPROVAL"


class TestApplicationServiceDeterministic:
    def test_tc_integ_005_deterministic_replay(self) -> None:
        """TC-INTEG-005: Same input sequence produces same final state."""

        def run_scenario() -> tuple[str, str, int]:
            app = ApplicationService(
                FakeClock(base_ms=1_700_000_000_000),
                DeterministicIdGenerator("M", 0),
            )
            draft = app.create_mission(_request())
            plan = app.approve_mission(draft.mission_id, "CMDR")
            app.start_mission(draft.mission_id)
            app.process_terrain(draft.mission_id, 30.0, 8.0, 0.3, 0.1, 0.6)
            app.complete_mission(draft.mission_id)
            events = app.get_event_history()
            return draft.mission_id, plan.plan_snapshot_id, len(events)

        r1 = run_scenario()
        r2 = run_scenario()
        assert r1 == r2


class TestApplicationServiceEvents:
    def test_event_history_populated(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())
        events = app.get_event_history()
        assert len(events) >= 1
        assert events[0].mission_id == draft.mission_id


class TestApplicationServiceEnrichment:
    def test_get_available_sop_profiles(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        profiles = app.get_available_sop_profiles()
        assert len(profiles) == 3
        assert profiles[0]["id"] == "mountain_missing_person"

    def test_get_all_missions_and_summaries(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        draft1 = app.create_mission(_request("REQ-001"))
        draft2 = app.create_mission(_request("REQ-002"))

        missions = app.get_all_missions()
        assert len(missions) == 2

        summaries = app.get_mission_summary_list()
        assert len(summaries) == 2
        assert summaries[0]["mission_id"] == draft1.mission_id
        assert summaries[1]["mission_id"] == draft2.mission_id

    def test_get_mission_details(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())

        details = app.get_mission_details(draft.mission_id)
        assert details["mission_id"] == draft.mission_id
        assert details["status"] == MissionState.DRAFT
        assert "sop_constraints" in details
        assert len(details["search_area"]["coordinates"]) == 3

    def test_tick_mission_simulation_flow(self) -> None:
        app = ApplicationService(_clock(), _id_gen())
        draft = app.create_mission(_request())
        mid = draft.mission_id

        # 1. First tick (DRAFT -> APPROVED)
        details = app.tick_mission(mid)
        assert details["status"] == MissionState.APPROVED

        # 2. Second tick (APPROVED -> ACTIVE)
        details = app.tick_mission(mid)
        assert details["status"] == MissionState.ACTIVE
        assert details["map_coverage_ratio"] == 0.0

        # 3. Third tick (ACTIVE simulation steps)
        details = app.tick_mission(mid)
        assert details["status"] == MissionState.ACTIVE
        assert details["map_coverage_ratio"] == 0.10
        assert details["current_pose"]["yaw"] > 0
