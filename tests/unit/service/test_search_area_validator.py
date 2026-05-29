"""TC-MISSION-002, TC-FUNC-BND-010: SearchArea validation tests."""

from __future__ import annotations

from domain_types.common import Pose3D
from domain_types.mission import SearchArea, SearchAreaType
from service.search_area_validator import validate_search_area


def _pose(x: float = 0.0, y: float = 0.0) -> Pose3D:
    return Pose3D(x=x, y=y, z=0.0, roll=0.0, pitch=0.0, yaw=0.0)


class TestSearchAreaValidator:
    def test_polygon_3_coords_valid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(_pose(0), _pose(1), _pose(2)),
            frame_id="map",
        )
        result = validate_search_area(area)
        assert result.is_valid is True

    def test_polygon_2_coords_invalid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(_pose(0), _pose(1)),
            frame_id="map",
        )
        result = validate_search_area(area)
        assert result.is_valid is False
        assert result.errors[0].code == "MIN_COORDINATES"

    def test_polygon_0_coords_invalid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(),
            frame_id="map",
        )
        result = validate_search_area(area)
        assert result.is_valid is False

    def test_waypoint_2_coords_valid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.WAYPOINT_ROUTE,
            coordinates=(_pose(0), _pose(1)),
            frame_id="map",
        )
        result = validate_search_area(area)
        assert result.is_valid is True

    def test_waypoint_1_coord_invalid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.WAYPOINT_ROUTE,
            coordinates=(_pose(0),),
            frame_id="map",
        )
        result = validate_search_area(area)
        assert result.is_valid is False

    def test_grid_1_coord_valid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.GRID,
            coordinates=(_pose(0),),
            frame_id="map",
        )
        result = validate_search_area(area)
        assert result.is_valid is True

    def test_empty_frame_id_invalid(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.GRID,
            coordinates=(_pose(0),),
            frame_id="",
        )
        result = validate_search_area(area)
        assert result.is_valid is False
        assert result.errors[0].code == "EMPTY_FRAME_ID"

    def test_multiple_errors(self) -> None:
        area = SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(),
            frame_id="  ",
        )
        result = validate_search_area(area)
        assert result.is_valid is False
        assert len(result.errors) == 2
