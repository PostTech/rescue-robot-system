"""TC-MISSION-003: SearchMethod policy tests."""

from __future__ import annotations

from domain_types.mission import SearchMethod
from domain_types.terrain import TerrainClass
from service.search_method_policy import validate_search_method


class TestSearchMethodPolicy:
    def test_flat_parallel_sweep_compatible(self) -> None:
        result = validate_search_method(SearchMethod.PARALLEL_SWEEP, TerrainClass.FLAT_OPEN)
        assert result.is_valid is True

    def test_flat_single_file_incompatible(self) -> None:
        result = validate_search_method(SearchMethod.SINGLE_FILE, TerrainClass.FLAT_OPEN)
        assert result.is_valid is False
        assert result.errors[0].code == "INCOMPATIBLE_TERRAIN"

    def test_cliff_perimeter_compatible(self) -> None:
        result = validate_search_method(SearchMethod.PERIMETER_SEARCH, TerrainClass.CLIFF_OR_DROP)
        assert result.is_valid is True

    def test_cliff_parallel_sweep_incompatible(self) -> None:
        result = validate_search_method(SearchMethod.PARALLEL_SWEEP, TerrainClass.CLIFF_OR_DROP)
        assert result.is_valid is False

    def test_narrow_passage_single_file(self) -> None:
        result = validate_search_method(SearchMethod.SINGLE_FILE, TerrainClass.NARROW_PASSAGE)
        assert result.is_valid is True

    def test_rough_rubble_frontier(self) -> None:
        result = validate_search_method(
            SearchMethod.FRONTIER_EXPLORATION, TerrainClass.ROUGH_RUBBLE
        )
        assert result.is_valid is True
