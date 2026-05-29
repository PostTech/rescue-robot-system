"""TC-FUNC-BND-010: Mission types — instantiation, frozen, boundary validation."""

from __future__ import annotations

import pytest

from domain_types.common import Pose3D
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

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_pose() -> Pose3D:
    return Pose3D(x=37.5, y=127.0, z=10.0, roll=0.0, pitch=0.0, yaw=1.57)


@pytest.fixture()
def sample_area(sample_pose: Pose3D) -> SearchArea:
    return SearchArea(
        area_type=SearchAreaType.POLYGON,
        coordinates=(sample_pose,),
        frame_id="map",
    )


@pytest.fixture()
def sample_request(sample_area: SearchArea) -> SearchMissionRequest:
    return SearchMissionRequest(
        request_id="REQ-001",
        operator_id="OP-001",
        mission_name="산악 수색",
        search_area=sample_area,
        search_method=SearchMethod.PARALLEL_SWEEP,
        sop_profile_id="SOP-DEFAULT",
        priority="HIGH",
        created_at_ms=1700000000000,
    )


# ---------------------------------------------------------------------------
# SearchAreaType enum
# ---------------------------------------------------------------------------


class TestSearchAreaType:
    def test_has_all_members(self) -> None:
        expected = {"POLYGON", "WAYPOINT_ROUTE", "GRID", "GEOFENCE"}
        assert {m.value for m in SearchAreaType} == expected

    def test_str_value(self) -> None:
        assert str(SearchAreaType.POLYGON) == "POLYGON"


# ---------------------------------------------------------------------------
# SearchMethod enum
# ---------------------------------------------------------------------------


class TestSearchMethod:
    def test_has_15_methods(self) -> None:
        assert len(SearchMethod) == 15

    def test_manual_assisted_exists(self) -> None:
        assert SearchMethod.MANUAL_ASSISTED == "MANUAL_ASSISTED"


# ---------------------------------------------------------------------------
# MissionStatus enum
# ---------------------------------------------------------------------------


class TestMissionStatus:
    def test_lifecycle_states(self) -> None:
        expected = {
            "DRAFT",
            "VALIDATING",
            "PENDING_APPROVAL",
            "APPROVED",
            "ACTIVE",
            "COMPLETED",
            "CANCELLED",
        }
        assert {m.value for m in MissionStatus} == expected


# ---------------------------------------------------------------------------
# SearchArea
# ---------------------------------------------------------------------------


class TestSearchArea:
    def test_creation(self, sample_area: SearchArea) -> None:
        assert sample_area.area_type == SearchAreaType.POLYGON
        assert len(sample_area.coordinates) == 1
        assert sample_area.frame_id == "map"

    def test_frozen(self, sample_area: SearchArea) -> None:
        with pytest.raises(AttributeError):
            sample_area.frame_id = "odom"

    def test_default_metadata(self, sample_pose: Pose3D) -> None:
        area = SearchArea(
            area_type=SearchAreaType.GRID,
            coordinates=(sample_pose,),
            frame_id="map",
        )
        assert area.metadata == {}

    def test_empty_coordinates_allowed(self) -> None:
        """TC-FUNC-BND-010: 빈 좌표 입력 허용 (검증은 Service 책임)."""
        area = SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(),
            frame_id="map",
        )
        assert len(area.coordinates) == 0


# ---------------------------------------------------------------------------
# SearchMissionRequest
# ---------------------------------------------------------------------------


class TestSearchMissionRequest:
    def test_creation(self, sample_request: SearchMissionRequest) -> None:
        assert sample_request.request_id == "REQ-001"
        assert sample_request.search_method == SearchMethod.PARALLEL_SWEEP

    def test_frozen(self, sample_request: SearchMissionRequest) -> None:
        with pytest.raises(AttributeError):
            sample_request.priority = "LOW"


# ---------------------------------------------------------------------------
# MissionDraft
# ---------------------------------------------------------------------------


class TestMissionDraft:
    def test_creation_with_defaults(self, sample_request: SearchMissionRequest) -> None:
        draft = MissionDraft(
            mission_id="M-001",
            request=sample_request,
            validation_status="VALIDATING",
        )
        assert draft.sop_constraints == {}
        assert draft.draft_snapshot_id == ""

    def test_frozen(self, sample_request: SearchMissionRequest) -> None:
        draft = MissionDraft(
            mission_id="M-001",
            request=sample_request,
            validation_status="DRAFT",
        )
        with pytest.raises(AttributeError):
            draft.mission_id = "M-999"


# ---------------------------------------------------------------------------
# SearchMissionPlan
# ---------------------------------------------------------------------------


class TestSearchMissionPlan:
    def test_creation(self, sample_area: SearchArea) -> None:
        plan = SearchMissionPlan(
            mission_id="M-001",
            search_area=sample_area,
            search_method=SearchMethod.CONTOUR_SEARCH,
            approved_by="CMDR-001",
            approved_at_ms=1700000001000,
            plan_snapshot_id="SNAP-001",
        )
        assert plan.approved_by == "CMDR-001"


# ---------------------------------------------------------------------------
# MissionSetupRecommendation
# ---------------------------------------------------------------------------


class TestMissionSetupRecommendation:
    def test_recommendation_only_default(self) -> None:
        rec = MissionSetupRecommendation(
            recommended_method=SearchMethod.EXPANDING_SQUARE,
        )
        assert rec.recommendation_only is True
        assert rec.warnings == ()
        assert rec.constraints == {}

    def test_with_warnings(self) -> None:
        rec = MissionSetupRecommendation(
            recommended_method=SearchMethod.SECTOR_SEARCH,
            warnings=("경사 지형 주의", "진입 금지 구역 근접"),
        )
        assert len(rec.warnings) == 2
