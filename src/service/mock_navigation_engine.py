"""Mock navigation engine.

Implements INavigationEngine Protocol with deterministic paths.
No ROS/rclpy dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain_types.common import Pose3D
from domain_types.terrain import TerrainClass


@dataclass(frozen=True)
class NavigationPath:
    """Planned navigation path."""

    waypoints: tuple[Pose3D, ...]
    total_distance_m: float
    estimated_time_s: float
    terrain_classes: tuple[str, ...] = ()
    is_feasible: bool = True
    blocked_reason: str = ""


class MockNavigationEngine:
    """Mock navigation engine returning fixed paths.

    Simulates INavigationEngine Protocol for Windows testing.
    Respects terrain traversability — blocked terrain yields infeasible path.
    """

    def __init__(self) -> None:
        self._blocked_terrains: set[str] = {TerrainClass.CLIFF_OR_DROP}

    def plan_path(
        self,
        start: Pose3D,
        goal: Pose3D,
        terrain_class: str = TerrainClass.FLAT_OPEN,
    ) -> NavigationPath:
        """Plan a path from start to goal.

        Args:
            start: Starting pose.
            goal: Goal pose.
            terrain_class: Terrain classification along the route.

        Returns:
            NavigationPath — infeasible if terrain is blocked.
        """
        if terrain_class in self._blocked_terrains:
            return NavigationPath(
                waypoints=(start,),
                total_distance_m=0.0,
                estimated_time_s=0.0,
                terrain_classes=(terrain_class,),
                is_feasible=False,
                blocked_reason=f"Terrain {terrain_class} is blocked",
            )

        # Simple 3-waypoint path: start -> midpoint -> goal
        mid = Pose3D(
            x=(start.x + goal.x) / 2,
            y=(start.y + goal.y) / 2,
            z=(start.z + goal.z) / 2,
            roll=0.0,
            pitch=0.0,
            yaw=0.0,
        )
        dist = ((goal.x - start.x) ** 2 + (goal.y - start.y) ** 2) ** 0.5
        speed = (
            0.3 if terrain_class in {TerrainClass.STEEP_SLOPE, TerrainClass.ROUGH_RUBBLE} else 1.0
        )

        return NavigationPath(
            waypoints=(start, mid, goal),
            total_distance_m=round(dist, 3),
            estimated_time_s=round(dist / speed, 3) if speed > 0 else 0.0,
            terrain_classes=(terrain_class,),
            is_feasible=True,
        )

    def add_blocked_terrain(self, terrain_class: str) -> None:
        """Mark a terrain class as blocked."""
        self._blocked_terrains.add(terrain_class)

    def remove_blocked_terrain(self, terrain_class: str) -> None:
        """Unblock a terrain class."""
        self._blocked_terrains.discard(terrain_class)
