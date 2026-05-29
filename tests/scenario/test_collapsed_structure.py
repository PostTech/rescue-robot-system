"""End-to-End: Collapsed structure SAR SOP scenario (TC-SCENARIO-002)."""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.events import BaseEvent, EventPriority, EventType
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
from service.safety_manager import SafetyLevel


class TestCollapsedStructureScenario:
    def test_tc_scenario_002_collapsed_structure_gas_retreat(self) -> None:
        """TC-SCENARIO-002: Verifies collapsed rubble navigation, multi-sensor fusion, and gas safety alert."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        id_gen = DeterministicIdGenerator("M", 0)
        app = ApplicationService(clock, id_gen)

        # 1. Draft Creation with collapsed structure SOP profile
        req = SearchMissionRequest(
            request_id="REQ-COL-001",
            operator_id="OP-FIELD-COL",
            mission_name="Collapsed Void SAR Mission",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(20.0, 5.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(10.0, 15.0, 0.0, 0.0, 0.0, 0.0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.FRONTIER_EXPLORATION,
            sop_profile_id="collapsed_structure",
            priority="CRITICAL",
            created_at_ms=clock.now_ms(),
        )

        draft = app.create_mission(req)
        mid = draft.mission_id
        assert app.get_mission_state(mid) == MissionState.DRAFT

        # 2. Approve Draft
        app.approve_mission(mid, "CDR-COL")
        assert app.get_mission_state(mid) == MissionState.APPROVED

        # 3. Start Mission
        app.start_mission(mid)
        assert app.get_mission_state(mid) == MissionState.ACTIVE

        # 4. Terrain Updates: Rough rubble (collapse obstacle) encountered
        # Decides drive profile based on slope=10.0, method=FRONTIER_EXPLORATION
        # step_height=18.0 exceeds mild limit, roughness=0.8 triggers rough rubble locomotion
        terrain = app.process_terrain(
            mission_id=mid,
            slope=10.0,
            step_height=18.0,
            roughness=0.8,
            obstacle_density=0.1,
            traversability=0.3,
        )
        assert terrain.roughness_score == 0.8
        # Verification of locomotion gear adapt
        assert app._robot.locomotion_mode == LocomotionMode.OBSTACLE_CLIMB

        # 5. Multi-Sensor Fusion: Thermal + Audio sensor fusion for high confidence victim candidate
        det_thermal = DetectionResult(
            sensor_type="THERMAL",
            label=DetectionLabel.VICTIM_ALIVE,
            confidence=0.85,
            bounding_box=(150, 150, 40, 40),
            timestamp_ms=clock.now_ms(),
        )
        det_audio = DetectionResult(
            sensor_type="AUDIO",
            label=DetectionLabel.VICTIM_ALIVE,
            confidence=0.72,
            bounding_box=(0, 0, 0, 0),
            timestamp_ms=clock.now_ms(),
        )

        # Process detections with 0.5 threshold
        decision = app.process_detections(mid, [det_thermal, det_audio], confidence_threshold=0.5)
        assert decision.detected is True
        assert decision.confidence >= 0.85  # Fusion increases/maintains high confidence
        assert decision.primary_sensor == "THERMAL"

        # 6. Gas Hazard Event: High toxic CO2 gas detected
        # Generates retreat safety triggers in SafetyManager
        gas_event = BaseEvent(
            event_id="EVT-GAS-001",
            mission_id=mid,
            robot_id="R-001",
            event_type=EventType.GAS_HAZARD,
            timestamp_ms=clock.now_ms(),
            source_module="SafetySystem",
            priority=EventPriority.CRITICAL,
            payload={"gas_type": "CO2", "value": 5500.0, "threshold": 5000.0},
        )
        app.event_bus.publish(gas_event)

        # 7. Safety Retreat Verification
        safety_state = app._safety.state
        assert safety_state.gas_alert_active is True
        assert safety_state.level == SafetyLevel.SAFE_MODE
        # Safety manager demands robot retreat mode (STOP_AND_REPLAN)
        assert safety_state.recommended_locomotion == LocomotionMode.STOP_AND_REPLAN
