"""TC-MISSION-005: Mission approval guard tests."""

from __future__ import annotations

import pytest

from domain_types.common import Pose3D
from domain_types.mission import (
    MissionDraft,
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionRequest,
)
from service.mission_approval_guard import approve_mission


def _make_request() -> SearchMissionRequest:
    return SearchMissionRequest(
        request_id="REQ-001",
        operator_id="OP-001",
        mission_name="테스트 임무",
        search_area=SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(
                Pose3D(0, 0, 0, 0, 0, 0),
                Pose3D(1, 0, 0, 0, 0, 0),
                Pose3D(1, 1, 0, 0, 0, 0),
            ),
            frame_id="map",
        ),
        search_method=SearchMethod.PARALLEL_SWEEP,
        sop_profile_id="mountain_missing_person",
        priority="HIGH",
        created_at_ms=1700000000000,
    )


class TestMissionApprovalGuard:
    def test_approve_pending_approval_succeeds(self) -> None:
        draft = MissionDraft(
            mission_id="M-000001",
            request=_make_request(),
            validation_status="PENDING_APPROVAL",
        )
        plan = approve_mission(
            draft=draft,
            approved_by="CMDR-001",
            approved_at_ms=1700000001000,
            plan_snapshot_id="PLAN-SNAP-001",
        )
        assert plan.mission_id == "M-000001"
        assert plan.approved_by == "CMDR-001"
        assert plan.search_method == SearchMethod.PARALLEL_SWEEP

    def test_approve_draft_status_raises(self) -> None:
        draft = MissionDraft(
            mission_id="M-000002",
            request=_make_request(),
            validation_status="DRAFT",
        )
        with pytest.raises(ValueError, match="PENDING_APPROVAL"):
            approve_mission(draft, "CMDR-001", 1700000001000, "SNAP")

    def test_approve_cancelled_status_raises(self) -> None:
        draft = MissionDraft(
            mission_id="M-000003",
            request=_make_request(),
            validation_status="CANCELLED",
        )
        with pytest.raises(ValueError):
            approve_mission(draft, "CMDR-001", 1700000001000, "SNAP")
