"""Terrain classification from analysis features.

Maps slope, roughness, step height, obstacle density
to TerrainClass using configurable thresholds.
"""

from __future__ import annotations

from config.terrain_thresholds import DEFAULT_TERRAIN_THRESHOLDS, TerrainThresholds
from domain_types.terrain import TerrainClass, TraversabilityLevel


def classify_terrain(
    slope_degree: float,
    step_height_cm: float,
    roughness_score: float,
    obstacle_density: float,
    thresholds: TerrainThresholds | None = None,
) -> TerrainClass:
    """Determine TerrainClass from raw analysis features.

    Decision priority (highest → lowest):
        1. CLIFF_OR_DROP  — slope ≥ cliff_slope_min
        2. OBSTACLE_DENSE — obstacle_density ≥ dense_min
        3. NARROW_PASSAGE — obstacle_density ≥ sparse_max AND step_height < caution
        4. ROUGH_RUBBLE   — roughness ≥ rough_min
        5. STEEP_SLOPE    — slope > steep_slope_max
        6. MILD_SLOPE     — slope > mild_slope_max
        7. FLAT_OPEN      — everything else
    """
    t = thresholds or DEFAULT_TERRAIN_THRESHOLDS

    if slope_degree >= t.cliff_slope_min:
        return TerrainClass.CLIFF_OR_DROP

    if obstacle_density >= t.dense_min:
        return TerrainClass.OBSTACLE_DENSE

    if obstacle_density >= t.sparse_max and step_height_cm < t.caution_step_max:
        return TerrainClass.NARROW_PASSAGE

    if roughness_score >= t.rough_min:
        return TerrainClass.ROUGH_RUBBLE

    if slope_degree > t.steep_slope_max:
        return TerrainClass.STEEP_SLOPE

    if slope_degree > t.mild_slope_max:
        return TerrainClass.MILD_SLOPE

    return TerrainClass.FLAT_OPEN


def assess_traversability(
    traversability_score: float,
    thresholds: TerrainThresholds | None = None,
) -> TraversabilityLevel:
    """Map a traversability score (0.0–1.0) to a qualitative level."""
    t = thresholds or DEFAULT_TERRAIN_THRESHOLDS

    if traversability_score >= t.passable_min:
        return TraversabilityLevel.PASSABLE
    if traversability_score >= t.caution_min:
        return TraversabilityLevel.CAUTION
    if traversability_score >= t.replan_min:
        return TraversabilityLevel.REPLAN_REQUIRED
    return TraversabilityLevel.BLOCKED
