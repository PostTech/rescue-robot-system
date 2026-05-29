"""End-to-End: Mountain search missing person SOP scenario (TC-SCENARIO-001)."""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.mission import (
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionRequest,
)
from domain_types.terrain import LocomotionMode
from service.application_service import ApplicationService
from service.mission_state_machine import MissionState
from service.mock_detector import DetectionLabel, DetectionResult


class TestMountainMissingPersonScenario:
    def test_tc_scenario_001_mountain_search_completes(self) -> None:
        """TC-SCENARIO-001: Verifies the full mountain search lifecycle with contour sweeping."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        id_gen = DeterministicIdGenerator("M", 0)
        app = ApplicationService(clock, id_gen)

        # 1. Draft Creation with mountain SOP profile
        req = SearchMissionRequest(
            request_id="REQ-MNT-001",
            operator_id="OP-FIELD-MNT",
            mission_name="Mountain Search Missing Person",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(50.0, 10.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(30.0, 40.0, 0.0, 0.0, 0.0, 0.0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.CONTOUR_SEARCH,
            sop_profile_id="mountain_missing_person",
            priority="HIGH",
            created_at_ms=clock.now_ms(),
        )

        draft = app.create_mission(req)
        mid = draft.mission_id
        assert app.get_mission_state(mid) == MissionState.DRAFT

        # 2. Approve Draft
        plan = app.approve_mission(mid, "CDR-MNT")
        assert app.get_mission_state(mid) == MissionState.APPROVED
        assert plan.search_method == SearchMethod.CONTOUR_SEARCH

        # 3. Start Mission
        app.start_mission(mid)
        assert app.get_mission_state(mid) == MissionState.ACTIVE

        # 4. Terrain Updates: Steep mountain slope (28 degrees) encountered
        # Decides drive profile based on slope=40.0, method=CONTOUR_SEARCH
        terrain = app.process_terrain(
            mission_id=mid,
            slope=40.0,
            step_height=5.0,
            roughness=0.1,
            obstacle_density=0.05,
            traversability=0.65,
        )
        assert terrain.slope_degree == 40.0
        # Robot controller gear adapt (Contour search on steep slopes triggers Slow Safe mode)
        assert app._robot.locomotion_mode == LocomotionMode.SLOW_SAFE

        # 5. Sensor Detections: High-priority Thermal Sensor captures human heat signature
        thermal_det = DetectionResult(
            sensor_type="THERMAL",
            label=DetectionLabel.VICTIM_ALIVE,
            confidence=0.92,
            bounding_box=(200, 300, 60, 60),
            timestamp_ms=clock.now_ms(),
        )
        decision = app.process_detections(mid, [thermal_det])
        assert decision.detected is True
        assert decision.confidence == 0.92
        assert decision.primary_sensor == "THERMAL"

        # 6. Success Completion
        app.complete_mission(mid)
        assert app.get_mission_state(mid) == MissionState.COMPLETED

        # 7. Timeline event validation
        events = app.get_event_history()
        assert len(events) >= 3  # Created, Approved, Terrain

    def test_tc_scenario_004_mountain_determinism(self) -> None:
        """TC-SCENARIO-004: Validates same inputs yield perfectly identical outputs (Replay)."""

        def run_mnt() -> tuple[str, str, int, str]:
            clock = FakeClock(base_ms=1_700_000_000_000)
            id_gen = DeterministicIdGenerator("M", 0)
            app = ApplicationService(clock, id_gen)

            req = SearchMissionRequest(
                request_id="REQ-DET-MNT",
                operator_id="OP-DET",
                mission_name="Det Mountain",
                search_area=SearchArea(
                    area_type=SearchAreaType.POLYGON,
                    coordinates=(
                        Pose3D(0, 0, 0, 0, 0, 0),
                        Pose3D(10, 0, 0, 0, 0, 0),
                        Pose3D(10, 10, 0, 0, 0, 0),
                    ),
                    frame_id="map",
                ),
                search_method=SearchMethod.CONTOUR_SEARCH,
                sop_profile_id="mountain_missing_person",
                priority="HIGH",
                created_at_ms=clock.now_ms(),
            )
            draft = app.create_mission(req)
            plan = app.approve_mission(draft.mission_id, "CDR")
            app.start_mission(draft.mission_id)
            app.process_terrain(draft.mission_id, 40.0, 5.0, 0.1, 0.05, 0.65)
            app.complete_mission(draft.mission_id)

            # Key outputs to assert replay determinism
            state_details = app.get_mission_details(draft.mission_id)
            return (
                draft.mission_id,
                plan.plan_snapshot_id,
                len(app.get_event_history()),
                state_details["robot_locomotion"],
            )

        assert run_mnt() == run_mnt()
