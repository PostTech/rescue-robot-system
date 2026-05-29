"""Mission setup ViewModel.

Bridges Operator UI input to Service layer.
No direct DB, ROS, Robot SDK, or Storage access.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain_types.common import Pose3D
from domain_types.core.protocols import IMissionCreationService
from domain_types.mission import (
    MissionDraft,
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionPlan,
    SearchMissionRequest,
)


@dataclass
class MissionSetupState:
    """Observable state for the mission setup UI."""

    area_type: SearchAreaType | None = None
    coordinates: list[Pose3D] | None = None
    frame_id: str = "map"
    search_method: SearchMethod | None = None
    sop_profile_id: str = ""
    mission_name: str = ""
    priority: str = "NORMAL"
    draft: MissionDraft | None = None
    plan: SearchMissionPlan | None = None
    error_message: str = ""


class MissionSetupViewModel:
    """ViewModel for the mission setup screen.

    Converts operator inputs into SearchMissionRequest
    and delegates to MissionCreationService.
    """

    def __init__(
        self,
        service: IMissionCreationService,
        operator_id: str,
        request_id_generator: object,
        clock: object,
    ) -> None:
        self._service = service
        self._operator_id = operator_id
        self._request_id_gen = request_id_generator
        self._clock = clock
        self.state = MissionSetupState()

    def set_area(
        self,
        area_type: SearchAreaType,
        coordinates: list[Pose3D],
        frame_id: str = "map",
    ) -> None:
        """Update the search area selection."""
        self.state.area_type = area_type
        self.state.coordinates = coordinates
        self.state.frame_id = frame_id

    def set_search_method(self, method: SearchMethod) -> None:
        """Update the search method selection."""
        self.state.search_method = method

    def set_sop_profile(self, profile_id: str) -> None:
        """Update the SOP profile selection."""
        self.state.sop_profile_id = profile_id

    def set_mission_name(self, name: str) -> None:
        """Update the mission name."""
        self.state.mission_name = name

    def set_priority(self, priority: str) -> None:
        """Update the mission priority."""
        self.state.priority = priority

    def submit(self) -> MissionDraft | None:
        """Build a request from current state and submit to service.

        Returns the created draft, or None if validation fails.
        """
        if not self.state.area_type or not self.state.coordinates or not self.state.search_method:
            self.state.error_message = "area_type, coordinates, search_method are required"
            return None

        request = SearchMissionRequest(
            request_id=getattr(self._request_id_gen, "next", lambda: "REQ-000001")(),
            operator_id=self._operator_id,
            mission_name=self.state.mission_name,
            search_area=SearchArea(
                area_type=self.state.area_type,
                coordinates=tuple(self.state.coordinates),
                frame_id=self.state.frame_id,
            ),
            search_method=self.state.search_method,
            sop_profile_id=self.state.sop_profile_id,
            priority=self.state.priority,
            created_at_ms=getattr(self._clock, "now_ms", lambda: 0)(),
        )

        try:
            draft = self._service.create_draft(request)
            self.state.draft = draft
            self.state.error_message = ""
            return draft
        except ValueError as e:
            self.state.error_message = str(e)
            return None
