"""Verification script for the Types layer."""
import sys
sys.path.insert(0, "src")

# 1. ids
from domain_types.ids import MissionId, RobotId, EventId, OperatorId, RequestId
print("ids OK")

# 2. common
from domain_types.common import Pose3D, Priority, TimestampMs, CommunicationStatus
print("common OK")

# 3. mission
from domain_types.mission import (
    SearchAreaType, SearchMethod, MissionStatus,
    SearchArea, SearchMissionRequest, MissionDraft,
    SearchMissionPlan, MissionSetupRecommendation,
)
print("mission OK")

# 4. terrain
from domain_types.terrain import (
    TerrainClass, TraversabilityLevel, LocomotionMode,
    TerrainAnalysisResult, LocomotionDecision, SearchDriveProfile,
)
print("terrain OK")

# 5. validation
from domain_types.validation import ValidationError, ValidationResult
print("validation OK")

# 6. events
from domain_types.events import BaseEvent, EventPriority, EventType
print("events OK")

# 7. protocols
from domain_types.protocols import (
    IDetector, ISlamEngine, ITerrainAnalyzer, ISearchDrivePolicy,
    INavigationEngine, IRobotController, IEventRepository,
    IMissionCreationService, IMissionRepository,
    ISopMissionConfigurator, ISopAgent,
)
print("protocols OK")

# 8. Smoke-test instantiation
pose = Pose3D(x=1.0, y=2.0, z=3.0, roll=0.0, pitch=0.0, yaw=0.0)
area = SearchArea(
    area_type=SearchAreaType.POLYGON,
    coordinates=(pose,),
    frame_id="map",
)
req = SearchMissionRequest(
    request_id="r1", operator_id="op1", mission_name="Test",
    search_area=area, search_method=SearchMethod.AREA_SWEEP,
    sop_profile_id="sop1", priority="HIGH", created_at_ms=1000,
)
draft = MissionDraft(
    mission_id="m1", request=req, validation_status="VALID",
    sop_constraints={}, draft_snapshot_id="snap1",
)
evt = BaseEvent(
    event_id="e1", mission_id="m1", robot_id="r1",
    event_type=EventType.SEARCH_MISSION_CREATED,
    timestamp_ms=1000, source_module="test",
)
terrain = TerrainAnalysisResult(
    terrain_class=TerrainClass.FLAT_OPEN, slope_degree=5.0,
    step_height_cm=2.0, roughness_score=0.1, obstacle_density=0.05,
    traversability_score=0.9, traversability_level=TraversabilityLevel.PASSABLE,
    traversable=True,
)
vr = ValidationResult(
    is_valid=True, errors=(),
)
print("instantiation OK")

# Verify frozen
try:
    pose.x = 99.0  # type: ignore[misc]
    print("FAIL: frozen not enforced")
except AttributeError:
    print("frozen OK")

print("\n=== All types imported and verified successfully ===")
