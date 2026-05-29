"""Application service — top-level orchestrator.

Wires all components via dependency injection and manages the
full mission lifecycle: Create -> Validate -> Approve -> Execute -> Complete.

No ROS/rclpy, real network, or external DB dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapters.storage.in_memory_mission_repository import InMemoryMissionRepository
from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.core.protocols import IMissionRepository
from domain_types.events import BaseEvent, EventType
from domain_types.mission import (
    MissionDraft,
    MissionSetupRecommendation,
    SearchMethod,
    SearchMissionPlan,
    SearchMissionRequest,
)
from domain_types.terrain import TerrainAnalysisResult
from service.event_bus import EventBus
from service.fusion_logic import VictimDecision, fuse_detections
from service.mission_approval_guard import approve_mission
from service.mission_creation_service import MissionCreationService
from service.mission_state_machine import MissionState, MissionStateMachine
from service.mock_detector import DetectionLabel, DetectionResult
from service.mock_robot_controller import MockRobotController, RobotCommand
from service.safety_manager import SafetyManager
from service.search_drive_policy import decide_drive_profile
from service.terrain_analyzer import analyze_terrain


class MockSopConfigurator:
    """Mock SOP Configurator returning realistic recommendations based on SOP Profile ID."""

    def apply_profile(self, request: SearchMissionRequest) -> MissionSetupRecommendation:
        profile_id = request.sop_profile_id
        if profile_id == "mountain_missing_person":
            return MissionSetupRecommendation(
                recommended_method=SearchMethod.GRID_COVERAGE,
                constraints={
                    "max_slope_deg": 25.0,
                    "max_roughness": 0.4,
                    "battery_reserve_pct": 20.0,
                    "safety_factor": 1.2,
                },
                warnings=("산악 경사지 및 수풀 우거짐 주의", "고도 급변 구역 존재"),
            )
        elif profile_id == "collapsed_structure":
            return MissionSetupRecommendation(
                recommended_method=SearchMethod.PARALLEL_SWEEP,
                constraints={
                    "max_obstacle_density": 0.6,
                    "max_step_height_cm": 15.0,
                    "battery_reserve_pct": 30.0,
                    "safety_factor": 1.5,
                },
                warnings=("붕괴 파편 및 잔해 집중 구역", "공동(Void) 붕괴 위험성 높음"),
            )
        elif profile_id == "flooded_tunnel":
            return MissionSetupRecommendation(
                recommended_method=SearchMethod.CONTOUR_SEARCH,
                constraints={
                    "max_water_depth_cm": 10.0,
                    "max_slope_deg": 15.0,
                    "battery_reserve_pct": 25.0,
                    "safety_factor": 1.4,
                },
                warnings=("침수 심화 및 통신 음영 발생 우려", "벽면 붕괴 위험 감시 요망"),
            )
        else:
            return MissionSetupRecommendation(
                recommended_method=request.search_method,
                constraints={
                    "battery_reserve_pct": 15.0,
                    "safety_factor": 1.0,
                },
                warnings=("기본 안전 SOP 가이드라인 준수",),
            )


@dataclass
class MissionContext:
    """Runtime context for an active mission."""

    mission_id: str
    request: SearchMissionRequest
    draft: MissionDraft
    plan: SearchMissionPlan | None = None
    state_machine: MissionStateMachine = field(default_factory=MissionStateMachine)
    terrain_results: list[TerrainAnalysisResult] = field(default_factory=list)
    detections: list[VictimDecision] = field(default_factory=list)
    map_coverage_ratio: float = 0.0
    current_pose: Pose3D = field(default_factory=lambda: Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))


class ApplicationService:
    """Top-level orchestrator for the rescue robot system.

    Manages the full lifecycle using dependency-injected components.
    """

    def __init__(
        self,
        clock: FakeClock,
        id_gen: DeterministicIdGenerator,
        robot_controller: MockRobotController | None = None,
    ) -> None:
        self._clock: FakeClock = clock
        self._id_gen: DeterministicIdGenerator = id_gen
        self._event_bus: EventBus = EventBus()
        self._safety: SafetyManager = SafetyManager()
        self._robot: MockRobotController = robot_controller or MockRobotController()
        self._repo: IMissionRepository = InMemoryMissionRepository()
        self._creation_service: MissionCreationService = MissionCreationService(
            clock=clock,
            id_gen=id_gen,
            mission_repo=self._repo,
            sop_configurator=MockSopConfigurator(),
        )
        self._missions: dict[str, MissionContext] = {}

        # Wire safety manager to event bus
        self._event_bus.subscribe_all(self._on_event)

    # ── Mission Creation ──────────────────────────────────────────

    def create_mission(self, request: SearchMissionRequest) -> MissionDraft:
        """Create a new mission draft from an operator request."""
        draft = self._creation_service.create_draft(request)

        ctx = MissionContext(
            mission_id=draft.mission_id,
            request=request,
            draft=draft,
        )
        self._missions[draft.mission_id] = ctx

        self._clock.advance(1)
        self._publish(EventType.SEARCH_MISSION_CREATED, draft.mission_id)
        return draft

    # ── Mission Approval ──────────────────────────────────────────

    def approve_mission(self, mission_id: str, approver: str) -> SearchMissionPlan:
        """Approve a mission draft and create a plan.

        Raises:
            ValueError: If mission not found or draft not PENDING_APPROVAL.
        """
        ctx = self._get_context(mission_id)
        ctx.state_machine.transition(MissionState.PENDING_APPROVAL)

        self._clock.advance(1)
        plan_snapshot_id = f"PLAN-{mission_id}-{self._clock.now_ms()}"

        plan = approve_mission(
            draft=ctx.draft,
            approved_by=approver,
            approved_at_ms=self._clock.now_ms(),
            plan_snapshot_id=plan_snapshot_id,
        )
        self._repo.save_plan(plan)
        ctx.plan = plan

        ctx.state_machine.transition(MissionState.APPROVED)
        self._publish(EventType.MISSION_APPROVAL_REQUESTED, mission_id)
        return plan

    # ── Mission Execution ─────────────────────────────────────────

    def start_mission(self, mission_id: str) -> MissionState:
        """Start executing an approved mission."""
        ctx = self._get_context(mission_id)
        ctx.state_machine.transition(MissionState.ACTIVE)
        return ctx.state_machine.state

    def process_terrain(
        self,
        mission_id: str,
        slope: float,
        step_height: float,
        roughness: float,
        obstacle_density: float,
        traversability: float,
    ) -> TerrainAnalysisResult:
        """Process terrain data during mission execution."""
        ctx = self._get_context(mission_id)
        result = analyze_terrain(slope, step_height, roughness, obstacle_density, traversability)
        ctx.terrain_results.append(result)

        profile = decide_drive_profile(result, ctx.request.search_method)
        self._robot.set_locomotion(profile.locomotion_mode, self._clock.now_ms())

        self._clock.advance(1)
        self._publish(EventType.TERRAIN_ANALYZED, mission_id)
        return result

    def process_detections(
        self,
        mission_id: str,
        results: list[DetectionResult],
        confidence_threshold: float = 0.5,
    ) -> VictimDecision:
        """Process sensor detections and produce a fused decision."""
        ctx = self._get_context(mission_id)
        decision = fuse_detections(results, confidence_threshold)
        ctx.detections.append(decision)
        return decision

    # ── Mission Completion ────────────────────────────────────────

    def complete_mission(self, mission_id: str) -> MissionState:
        """Mark a mission as completed."""
        ctx = self._get_context(mission_id)
        ctx.state_machine.transition(MissionState.COMPLETED)
        return ctx.state_machine.state

    def abort_mission(self, mission_id: str) -> MissionState:
        """Abort a mission."""
        ctx = self._get_context(mission_id)
        ctx.state_machine.transition(MissionState.ABORTED)
        return ctx.state_machine.state

    # ── Safety ────────────────────────────────────────────────────

    def emergency_stop(self, mission_id: str) -> MissionState:
        """Trigger emergency stop for a mission."""
        ctx = self._get_context(mission_id)
        self._robot.execute(RobotCommand.EMERGENCY_STOP, self._clock.now_ms())
        self._clock.advance(1)
        self._publish(EventType.EMERGENCY_STOP, mission_id)
        ctx.state_machine.emergency_stop()
        return ctx.state_machine.state

    # ── Query ─────────────────────────────────────────────────────

    def get_mission_state(self, mission_id: str) -> MissionState:
        return self._get_context(mission_id).state_machine.state

    def get_mission_context(self, mission_id: str) -> MissionContext:
        return self._get_context(mission_id)

    def get_event_history(self) -> list[BaseEvent]:
        from typing import cast

        return cast(list[BaseEvent], self._event_bus.get_history())

    def get_available_sop_profiles(self) -> list[dict[str, str]]:
        """Get the list of active SOP profiles for selection."""
        return [
            {"id": "mountain_missing_person", "name": "산악 실종자 수색"},
            {"id": "collapsed_structure", "name": "붕괴 건물 인명 구조"},
            {"id": "flooded_tunnel", "name": "침수 터널 탐색"},
        ]

    def get_all_missions(self) -> list[MissionContext]:
        """Get all mission contexts."""
        return list(self._missions.values())

    def get_mission_summary_list(self) -> list[dict[str, Any]]:
        """Get summarized list of all missions for the dashboard."""
        summaries = []
        for ctx in self._missions.values():
            victim_count = sum(1 for d in ctx.detections if d.detected)
            summaries.append(
                {
                    "mission_id": ctx.mission_id,
                    "name": ctx.request.mission_name,
                    "status": ctx.state_machine.state,
                    "priority": ctx.request.priority,
                    "sop_profile_id": ctx.request.sop_profile_id,
                    "created_at_ms": ctx.request.created_at_ms,
                    "map_coverage_ratio": ctx.map_coverage_ratio,
                    "victim_count": victim_count,
                }
            )
        return summaries

    def get_mission_details(self, mission_id: str) -> dict[str, Any]:
        """Get detailed breakdown of a single mission context for UI display."""
        ctx = self._get_context(mission_id)

        coords = []
        if ctx.request.search_area and ctx.request.search_area.coordinates:
            for c in ctx.request.search_area.coordinates:
                coords.append({"x": c.x, "y": c.y, "z": c.z})

        detections_list = []
        for d in ctx.detections:
            detections_list.append(
                {
                    "detected": d.detected,
                    "confidence": d.confidence,
                    "label": d.label,
                    "primary_sensor": d.primary_sensor,
                    "decision_level": d.decision_level.value,
                }
            )

        terrain_list = []
        for t in ctx.terrain_results:
            terrain_list.append(
                {
                    "slope": t.slope_degree,
                    "step_height": t.step_height_cm,
                    "roughness": t.roughness_score,
                    "obstacle_density": t.obstacle_density,
                    "traversability": t.traversability_score,
                    "traversability_level": t.traversability_level.value,
                    "traversable": t.traversable,
                }
            )

        constraints = ctx.draft.sop_constraints if ctx.draft else {}

        commands = []
        for cmd in self._robot.get_command_history():
            commands.append(
                {
                    "command": cmd.command,
                    "success": cmd.success,
                    "locomotion_mode": cmd.locomotion_mode,
                    "timestamp_ms": cmd.timestamp_ms,
                    "error": cmd.error,
                }
            )

        return {
            "mission_id": ctx.mission_id,
            "name": ctx.request.mission_name,
            "status": ctx.state_machine.state,
            "priority": ctx.request.priority,
            "sop_profile_id": ctx.request.sop_profile_id,
            "created_at_ms": ctx.request.created_at_ms,
            "search_method": ctx.request.search_method,
            "search_area": {
                "area_type": ctx.request.search_area.area_type,
                "coordinates": coords,
                "frame_id": ctx.request.search_area.frame_id,
            },
            "sop_constraints": constraints,
            "map_coverage_ratio": ctx.map_coverage_ratio,
            "current_pose": {
                "x": ctx.current_pose.x,
                "y": ctx.current_pose.y,
                "z": ctx.current_pose.z,
                "roll": ctx.current_pose.roll,
                "pitch": ctx.current_pose.pitch,
                "yaw": ctx.current_pose.yaw,
            },
            "terrain_results": terrain_list,
            "detections": detections_list,
            "robot_locomotion": self._robot.locomotion_mode,
            "robot_emergency_stopped": self._robot.is_emergency_stopped,
            "commands": commands,
        }

    def tick_mission(self, mission_id: str) -> dict[str, Any]:
        """Advance the active mission by one simulation step (Tick).

        Automatically handles state transitions, SLAM updates, virtual terrain detection,
        locomotion adjustments, and target searching.
        """
        ctx = self._get_context(mission_id)
        state = ctx.state_machine.state

        if state == MissionState.DRAFT:
            self.approve_mission(mission_id, "SYSTEM_AUTO")
            self._clock.advance(1)

        elif state == MissionState.APPROVED:
            self.start_mission(mission_id)
            self._clock.advance(1)

        elif state == MissionState.ACTIVE:
            self._clock.advance(100)  # advance clock by 100ms
            now = self._clock.now_ms()

            ctx.map_coverage_ratio = round(min(1.0, ctx.map_coverage_ratio + 0.1), 2)

            # Spiral path simulation
            angle = ctx.map_coverage_ratio * 4 * 3.14159
            radius = ctx.map_coverage_ratio * 15.0
            ctx.current_pose = Pose3D(
                x=round(radius * float(abs(angle % 2 - 1)), 2),
                y=round(radius * float(abs((angle + 1.57) % 2 - 1)), 2),
                z=0.0,
                roll=0.0,
                pitch=0.0,
                yaw=round(angle, 2),
            )

            # Simulate terrain challenges
            slope = 5.0
            roughness = 0.05
            obstacle = 0.05
            if 0.28 <= ctx.map_coverage_ratio <= 0.35:
                slope = 28.0
                roughness = 0.2
            elif 0.65 <= ctx.map_coverage_ratio <= 0.75:
                slope = 10.0
                roughness = 0.45
                obstacle = 0.35

            self.process_terrain(
                mission_id=mission_id,
                slope=slope,
                step_height=slope / 5.0,
                roughness=roughness,
                obstacle_density=obstacle,
                traversability=1.0 - (slope / 90.0) - (roughness * 0.5),
            )

            # Simulate victim detections at 40% and 80% coverage
            if abs(ctx.map_coverage_ratio - 0.4) < 0.02 or abs(ctx.map_coverage_ratio - 0.8) < 0.02:
                det = DetectionResult(
                    sensor_type="THERMAL",
                    label=DetectionLabel.VICTIM_ALIVE,
                    confidence=0.92,
                    bounding_box=(100, 150, 50, 50),
                    timestamp_ms=now,
                )
                self.process_detections(mission_id, [det])

            # Auto-complete
            if ctx.map_coverage_ratio >= 1.0:
                self.complete_mission(mission_id)
                self._clock.advance(1)

        return self.get_mission_details(mission_id)

    # ── Internals ─────────────────────────────────────────────────

    def _get_context(self, mission_id: str) -> MissionContext:
        ctx = self._missions.get(mission_id)
        if ctx is None:
            raise ValueError(f"Mission not found: {mission_id}")
        return ctx

    def _publish(self, event_type: str, mission_id: str) -> None:
        evt = BaseEvent(
            event_id=self._id_gen.next(),
            mission_id=mission_id,
            robot_id="R-001",
            event_type=event_type,
            timestamp_ms=self._clock.now_ms(),
            source_module="application_service",
        )
        self._event_bus.publish(evt)

    def _on_event(self, event: BaseEvent) -> None:
        """Global event handler — routes safety events."""
        self._safety.handle_event(event)

    @property
    def event_bus(self) -> EventBus:
        """Expose EventBus for external subscription gateways."""
        return self._event_bus
