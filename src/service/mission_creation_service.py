"""Mission Creation Service.

Orchestrates the full mission creation flow:
    Request → Validate → Draft → (SOP Recommend) → Pending Approval

All external dependencies are injected via Protocol interfaces.
"""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.aiagent.protocols import ISopMissionConfigurator
from domain_types.core.protocols import IMissionRepository
from domain_types.mission import (
    MissionDraft,
    SearchMissionRequest,
)
from service.search_area_validator import validate_search_area
from service.search_method_policy import validate_search_method


class MissionCreationService:
    """Creates and validates mission drafts.

    Dependencies are injected — no direct DB, ROS, or UI access.
    """

    def __init__(
        self,
        clock: FakeClock,
        id_gen: DeterministicIdGenerator,
        mission_repo: IMissionRepository,
        sop_configurator: ISopMissionConfigurator | None = None,
    ) -> None:
        self._clock = clock
        self._id_gen = id_gen
        self._mission_repo = mission_repo
        self._sop_configurator = sop_configurator

    def create_draft(
        self,
        request: SearchMissionRequest,
        terrain_class: str = "",
    ) -> MissionDraft:
        """Validate a request and produce a MissionDraft.

        Args:
            request: The operator's search mission request.
            terrain_class: Optional terrain classification for method validation.

        Returns:
            A MissionDraft ready for SOP recommendation and approval.

        Raises:
            ValueError: If the request fails validation.
        """
        # 1. Validate SearchArea
        area_result = validate_search_area(request.search_area)
        if not area_result.is_valid:
            raise ValueError(
                f"SearchArea validation failed: {[e.message for e in area_result.errors]}"
            )

        # 2. Validate SearchMethod compatibility (if terrain provided)
        if terrain_class:
            method_result = validate_search_method(request.search_method, terrain_class)
            if not method_result.is_valid:
                raise ValueError(
                    f"SearchMethod validation failed: {[e.message for e in method_result.errors]}"
                )

        # 3. Build draft
        mission_id = self._id_gen.next()
        draft_snapshot_id = f"SNAP-{mission_id}-{self._clock.now_ms()}"

        # 4. Apply SOP recommendation if available
        sop_constraints: dict[str, object] = {}
        if self._sop_configurator is not None:
            recommendation = self._sop_configurator.apply_profile(request)
            sop_constraints = dict(recommendation.constraints)

        draft = MissionDraft(
            mission_id=mission_id,
            request=request,
            validation_status="PENDING_APPROVAL",
            sop_constraints=sop_constraints,
            draft_snapshot_id=draft_snapshot_id,
        )

        # 5. Persist
        self._mission_repo.save_draft(draft)

        return draft
