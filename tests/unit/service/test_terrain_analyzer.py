"""TC-TERRAIN-004/005: Terrain analyzer integration tests."""

from __future__ import annotations

from domain_types.terrain import TerrainClass, TraversabilityLevel
from service.terrain_analyzer import analyze_terrain


class TestAnalyzeTerrain:
    def test_flat_open_passable(self) -> None:
        """TC-TERRAIN-004: 평탄 지형 → PASSABLE."""
        result = analyze_terrain(
            slope_degree=3.0,
            step_height_cm=1.0,
            roughness_score=0.1,
            obstacle_density=0.05,
            traversability_score=0.9,
        )
        assert result.terrain_class == TerrainClass.FLAT_OPEN
        assert result.traversability_level == TraversabilityLevel.PASSABLE
        assert result.traversable is True

    def test_cliff_blocked(self) -> None:
        """TC-TERRAIN-005: 절벽 → BLOCKED."""
        result = analyze_terrain(
            slope_degree=80.0,
            step_height_cm=200.0,
            roughness_score=0.9,
            obstacle_density=0.8,
            traversability_score=0.05,
        )
        assert result.terrain_class == TerrainClass.CLIFF_OR_DROP
        assert result.traversability_level == TraversabilityLevel.BLOCKED
        assert result.traversable is False

    def test_rough_rubble_caution(self) -> None:
        result = analyze_terrain(
            slope_degree=10.0,
            step_height_cm=15.0,
            roughness_score=0.8,
            obstacle_density=0.1,
            traversability_score=0.5,
        )
        assert result.terrain_class == TerrainClass.ROUGH_RUBBLE
        assert result.traversability_level == TraversabilityLevel.CAUTION

    def test_result_is_frozen(self) -> None:
        result = analyze_terrain(3.0, 1.0, 0.1, 0.05, 0.9)
        import pytest

        with pytest.raises(AttributeError):
            result.slope_degree = 99.0

    def test_deterministic_same_input(self) -> None:
        """TC-DETVAL-009 partial: 동일 입력 → 동일 결과."""
        r1 = analyze_terrain(25.0, 8.0, 0.3, 0.12, 0.6)
        r2 = analyze_terrain(25.0, 8.0, 0.3, 0.12, 0.6)
        assert r1 == r2
