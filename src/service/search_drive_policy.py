"""Search drive policy.

Combines TerrainAnalysisResult + SearchMethod to decide
the SearchDriveProfile (locomotion mode, speed, clearance, etc.).

Decision rules from mission_creation_plan.md §5.1.
"""

from __future__ import annotations

from config.terrain_thresholds import DEFAULT_TERRAIN_THRESHOLDS, TerrainThresholds
from domain_types.mission import SearchMethod
from domain_types.terrain import (
    LocomotionMode,
    SearchDriveProfile,
    TerrainAnalysisResult,
    TerrainClass,
    TraversabilityLevel,
)


from beartype import beartype


@beartype
def decide_drive_profile(
    terrain: TerrainAnalysisResult,
    method: SearchMethod,
    thresholds: TerrainThresholds | None = None,
) -> SearchDriveProfile:
    """Decide the SearchDriveProfile based on terrain and search method.

    Decision priority:
        1. traversability_score < stop_threshold → STOP_AND_REPLAN
        2. CLIFF_OR_DROP or BLOCKED → STOP_AND_REPLAN
        3. STEEP_SLOPE → SLOW_SAFE
        4. ROUGH_RUBBLE → OBSTACLE_CLIMB
        5. NARROW_PASSAGE → EDGE_FOLLOW
        6. OBSTACLE_DENSE → SLOW_SAFE
        7. FLAT_OPEN / MILD_SLOPE → WHEEL
    """
    t = thresholds or DEFAULT_TERRAIN_THRESHOLDS

    # Rule 1: Below stop threshold
    if terrain.traversability_score < t.stop_threshold:
        return SearchDriveProfile(
            search_method=method,
            locomotion_mode=LocomotionMode.STOP_AND_REPLAN,
            speed_scale=0.0,
            min_clearance_cm=0.0,
            replan_required=True,
            scan_density="HIGH",
            reason=f"traversability_score {terrain.traversability_score} < stop_threshold {t.stop_threshold}",
        )

    # Rule 2: Cliff or blocked
    if (
        terrain.terrain_class == TerrainClass.CLIFF_OR_DROP
        or terrain.traversability_level == TraversabilityLevel.BLOCKED
    ):
        return SearchDriveProfile(
            search_method=method,
            locomotion_mode=LocomotionMode.STOP_AND_REPLAN,
            speed_scale=0.0,
            min_clearance_cm=0.0,
            replan_required=True,
            scan_density="HIGH",
            reason=f"terrain={terrain.terrain_class}, level={terrain.traversability_level}",
        )

    # Rule 3: Steep slope
    if terrain.terrain_class == TerrainClass.STEEP_SLOPE:
        return SearchDriveProfile(
            search_method=method,
            locomotion_mode=LocomotionMode.SLOW_SAFE,
            speed_scale=t.slow_speed / t.normal_speed,
            min_clearance_cm=40.0,
            replan_required=False,
            scan_density="HIGH",
            reason="steep slope — slow safe mode",
        )

    # Rule 4: Rough rubble
    if terrain.terrain_class == TerrainClass.ROUGH_RUBBLE:
        return SearchDriveProfile(
            search_method=method,
            locomotion_mode=LocomotionMode.OBSTACLE_CLIMB,
            speed_scale=t.crawl_speed / t.normal_speed,
            min_clearance_cm=50.0,
            replan_required=True,
            scan_density="HIGH",
            reason="rough rubble — obstacle climb mode",
        )

    # Rule 5: Narrow passage
    if terrain.terrain_class == TerrainClass.NARROW_PASSAGE:
        return SearchDriveProfile(
            search_method=method,
            locomotion_mode=LocomotionMode.EDGE_FOLLOW,
            speed_scale=t.slow_speed / t.normal_speed,
            min_clearance_cm=20.0,
            replan_required=False,
            scan_density="NORMAL",
            reason="narrow passage — edge follow mode",
        )

    # Rule 6: Obstacle dense
    if terrain.terrain_class == TerrainClass.OBSTACLE_DENSE:
        return SearchDriveProfile(
            search_method=method,
            locomotion_mode=LocomotionMode.SLOW_SAFE,
            speed_scale=t.slow_speed / t.normal_speed,
            min_clearance_cm=40.0,
            replan_required=True,
            scan_density="HIGH",
            reason="obstacle dense — slow safe with replan",
        )

    # Rule 7: Flat or mild — normal wheel
    return SearchDriveProfile(
        search_method=method,
        locomotion_mode=LocomotionMode.WHEEL,
        speed_scale=1.0,
        min_clearance_cm=30.0,
        replan_required=False,
        scan_density="NORMAL",
        reason=f"terrain={terrain.terrain_class} — normal wheel mode",
    )
