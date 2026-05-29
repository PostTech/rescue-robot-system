# Types Layer — DTO, Enum, Protocol, Value Object
# 이 계층은 Config/Service/UI를 import하지 않습니다.
"""Public re-exports for the ``types`` package.

Usage::

    from domain_types.ids import MissionId
    from domain_types.common import Pose3D, Priority
    from domain_types.mission import SearchMethod, SearchMissionRequest
    from domain_types.terrain import TerrainClass, TerrainAnalysisResult
    from domain_types.events import BaseEvent, EventType
    from domain_types.protocols import IDetector, ISlamEngine
"""

from __future__ import annotations

# --- common ---
from domain_types.common import CommunicationStatus, Pose3D, Priority, TimestampMs

# --- events ---
from domain_types.events import BaseEvent, EventPriority, EventType

# --- ids ---
from domain_types.ids import EventId, MissionId, OperatorId, RequestId, RobotId

# --- mission ---
from domain_types.mission import (
    MissionDraft,
    MissionSetupRecommendation,
    MissionStatus,
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionPlan,
    SearchMissionRequest,
)

# --- protocols ---
from domain_types.protocols import (
    IDetector,
    IEventRepository,
    IMissionCreationService,
    IMissionRepository,
    INavigationEngine,
    IRobotController,
    ISearchDrivePolicy,
    ISlamEngine,
    ISopAgent,
    ISopMissionConfigurator,
    ITerrainAnalyzer,
)

# --- terrain ---
from domain_types.terrain import (
    LocomotionDecision,
    LocomotionMode,
    SearchDriveProfile,
    TerrainAnalysisResult,
    TerrainClass,
    TraversabilityLevel,
)

# --- validation ---
from domain_types.validation import ValidationError, ValidationResult

__all__ = [
    # ids
    "MissionId",
    "RobotId",
    "EventId",
    "OperatorId",
    "RequestId",
    # common
    "TimestampMs",
    "Pose3D",
    "Priority",
    "CommunicationStatus",
    # mission
    "SearchAreaType",
    "SearchMethod",
    "MissionStatus",
    "SearchArea",
    "SearchMissionRequest",
    "MissionDraft",
    "SearchMissionPlan",
    "MissionSetupRecommendation",
    # terrain
    "TerrainClass",
    "TraversabilityLevel",
    "LocomotionMode",
    "TerrainAnalysisResult",
    "LocomotionDecision",
    "SearchDriveProfile",
    # validation
    "ValidationError",
    "ValidationResult",
    # events
    "EventPriority",
    "EventType",
    "BaseEvent",
    # protocols
    "IDetector",
    "ISlamEngine",
    "ITerrainAnalyzer",
    "ISearchDrivePolicy",
    "INavigationEngine",
    "IRobotController",
    "IEventRepository",
    "IMissionCreationService",
    "IMissionRepository",
    "ISopMissionConfigurator",
    "ISopAgent",
]
