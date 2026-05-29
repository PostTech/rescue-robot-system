"""Terrain analysis threshold configuration.

Defines thresholds for slope, roughness, step height, and traversability scoring.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TerrainThresholds:
    """Configurable thresholds for terrain classification and traversability."""

    # Slope thresholds (degrees)
    mild_slope_max: float = 15.0
    steep_slope_max: float = 35.0
    cliff_slope_min: float = 60.0

    # Step height thresholds (cm)
    passable_step_max: float = 10.0
    caution_step_max: float = 25.0
    blocked_step_min: float = 50.0

    # Roughness thresholds (0.0 ~ 1.0)
    smooth_max: float = 0.2
    moderate_max: float = 0.5
    rough_min: float = 0.7

    # Obstacle density thresholds (0.0 ~ 1.0)
    sparse_max: float = 0.15
    dense_min: float = 0.5

    # Traversability score thresholds (0.0 ~ 1.0)
    passable_min: float = 0.7
    caution_min: float = 0.4
    replan_min: float = 0.2
    stop_threshold: float = 0.1

    # Speed limits (m/s)
    normal_speed: float = 1.0
    slow_speed: float = 0.3
    crawl_speed: float = 0.1


# Default thresholds instance
DEFAULT_TERRAIN_THRESHOLDS = TerrainThresholds()
