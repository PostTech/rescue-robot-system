"""Tests for mission_policy config."""

from __future__ import annotations

from config.mission_policy import (
    TERRAIN_METHOD_COMPATIBILITY,
    SearchAreaPolicy,
    is_method_compatible,
)
from domain_types.mission import SearchAreaType, SearchMethod
from domain_types.terrain import TerrainClass


class TestSearchAreaPolicy:
    def test_polygon_requires_3(self) -> None:
        policy = SearchAreaPolicy()
        assert policy.min_coordinates[SearchAreaType.POLYGON] == 3

    def test_waypoint_requires_2(self) -> None:
        policy = SearchAreaPolicy()
        assert policy.min_coordinates[SearchAreaType.WAYPOINT_ROUTE] == 2

    def test_grid_requires_1(self) -> None:
        policy = SearchAreaPolicy()
        assert policy.min_coordinates[SearchAreaType.GRID] == 1


class TestTerrainMethodCompatibility:
    def test_flat_open_allows_parallel_sweep(self) -> None:
        assert is_method_compatible(TerrainClass.FLAT_OPEN, SearchMethod.PARALLEL_SWEEP)

    def test_flat_open_rejects_single_file(self) -> None:
        assert not is_method_compatible(TerrainClass.FLAT_OPEN, SearchMethod.SINGLE_FILE)

    def test_cliff_allows_perimeter_only(self) -> None:
        allowed = TERRAIN_METHOD_COMPATIBILITY[TerrainClass.CLIFF_OR_DROP]
        assert allowed == (SearchMethod.PERIMETER_SEARCH,)

    def test_narrow_passage_allows_single_file(self) -> None:
        assert is_method_compatible(TerrainClass.NARROW_PASSAGE, SearchMethod.SINGLE_FILE)

    def test_unknown_terrain_returns_empty_for_missing(self) -> None:
        assert not is_method_compatible("NONEXISTENT", SearchMethod.AREA_SWEEP)

    def test_all_terrain_classes_have_mapping(self) -> None:
        for tc in TerrainClass:
            assert tc in TERRAIN_METHOD_COMPATIBILITY, f"Missing mapping for {tc}"
