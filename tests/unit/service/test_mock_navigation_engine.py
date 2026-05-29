"""TC-NAV-001/002: Mock navigation engine tests."""

from __future__ import annotations

from domain_types.common import Pose3D
from domain_types.terrain import TerrainClass
from service.mock_navigation_engine import MockNavigationEngine

START = Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
GOAL = Pose3D(10.0, 0.0, 0.0, 0.0, 0.0, 0.0)


class TestMockNavigationEngine:
    def test_tc_nav_001_fixed_path(self) -> None:
        """TC-NAV-001: Mock navigation returns fixed path."""
        nav = MockNavigationEngine()
        path = nav.plan_path(START, GOAL)
        assert path.is_feasible is True
        assert len(path.waypoints) == 3
        assert path.waypoints[0] == START
        assert path.waypoints[-1] == GOAL
        assert path.total_distance_m == 10.0

    def test_tc_nav_002_blocked_terrain(self) -> None:
        """TC-NAV-002: Navigation respects blocked terrain."""
        nav = MockNavigationEngine()
        path = nav.plan_path(START, GOAL, terrain_class=TerrainClass.CLIFF_OR_DROP)
        assert path.is_feasible is False
        assert "blocked" in path.blocked_reason.lower()

    def test_steep_slope_slower(self) -> None:
        nav = MockNavigationEngine()
        flat_path = nav.plan_path(START, GOAL, TerrainClass.FLAT_OPEN)
        steep_path = nav.plan_path(START, GOAL, TerrainClass.STEEP_SLOPE)
        assert steep_path.estimated_time_s > flat_path.estimated_time_s

    def test_midpoint_calculation(self) -> None:
        nav = MockNavigationEngine()
        path = nav.plan_path(START, Pose3D(4.0, 6.0, 0.0, 0.0, 0.0, 0.0))
        mid = path.waypoints[1]
        assert mid.x == 2.0
        assert mid.y == 3.0

    def test_add_blocked_terrain(self) -> None:
        nav = MockNavigationEngine()
        nav.add_blocked_terrain(TerrainClass.OBSTACLE_DENSE)
        path = nav.plan_path(START, GOAL, TerrainClass.OBSTACLE_DENSE)
        assert path.is_feasible is False

    def test_remove_blocked_terrain(self) -> None:
        nav = MockNavigationEngine()
        nav.remove_blocked_terrain(TerrainClass.CLIFF_OR_DROP)
        path = nav.plan_path(START, GOAL, TerrainClass.CLIFF_OR_DROP)
        assert path.is_feasible is True

    def test_deterministic(self) -> None:
        n1 = MockNavigationEngine()
        n2 = MockNavigationEngine()
        assert n1.plan_path(START, GOAL) == n2.plan_path(START, GOAL)
