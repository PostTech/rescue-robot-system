"""End-to-End: Tunnel flooded gas risk emergency stop SOP scenario (TC-SCENARIO-003)."""

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
from service.safety_manager import SafetyLevel


class TestTunnelGasRiskScenario:
    def test_tc_scenario_003_tunnel_gas_emergency_stop(self) -> None:
        """TC-SCENARIO-003: Verifies narrow passage navigation and emergency stop safety shutdown on gas overflow."""
        clock = FakeClock(base_ms=1_700_000_000_000)
        id_gen = DeterministicIdGenerator("M", 0)
        app = ApplicationService(clock, id_gen)

        # 1. Draft Creation with flooded tunnel SOP profile
        req = SearchMissionRequest(
            request_id="REQ-TNL-001",
            operator_id="OP-FIELD-TNL",
            mission_name="Flooded Tunnel Search Mission",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(30.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(30.0, 10.0, 0.0, 0.0, 0.0, 0.0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.SINGLE_FILE,
            sop_profile_id="flooded_tunnel",
            priority="CRITICAL",
            created_at_ms=clock.now_ms(),
        )

        draft = app.create_mission(req)
        mid = draft.mission_id
        assert app.get_mission_state(mid) == MissionState.DRAFT

        # 2. Approve Draft
        app.approve_mission(mid, "CDR-TNL")
        assert app.get_mission_state(mid) == MissionState.APPROVED

        # 3. Start Mission
        app.start_mission(mid)
        assert app.get_mission_state(mid) == MissionState.ACTIVE

        # 4. Terrain Updates: Narrow flooded passage encountered
        # Decides drive profile based on slope=2.0, method=SINGLE_FILE
        # step_height=1.0, roughness=0.05, obstacle_density=0.1
        terrain = app.process_terrain(
            mission_id=mid,
            slope=2.0,
            step_height=1.0,
            roughness=0.05,
            obstacle_density=0.1,
            traversability=0.8,
        )
        assert terrain.slope_degree == 2.0
        # Adapt locomotion mode to wheels (Normal speed in narrow tunnels)
        assert app._robot.locomotion_mode == LocomotionMode.WHEEL

        # 5. CO2 toxic gas level exceeds safe operation limit
        # Generates immediate EMERGENCY_STOP event and robot shutdown
        estop_event = BaseEvent(
            event_id="EVT-ESTOP-001",
            mission_id=mid,
            robot_id="R-001",
            event_type=EventType.EMERGENCY_STOP,
            timestamp_ms=clock.now_ms(),
            source_module="SafetySystem",
            priority=EventPriority.CRITICAL,
            payload={
                "gas_type": "CO2",
                "value": 6500.0,
                "threshold": 5000.0,
                "reason": "CO2 level overflow",
            },
        )
        app.event_bus.publish(estop_event)

        # Trigger application service emergency stop routing
        app.emergency_stop(mid)

        # 6. Safety Shutdown Validation
        safety_state = app._safety.state
        assert safety_state.emergency_stopped is True
        assert safety_state.level == SafetyLevel.EMERGENCY_STOP

        # Verify robot hardware state has been physically shutdown
        assert app._robot.is_emergency_stopped is True
        assert app._robot.locomotion_mode == LocomotionMode.STOP_AND_REPLAN

        # Verify mission control state transitions to EMERGENCY_STOPPED
        assert app.get_mission_state(mid) == MissionState.EMERGENCY_STOPPED

    def test_tc_scenario_004_tunnel_determinism(self) -> None:
        """TC-SCENARIO-004: Validates same inputs yield identical E-STOP outputs (Replay)."""

        def run_tnl() -> tuple[str, str, int, bool]:
            clock = FakeClock(base_ms=1_700_000_000_000)
            id_gen = DeterministicIdGenerator("M", 0)
            app = ApplicationService(clock, id_gen)

            req = SearchMissionRequest(
                request_id="REQ-DET-TNL",
                operator_id="OP-DET",
                mission_name="Det Tunnel",
                search_area=SearchArea(
                    area_type=SearchAreaType.POLYGON,
                    coordinates=(
                        Pose3D(0, 0, 0, 0, 0, 0),
                        Pose3D(10, 0, 0, 0, 0, 0),
                        Pose3D(10, 10, 0, 0, 0, 0),
                    ),
                    frame_id="map",
                ),
                search_method=SearchMethod.SINGLE_FILE,
                sop_profile_id="flooded_tunnel",
                priority="CRITICAL",
                created_at_ms=clock.now_ms(),
            )
            draft = app.create_mission(req)
            app.approve_mission(draft.mission_id, "CDR")
            app.start_mission(draft.mission_id)
            app.process_terrain(draft.mission_id, 2.0, 1.0, 0.05, 0.1, 0.8)

            # Publish E-STOP
            estop_event = BaseEvent(
                event_id="EVT-ESTOP-001",
                mission_id=draft.mission_id,
                robot_id="R-001",
                event_type=EventType.EMERGENCY_STOP,
                timestamp_ms=clock.now_ms(),
                source_module="SafetySystem",
                priority=EventPriority.CRITICAL,
                payload={"reason": "CO2 overflow"},
            )
            app.event_bus.publish(estop_event)
            app.emergency_stop(draft.mission_id)

            state_details = app.get_mission_details(draft.mission_id)
            return (
                draft.mission_id,
                state_details["status"],
                len(app.get_event_history()),
                state_details["robot_emergency_stopped"],
            )

        assert run_tnl() == run_tnl()
