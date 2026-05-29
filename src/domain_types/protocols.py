"""Protocol interfaces – re-export Facade from isolated client/server packages.

Backward compatibility layer preserving the monolithic protocols location for older tests/configs.
"""

from __future__ import annotations

from domain_types.aiagent.protocols import ISopAgent, ISopMissionConfigurator
from domain_types.core.protocols import IMissionCreationService, IMissionRepository
from domain_types.db.protocols import IEventRepository, IMediaRepository
from domain_types.search.protocols import (
    INavigationEngine,
    IRobotController,
    ISearchDrivePolicy,
    ISlamEngine,
    ITerrainAnalyzer,
)
from domain_types.webrtc.protocols import IWebRTCTrackSender
from domain_types.yolo.protocols import IDetector

__all__ = [
    "IWebRTCTrackSender",
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
    "IMediaRepository",
]
