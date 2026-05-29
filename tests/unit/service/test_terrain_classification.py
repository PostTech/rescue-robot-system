"""TC-TERRAIN-001~003: Terrain classification tests."""

from __future__ import annotations

from config.terrain_thresholds import DEFAULT_TERRAIN_THRESHOLDS
from domain_types.terrain import TerrainClass, TraversabilityLevel
from service.terrain_classification import assess_traversability, classify_terrain


class TestClassifyTerrain:
    def test_flat_open(self) -> None:
        """TC-TERRAIN-001: 평탄 지형 분류."""
        assert classify_terrain(5.0, 2.0, 0.1, 0.05) == TerrainClass.FLAT_OPEN

    def test_mild_slope(self) -> None:
        assert classify_terrain(20.0, 5.0, 0.2, 0.1) == TerrainClass.MILD_SLOPE

    def test_steep_slope(self) -> None:
        """TC-TERRAIN-002: 급경사 분류."""
        assert classify_terrain(40.0, 10.0, 0.3, 0.1) == TerrainClass.STEEP_SLOPE

    def test_cliff_or_drop(self) -> None:
        """TC-TERRAIN-003: 절벽 분류."""
        assert classify_terrain(70.0, 100.0, 0.9, 0.8) == TerrainClass.CLIFF_OR_DROP

    def test_rough_rubble(self) -> None:
        assert classify_terrain(10.0, 15.0, 0.8, 0.1) == TerrainClass.ROUGH_RUBBLE

    def test_obstacle_dense(self) -> None:
        assert classify_terrain(10.0, 5.0, 0.3, 0.6) == TerrainClass.OBSTACLE_DENSE

    def test_narrow_passage(self) -> None:
        assert classify_terrain(10.0, 5.0, 0.3, 0.2) == TerrainClass.NARROW_PASSAGE

    def test_cliff_takes_priority_over_dense(self) -> None:
        """Cliff classification has highest priority."""
        assert classify_terrain(65.0, 100.0, 0.9, 0.9) == TerrainClass.CLIFF_OR_DROP

    def test_dense_takes_priority_over_rough(self) -> None:
        assert classify_terrain(10.0, 5.0, 0.8, 0.6) == TerrainClass.OBSTACLE_DENSE

    def test_boundary_mild_slope_max(self) -> None:
        t = DEFAULT_TERRAIN_THRESHOLDS
        assert classify_terrain(t.mild_slope_max, 0.0, 0.0, 0.0) == TerrainClass.FLAT_OPEN
        assert classify_terrain(t.mild_slope_max + 0.1, 0.0, 0.0, 0.0) == TerrainClass.MILD_SLOPE


class TestAssessTraversability:
    def test_passable(self) -> None:
        assert assess_traversability(0.8) == TraversabilityLevel.PASSABLE

    def test_caution(self) -> None:
        assert assess_traversability(0.5) == TraversabilityLevel.CAUTION

    def test_replan_required(self) -> None:
        assert assess_traversability(0.25) == TraversabilityLevel.REPLAN_REQUIRED

    def test_blocked(self) -> None:
        assert assess_traversability(0.1) == TraversabilityLevel.BLOCKED

    def test_boundary_passable_min(self) -> None:
        t = DEFAULT_TERRAIN_THRESHOLDS
        assert assess_traversability(t.passable_min) == TraversabilityLevel.PASSABLE
        assert assess_traversability(t.passable_min - 0.01) == TraversabilityLevel.CAUTION
