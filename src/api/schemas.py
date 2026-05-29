"""Pydantic schemas for the REST API request/response validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from domain_types.common import Pose3D
from domain_types.mission import SearchArea, SearchAreaType, SearchMethod, SearchMissionRequest


class Pose3DModel(BaseModel):
    """3D Pose schema."""

    x: float
    y: float
    z: float
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    def to_domain(self) -> Pose3D:
        return Pose3D(self.x, self.y, self.z, self.roll, self.pitch, self.yaw)


class SearchAreaModel(BaseModel):
    """Search Area schema."""

    area_type: SearchAreaType
    coordinates: list[Pose3DModel]
    frame_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_domain(self) -> SearchArea:
        coords = tuple(c.to_domain() for c in self.coordinates)
        return SearchArea(
            area_type=self.area_type,
            coordinates=coords,
            frame_id=self.frame_id,
            metadata=self.metadata,
        )


class MissionRequestModel(BaseModel):
    """Search Mission Request schema."""

    request_id: str
    operator_id: str
    mission_name: str
    search_area: SearchAreaModel
    search_method: SearchMethod
    sop_profile_id: str
    priority: str
    created_at_ms: int

    def to_domain(self) -> SearchMissionRequest:
        return SearchMissionRequest(
            request_id=self.request_id,
            operator_id=self.operator_id,
            mission_name=self.mission_name,
            search_area=self.search_area.to_domain(),
            search_method=self.search_method,
            sop_profile_id=self.sop_profile_id,
            priority=self.priority,
            created_at_ms=self.created_at_ms,
        )


class ApproveMissionRequest(BaseModel):
    """Approve mission request body."""

    approver: str


class TerrainAnalyzeRequest(BaseModel):
    """Terrain analysis request body."""

    slope: float
    step_height: float
    roughness: float
    obstacle_density: float
    traversability: float


class DetectionItemModel(BaseModel):
    """Single detection item schema."""

    sensor_type: str
    label: str
    confidence: float
    bounding_box: tuple[float, float, float, float] | None = None
    timestamp_ms: int = 0


class DetectionAnalyzeRequest(BaseModel):
    """Detection list analysis request body."""

    results: list[DetectionItemModel]
    confidence_threshold: float = 0.5
