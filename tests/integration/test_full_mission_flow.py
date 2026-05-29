"""Integration: Full mission flow end-to-end test."""

from __future__ import annotations

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


class TestFullMissionFlow:
    def test_full_flow_create_to_complete(self) -> None:
        """Full mission: create -> approve -> start -> terrain -> detect -> complete."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        id_gen = DeterministicIdGenerator("M", 0)
        app = ApplicationService(clock, id_gen)

        # Create
        req = SearchMissionRequest(
            request_id="REQ-FULL-001",
            operator_id="OP-001",
            mission_name="full flow test",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(0, 0, 0, 0, 0, 0),
                    Pose3D(20, 0, 0, 0, 0, 0),
                    Pose3D(20, 20, 0, 0, 0, 0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.PARALLEL_SWEEP,
            sop_profile_id="mountain_missing_person",
            priority="HIGH",
            created_at_ms=clock.now_ms(),
        )
        draft = app.create_mission(req)
        assert app.get_mission_state(draft.mission_id) == MissionState.DRAFT

        # Approve
        plan = app.approve_mission(draft.mission_id, "CMDR-FIELD")
        assert plan.approved_by == "CMDR-FIELD"
        assert app.get_mission_state(draft.mission_id) == MissionState.APPROVED

        # Start
        app.start_mission(draft.mission_id)
        assert app.get_mission_state(draft.mission_id) == MissionState.ACTIVE

        # Terrain updates
        t1 = app.process_terrain(draft.mission_id, 5.0, 2.0, 0.1, 0.05, 0.9)
        assert t1.traversable is True

        app.process_terrain(draft.mission_id, 35.0, 15.0, 0.5, 0.2, 0.4)
        ctx = app.get_mission_context(draft.mission_id)
        assert len(ctx.terrain_results) == 2

        # Detection
        det = MockDetector("THERMAL", DetectionLabel.VICTIM_ALIVE, 0.92)
        decision = app.process_detections(draft.mission_id, [det.detect(clock.now_ms())])
        assert decision.detected is True

        # Complete
        state = app.complete_mission(draft.mission_id)
        assert state == MissionState.COMPLETED

        # Events were recorded
        events = app.get_event_history()
        assert len(events) >= 4  # create + approve + terrain*2

    def test_full_flow_with_emergency_stop(self) -> None:
        """Mission interrupted by emergency stop mid-execution."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        id_gen = DeterministicIdGenerator("M", 0)
        app = ApplicationService(clock, id_gen)

        req = SearchMissionRequest(
            request_id="REQ-EMG-001",
            operator_id="OP-002",
            mission_name="emergency test",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(0, 0, 0, 0, 0, 0),
                    Pose3D(5, 0, 0, 0, 0, 0),
                    Pose3D(5, 5, 0, 0, 0, 0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.AREA_SWEEP,
            sop_profile_id="collapsed_structure",
            priority="CRITICAL",
            created_at_ms=clock.now_ms(),
        )

        draft = app.create_mission(req)
        app.approve_mission(draft.mission_id, "CMDR")
        app.start_mission(draft.mission_id)

        # Emergency stop
        state = app.emergency_stop(draft.mission_id)
        assert state == MissionState.EMERGENCY_STOPPED

    def test_deterministic_replay(self) -> None:
        """Two identical runs produce identical results."""

        def run() -> tuple[str, str, int]:
            clock = FakeClock(base_ms=1_700_000_000_000)
            id_gen = DeterministicIdGenerator("M", 0)
            app = ApplicationService(clock, id_gen)

            req = SearchMissionRequest(
                request_id="REQ-DET-001",
                operator_id="OP-001",
                mission_name="deterministic",
                search_area=SearchArea(
                    area_type=SearchAreaType.POLYGON,
                    coordinates=(
                        Pose3D(0, 0, 0, 0, 0, 0),
                        Pose3D(1, 0, 0, 0, 0, 0),
                        Pose3D(1, 1, 0, 0, 0, 0),
                    ),
                    frame_id="map",
                ),
                search_method=SearchMethod.GRID_COVERAGE,
                sop_profile_id="mountain_missing_person",
                priority="NORMAL",
                created_at_ms=clock.now_ms(),
            )
            draft = app.create_mission(req)
            plan = app.approve_mission(draft.mission_id, "CMDR")
            app.start_mission(draft.mission_id)
            app.process_terrain(draft.mission_id, 10.0, 3.0, 0.2, 0.1, 0.7)
            app.complete_mission(draft.mission_id)
            return draft.mission_id, plan.plan_snapshot_id, len(app.get_event_history())

        assert run() == run()

    def test_tick_simulation_full_lifecycle(self) -> None:
        """Integration: Test that tick_mission can drive a mission from DRAFT to COMPLETED."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        id_gen = DeterministicIdGenerator("M", 0)
        app = ApplicationService(clock, id_gen)

        req = SearchMissionRequest(
            request_id="REQ-TICK-001",
            operator_id="OP-001",
            mission_name="tick flow test",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(0, 0, 0, 0, 0, 0),
                    Pose3D(20, 0, 0, 0, 0, 0),
                    Pose3D(20, 20, 0, 0, 0, 0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.PARALLEL_SWEEP,
            sop_profile_id="mountain_missing_person",
            priority="HIGH",
            created_at_ms=clock.now_ms(),
        )

        draft = app.create_mission(req)
        mid = draft.mission_id

        # Tick 1: DRAFT -> APPROVED
        res = app.tick_mission(mid)
        assert res["status"] == MissionState.APPROVED
        assert "max_slope_deg" in res["sop_constraints"]  # Verify SOP constraints populated

        # Tick 2: APPROVED -> ACTIVE
        res = app.tick_mission(mid)
        assert res["status"] == MissionState.ACTIVE
        assert res["map_coverage_ratio"] == 0.0

        # Tick 3..12: Run ACTIVE ticks until completion
        for _ in range(10):
            res = app.tick_mission(mid)
            if res["status"] == MissionState.COMPLETED:
                break

        assert res["status"] == MissionState.COMPLETED
        assert res["map_coverage_ratio"] >= 1.0
        assert len(res["terrain_results"]) > 0
        assert len(res["detections"]) > 0  # Detections should have been triggered at 40% / 80%
