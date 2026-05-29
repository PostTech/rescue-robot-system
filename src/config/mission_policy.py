"""Mission policy configuration.

Defines SearchArea validation rules and SearchMethod-TerrainClass compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from domain_types.mission import SearchAreaType, SearchMethod
from domain_types.terrain import TerrainClass

# ---------------------------------------------------------------------------
# SearchArea validation policy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SearchAreaPolicy:
    """Minimum coordinate counts required for each area type."""

    min_coordinates: dict[str, int] = field(
        default_factory=lambda: {
            SearchAreaType.POLYGON: 3,
            SearchAreaType.WAYPOINT_ROUTE: 2,
            SearchAreaType.GRID: 1,
            SearchAreaType.GEOFENCE: 3,
        }
    )


# ---------------------------------------------------------------------------
# SearchMethod ↔ TerrainClass compatibility
# ---------------------------------------------------------------------------

# Maps TerrainClass → tuple of recommended SearchMethods
TERRAIN_METHOD_COMPATIBILITY: dict[str, tuple[SearchMethod, ...]] = {
    TerrainClass.FLAT_OPEN: (
        SearchMethod.PARALLEL_SWEEP,
        SearchMethod.GRID_COVERAGE,
        SearchMethod.AREA_SWEEP,
    ),
    TerrainClass.MILD_SLOPE: (
        SearchMethod.CONTOUR_SEARCH,
        SearchMethod.PARALLEL_SWEEP,
    ),
    TerrainClass.STEEP_SLOPE: (
        SearchMethod.CONTOUR_SEARCH,
        SearchMethod.WAYPOINT_ROUTE,
    ),
    TerrainClass.ROUGH_RUBBLE: (
        SearchMethod.FRONTIER_EXPLORATION,
        SearchMethod.MANUAL_ASSISTED,
    ),
    TerrainClass.NARROW_PASSAGE: (
        SearchMethod.SINGLE_FILE,
        SearchMethod.TRACKLINE_SEARCH,
        SearchMethod.WAYPOINT_ROUTE,
    ),
    TerrainClass.OBSTACLE_DENSE: (
        SearchMethod.PERIMETER_SEARCH,
        SearchMethod.FRONTIER_EXPLORATION,
    ),
    TerrainClass.CLIFF_OR_DROP: (SearchMethod.PERIMETER_SEARCH,),
    TerrainClass.UNKNOWN: (
        SearchMethod.MANUAL_ASSISTED,
        SearchMethod.FRONTIER_EXPLORATION,
    ),
}


def is_method_compatible(terrain: str, method: SearchMethod) -> bool:
    """Check if a search method is compatible with a terrain class."""
    allowed = TERRAIN_METHOD_COMPATIBILITY.get(terrain, ())
    return method in allowed
