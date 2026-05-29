"""TC-TERRAIN-006~008, TC-DETVAL-009: Search drive policy tests."""

from __future__ import annotations

from domain_types.mission import SearchMethod
from domain_types.terrain import (
    LocomotionMode,
    TerrainAnalysisResult,
    TerrainClass,
    TraversabilityLevel,
)
from service.search_drive_policy import decide_drive_profile


def _result(
    terrain_class: TerrainClass = TerrainClass.FLAT_OPEN,
    slope: float = 3.0,
    step: float = 1.0,
    roughness: float = 0.1,
    obstacle: float = 0.05,
    trav_score: float = 0.9,
    trav_level: TraversabilityLevel = TraversabilityLevel.PASSABLE,
    traversable: bool = True,
) -> TerrainAnalysisResult:
    return TerrainAnalysisResult(
        terrain_class=terrain_class,
        slope_degree=slope,
        step_height_cm=step,
        roughness_score=roughness,
        obstacle_density=obstacle,
        traversability_score=trav_score,
        traversability_level=trav_level,
        traversable=traversable,
    )


class TestDecideDriveProfile:
    def test_flat_open_wheel(self) -> None:
        """TC-TERRAIN-006: 평탄 → WHEEL."""
        profile = decide_drive_profile(
            _result(),
            SearchMethod.PARALLEL_SWEEP,
        )
        assert profile.locomotion_mode == LocomotionMode.WHEEL
        assert profile.speed_scale == 1.0
        assert profile.replan_required is False

    def test_cliff_stop_and_replan(self) -> None:
        """TC-TERRAIN-007: 절벽 → STOP_AND_REPLAN."""
        profile = decide_drive_profile(
            _result(
                terrain_class=TerrainClass.CLIFF_OR_DROP,
                slope=80.0,
                trav_score=0.05,
                trav_level=TraversabilityLevel.BLOCKED,
                traversable=False,
            ),
            SearchMethod.PERIMETER_SEARCH,
        )
        assert profile.locomotion_mode == LocomotionMode.STOP_AND_REPLAN
        assert profile.replan_required is True
        assert profile.speed_scale == 0.0

    def test_steep_slope_slow_safe(self) -> None:
        """TC-TERRAIN-008: 급경사 → SLOW_SAFE."""
        profile = decide_drive_profile(
            _result(
                terrain_class=TerrainClass.STEEP_SLOPE,
                slope=40.0,
                trav_score=0.5,
                trav_level=TraversabilityLevel.CAUTION,
            ),
            SearchMethod.CONTOUR_SEARCH,
        )
        assert profile.locomotion_mode == LocomotionMode.SLOW_SAFE
        assert 0.0 < profile.speed_scale < 1.0

    def test_rough_rubble_obstacle_climb(self) -> None:
        profile = decide_drive_profile(
            _result(
                terrain_class=TerrainClass.ROUGH_RUBBLE,
                roughness=0.8,
                trav_score=0.35,
                trav_level=TraversabilityLevel.CAUTION,
            ),
            SearchMethod.FRONTIER_EXPLORATION,
        )
        assert profile.locomotion_mode == LocomotionMode.OBSTACLE_CLIMB
        assert profile.replan_required is True

    def test_narrow_passage_edge_follow(self) -> None:
        profile = decide_drive_profile(
            _result(
                terrain_class=TerrainClass.NARROW_PASSAGE,
                obstacle=0.2,
                trav_score=0.6,
                trav_level=TraversabilityLevel.CAUTION,
            ),
            SearchMethod.SINGLE_FILE,
        )
        assert profile.locomotion_mode == LocomotionMode.EDGE_FOLLOW

    def test_obstacle_dense_slow_safe(self) -> None:
        profile = decide_drive_profile(
            _result(
                terrain_class=TerrainClass.OBSTACLE_DENSE,
                obstacle=0.7,
                trav_score=0.3,
                trav_level=TraversabilityLevel.REPLAN_REQUIRED,
            ),
            SearchMethod.PERIMETER_SEARCH,
        )
        assert profile.locomotion_mode == LocomotionMode.SLOW_SAFE
        assert profile.replan_required is True

    def test_below_stop_threshold_always_stops(self) -> None:
        """Any terrain below stop_threshold → STOP_AND_REPLAN regardless."""
        profile = decide_drive_profile(
            _result(
                terrain_class=TerrainClass.FLAT_OPEN,
                trav_score=0.05,
                trav_level=TraversabilityLevel.BLOCKED,
            ),
            SearchMethod.AREA_SWEEP,
        )
        assert profile.locomotion_mode == LocomotionMode.STOP_AND_REPLAN

    def test_mild_slope_wheel(self) -> None:
        profile = decide_drive_profile(
            _result(terrain_class=TerrainClass.MILD_SLOPE, slope=20.0),
            SearchMethod.CONTOUR_SEARCH,
        )
        assert profile.locomotion_mode == LocomotionMode.WHEEL

    def test_deterministic_same_input(self) -> None:
        """TC-DETVAL-009: 동일 입력 → 동일 SearchDriveProfile."""
        terrain = _result(
            terrain_class=TerrainClass.STEEP_SLOPE,
            slope=40.0,
            trav_score=0.5,
            trav_level=TraversabilityLevel.CAUTION,
        )
        p1 = decide_drive_profile(terrain, SearchMethod.CONTOUR_SEARCH)
        p2 = decide_drive_profile(terrain, SearchMethod.CONTOUR_SEARCH)
        assert p1 == p2

    def test_search_method_preserved_in_profile(self) -> None:
        profile = decide_drive_profile(_result(), SearchMethod.GRID_COVERAGE)
        assert profile.search_method == SearchMethod.GRID_COVERAGE
