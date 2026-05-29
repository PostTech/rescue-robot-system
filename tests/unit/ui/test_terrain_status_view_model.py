"""TC-MOD-008: Terrain status ViewModel tests."""

from __future__ import annotations

from domain_types.mission import SearchMethod
from domain_types.terrain import (
    LocomotionMode,
    SearchDriveProfile,
    TerrainAnalysisResult,
    TerrainClass,
    TraversabilityLevel,
)
from ui.terrain_status_view_model import TerrainStatusViewModel


def _flat_result() -> TerrainAnalysisResult:
    return TerrainAnalysisResult(
        terrain_class=TerrainClass.FLAT_OPEN,
        slope_degree=3.0,
        step_height_cm=1.0,
        roughness_score=0.1,
        obstacle_density=0.05,
        traversability_score=0.9,
        traversability_level=TraversabilityLevel.PASSABLE,
        traversable=True,
    )


def _cliff_result() -> TerrainAnalysisResult:
    return TerrainAnalysisResult(
        terrain_class=TerrainClass.CLIFF_OR_DROP,
        slope_degree=80.0,
        step_height_cm=200.0,
        roughness_score=0.9,
        obstacle_density=0.8,
        traversability_score=0.05,
        traversability_level=TraversabilityLevel.BLOCKED,
        traversable=False,
    )


class TestTerrainStatusViewModel:
    def test_update_flat_terrain(self) -> None:
        vm = TerrainStatusViewModel()
        vm.update_terrain(_flat_result())
        assert vm.state.terrain_class == TerrainClass.FLAT_OPEN
        assert vm.state.traversable is True
        assert len(vm.state.warnings) == 0

    def test_update_cliff_terrain(self) -> None:
        vm = TerrainStatusViewModel()
        vm.update_terrain(_cliff_result())
        assert vm.state.terrain_class == TerrainClass.CLIFF_OR_DROP
        assert vm.state.traversable is False
        assert any("cliff" in w.lower() for w in vm.state.warnings)
        assert any("BLOCKED" in w for w in vm.state.warnings)

    def test_update_drive_profile(self) -> None:
        vm = TerrainStatusViewModel()
        profile = SearchDriveProfile(
            search_method=SearchMethod.PARALLEL_SWEEP,
            locomotion_mode=LocomotionMode.WHEEL,
            speed_scale=1.0,
            min_clearance_cm=30.0,
            replan_required=False,
            scan_density="NORMAL",
            reason="flat terrain",
        )
        vm.update_drive_profile(profile)
        assert vm.state.locomotion_mode == LocomotionMode.WHEEL
        assert vm.state.speed_scale == 1.0

    def test_is_safe_flat(self) -> None:
        vm = TerrainStatusViewModel()
        vm.update_terrain(_flat_result())
        vm.update_drive_profile(
            SearchDriveProfile(
                search_method=SearchMethod.AREA_SWEEP,
                locomotion_mode=LocomotionMode.WHEEL,
                speed_scale=1.0,
                min_clearance_cm=30.0,
                replan_required=False,
                scan_density="NORMAL",
                reason="ok",
            )
        )
        assert vm.is_safe() is True

    def test_is_not_safe_cliff(self) -> None:
        vm = TerrainStatusViewModel()
        vm.update_terrain(_cliff_result())
        vm.update_drive_profile(
            SearchDriveProfile(
                search_method=SearchMethod.PERIMETER_SEARCH,
                locomotion_mode=LocomotionMode.STOP_AND_REPLAN,
                speed_scale=0.0,
                min_clearance_cm=0.0,
                replan_required=True,
                scan_density="HIGH",
                reason="cliff",
            )
        )
        assert vm.is_safe() is False
