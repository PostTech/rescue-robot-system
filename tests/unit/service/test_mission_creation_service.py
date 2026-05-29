"""TC-MISSION-001/008: MissionCreationService integration tests."""

from __future__ import annotations

import pytest

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.mission import (
    MissionDraft,
    MissionSetupRecommendation,
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionPlan,
    SearchMissionRequest,
)
from domain_types.terrain import TerrainClass
from service.mission_creation_service import MissionCreationService

# ---------------------------------------------------------------------------
# Mock implementations (inline, no adapter import)
# ---------------------------------------------------------------------------


class FakeMissionRepository:
    """In-memory mission repository for testing."""

    def __init__(self) -> None:
        self.drafts: list[MissionDraft] = []
        self.plans: list[SearchMissionPlan] = []

    def save_draft(self, draft: MissionDraft) -> None:
        self.drafts.append(draft)

    def save_plan(self, plan: SearchMissionPlan) -> None:
        self.plans.append(plan)


class FakeSopConfigurator:
    """Returns a fixed recommendation for testing."""

    def apply_profile(self, request: SearchMissionRequest) -> MissionSetupRecommendation:
        return MissionSetupRecommendation(
            recommended_method=SearchMethod.CONTOUR_SEARCH,
            constraints={"max_slope": 30.0},
            warnings=("경사 구간 주의",),
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def clock() -> FakeClock:
    return FakeClock(base_ms=1_700_000_000_000)


@pytest.fixture()
def id_gen() -> DeterministicIdGenerator:
    return DeterministicIdGenerator(prefix="M", seed=0)


@pytest.fixture()
def repo() -> FakeMissionRepository:
    return FakeMissionRepository()


@pytest.fixture()
def svc(
    clock: FakeClock, id_gen: DeterministicIdGenerator, repo: FakeMissionRepository
) -> MissionCreationService:
    return MissionCreationService(
        clock=clock,
        id_gen=id_gen,
        mission_repo=repo,
        sop_configurator=FakeSopConfigurator(),
    )


@pytest.fixture()
def valid_request() -> SearchMissionRequest:
    return SearchMissionRequest(
        request_id="REQ-001",
        operator_id="OP-001",
        mission_name="산악 수색",
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
        created_at_ms=1_700_000_000_000,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMissionCreationService:
    def test_create_draft_success(
        self,
        svc: MissionCreationService,
        valid_request: SearchMissionRequest,
        repo: FakeMissionRepository,
    ) -> None:
        """TC-MISSION-001: Operator가 SearchMissionRequest를 생성할 수 있다."""
        draft = svc.create_draft(valid_request)
        assert draft.mission_id == "M-000001"
        assert draft.validation_status == "PENDING_APPROVAL"
        assert len(repo.drafts) == 1

    def test_create_draft_with_sop_constraints(
        self,
        svc: MissionCreationService,
        valid_request: SearchMissionRequest,
    ) -> None:
        draft = svc.create_draft(valid_request)
        assert "max_slope" in draft.sop_constraints

    def test_create_draft_invalid_area_raises(
        self,
        svc: MissionCreationService,
    ) -> None:
        """TC-MISSION-002: SearchArea 검증 실패 시 ValueError."""
        bad_request = SearchMissionRequest(
            request_id="REQ-BAD",
            operator_id="OP-001",
            mission_name="잘못된 구역",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(),
                frame_id="map",
            ),
            search_method=SearchMethod.AREA_SWEEP,
            sop_profile_id="mountain_missing_person",
            priority="HIGH",
            created_at_ms=1_700_000_000_000,
        )
        with pytest.raises(ValueError, match="SearchArea validation failed"):
            svc.create_draft(bad_request)

    def test_create_draft_incompatible_terrain_raises(
        self,
        svc: MissionCreationService,
        valid_request: SearchMissionRequest,
    ) -> None:
        """TC-MISSION-003: 지형 불일치 시 ValueError."""
        with pytest.raises(ValueError, match="SearchMethod validation failed"):
            svc.create_draft(valid_request, terrain_class=TerrainClass.CLIFF_OR_DROP)

    def test_deterministic_snapshot(
        self,
        clock: FakeClock,
        id_gen: DeterministicIdGenerator,
        repo: FakeMissionRepository,
        valid_request: SearchMissionRequest,
    ) -> None:
        """TC-MISSION-008: 동일 입력에서 동일 Draft Snapshot."""
        svc1 = MissionCreationService(
            clock=FakeClock(base_ms=1_700_000_000_000),
            id_gen=DeterministicIdGenerator(prefix="M", seed=0),
            mission_repo=FakeMissionRepository(),
            sop_configurator=FakeSopConfigurator(),
        )
        svc2 = MissionCreationService(
            clock=FakeClock(base_ms=1_700_000_000_000),
            id_gen=DeterministicIdGenerator(prefix="M", seed=0),
            mission_repo=FakeMissionRepository(),
            sop_configurator=FakeSopConfigurator(),
        )
        draft1 = svc1.create_draft(valid_request)
        draft2 = svc2.create_draft(valid_request)
        assert draft1.mission_id == draft2.mission_id
        assert draft1.draft_snapshot_id == draft2.draft_snapshot_id

    def test_without_sop_configurator(
        self,
        clock: FakeClock,
        id_gen: DeterministicIdGenerator,
        repo: FakeMissionRepository,
        valid_request: SearchMissionRequest,
    ) -> None:
        svc = MissionCreationService(clock=clock, id_gen=id_gen, mission_repo=repo)
        draft = svc.create_draft(valid_request)
        assert draft.sop_constraints == {}
