"""TC-DEP-004, TC-MISSION-006, TC-MOD-005: Mission setup ViewModel tests."""

from __future__ import annotations

import pytest

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.common import Pose3D
from domain_types.mission import (
    MissionDraft,
    SearchAreaType,
    SearchMethod,
    SearchMissionRequest,
)
from ui.mission_setup_view_model import MissionSetupViewModel


class FakeMissionService:
    """Mock service for ViewModel testing."""

    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail
        self.last_request: SearchMissionRequest | None = None

    def create_draft(self, request: SearchMissionRequest) -> MissionDraft:
        self.last_request = request
        if self._should_fail:
            raise ValueError("Validation failed")
        return MissionDraft(
            mission_id="M-000001",
            request=request,
            validation_status="PENDING_APPROVAL",
        )


@pytest.fixture()
def vm() -> MissionSetupViewModel:
    return MissionSetupViewModel(
        service=FakeMissionService(),
        operator_id="OP-001",
        request_id_generator=DeterministicIdGenerator("REQ", 0),
        clock=FakeClock(base_ms=1_700_000_000_000),
    )


class TestMissionSetupViewModel:
    def test_submit_success(self, vm: MissionSetupViewModel) -> None:
        vm.set_area(
            SearchAreaType.POLYGON,
            [Pose3D(0, 0, 0, 0, 0, 0), Pose3D(1, 0, 0, 0, 0, 0), Pose3D(1, 1, 0, 0, 0, 0)],
        )
        vm.set_search_method(SearchMethod.PARALLEL_SWEEP)
        vm.set_sop_profile("mountain_missing_person")
        vm.set_mission_name("test mission")
        draft = vm.submit()
        assert draft is not None
        assert draft.mission_id == "M-000001"
        assert vm.state.error_message == ""

    def test_submit_missing_fields(self, vm: MissionSetupViewModel) -> None:
        draft = vm.submit()
        assert draft is None
        assert "required" in vm.state.error_message

    def test_submit_validation_error(self) -> None:
        vm = MissionSetupViewModel(
            service=FakeMissionService(should_fail=True),
            operator_id="OP-001",
            request_id_generator=DeterministicIdGenerator("REQ", 0),
            clock=FakeClock(),
        )
        vm.set_area(
            SearchAreaType.POLYGON,
            [Pose3D(0, 0, 0, 0, 0, 0), Pose3D(1, 0, 0, 0, 0, 0), Pose3D(1, 1, 0, 0, 0, 0)],
        )
        vm.set_search_method(SearchMethod.AREA_SWEEP)
        draft = vm.submit()
        assert draft is None
        assert "Validation failed" in vm.state.error_message

    def test_state_updates(self, vm: MissionSetupViewModel) -> None:
        vm.set_area(SearchAreaType.GRID, [Pose3D(0, 0, 0, 0, 0, 0)])
        assert vm.state.area_type == SearchAreaType.GRID
        vm.set_search_method(SearchMethod.GRID_COVERAGE)
        assert vm.state.search_method == SearchMethod.GRID_COVERAGE
        vm.set_priority("HIGH")
        assert vm.state.priority == "HIGH"

    def test_no_direct_db_access(self) -> None:
        """TC-MISSION-006: UI does not directly access DB/Repository."""
        import ast
        from pathlib import Path

        src = Path("c:/Users/cosmo/AI_challange/src/ui/mission_setup_view_model.py")
        tree = ast.parse(src.read_text(encoding="utf-8"))
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        forbidden = {"sqlite3", "psycopg2", "pymongo", "adapters.storage"}
        violations = [i for i in imports if i.split(".")[0] in forbidden or i in forbidden]
        assert violations == [], f"UI directly imports DB: {violations}"
