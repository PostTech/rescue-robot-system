"""Terrain analyzer service.

Produces a TerrainAnalysisResult from raw feature inputs.
In production, features come from 3D LiDAR elevation grid processing.
In testing, features are fixed fixtures.
"""

from __future__ import annotations

from config.terrain_thresholds import DEFAULT_TERRAIN_THRESHOLDS, TerrainThresholds
from domain_types.terrain import TerrainAnalysisResult
from service.terrain_classification import assess_traversability, classify_terrain


def analyze_terrain(
    slope_degree: float,
    step_height_cm: float,
    roughness_score: float,
    obstacle_density: float,
    traversability_score: float,
    thresholds: TerrainThresholds | None = None,
) -> TerrainAnalysisResult:
    """Analyze terrain features and produce an immutable result.

    Args:
        slope_degree: Ground slope in degrees (0–90).
        step_height_cm: Maximum step height in centimeters.
        roughness_score: Surface roughness (0.0–1.0).
        obstacle_density: Obstacle density ratio (0.0–1.0).
        traversability_score: Overall traversability (0.0–1.0).
        thresholds: Optional custom thresholds (defaults to DEFAULT).

    Returns:
        Frozen TerrainAnalysisResult.
    """
    t = thresholds or DEFAULT_TERRAIN_THRESHOLDS

    terrain_class = classify_terrain(
        slope_degree=slope_degree,
        step_height_cm=step_height_cm,
        roughness_score=roughness_score,
        obstacle_density=obstacle_density,
        thresholds=t,
    )

    traversability_level = assess_traversability(
        traversability_score=traversability_score,
        thresholds=t,
    )

    traversable = traversability_score >= t.replan_min

    return TerrainAnalysisResult(
        terrain_class=terrain_class,
        slope_degree=slope_degree,
        step_height_cm=step_height_cm,
        roughness_score=roughness_score,
        obstacle_density=obstacle_density,
        traversability_score=traversability_score,
        traversability_level=traversability_level,
        traversable=traversable,
    )
