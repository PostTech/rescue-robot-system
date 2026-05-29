"""TC-FUNC-BND-014: Terrain types — instantiation, frozen, boundary validation."""

from __future__ import annotations

import pytest

from domain_types.mission import SearchMethod
from domain_types.terrain import (
    LocomotionDecision,
    LocomotionMode,
    SearchDriveProfile,
    TerrainAnalysisResult,
    TerrainClass,
    TraversabilityLevel,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def flat_terrain() -> TerrainAnalysisResult:
    return TerrainAnalysisResult(
        terrain_class=TerrainClass.FLAT_OPEN,
        slope_degree=2.0,
        step_height_cm=0.5,
        roughness_score=0.1,
        obstacle_density=0.05,
        traversability_score=0.95,
        traversability_level=TraversabilityLevel.PASSABLE,
        traversable=True,
    )


@pytest.fixture()
def cliff_terrain() -> TerrainAnalysisResult:
    return TerrainAnalysisResult(
        terrain_class=TerrainClass.CLIFF_OR_DROP,
        slope_degree=85.0,
        step_height_cm=200.0,
        roughness_score=0.9,
        obstacle_density=0.8,
        traversability_score=0.05,
        traversability_level=TraversabilityLevel.BLOCKED,
        traversable=False,
    )


# ---------------------------------------------------------------------------
# TerrainClass enum
# ---------------------------------------------------------------------------


class TestTerrainClass:
    def test_has_8_classes(self) -> None:
        assert len(TerrainClass) == 8

    def test_unknown_exists(self) -> None:
        assert TerrainClass.UNKNOWN == "UNKNOWN"


# ---------------------------------------------------------------------------
# TraversabilityLevel enum
# ---------------------------------------------------------------------------


class TestTraversabilityLevel:
    def test_has_4_levels(self) -> None:
        expected = {"PASSABLE", "CAUTION", "REPLAN_REQUIRED", "BLOCKED"}
        assert {m.value for m in TraversabilityLevel} == expected


# ---------------------------------------------------------------------------
# LocomotionMode enum
# ---------------------------------------------------------------------------


class TestLocomotionMode:
    def test_has_6_modes(self) -> None:
        assert len(LocomotionMode) == 6

    def test_wheel_mode(self) -> None:
        assert LocomotionMode.WHEEL == "WHEEL"

    def test_stop_mode(self) -> None:
        assert LocomotionMode.STOP == "STOP"


# ---------------------------------------------------------------------------
# TerrainAnalysisResult
# ---------------------------------------------------------------------------


class TestTerrainAnalysisResult:
    def test_flat_terrain(self, flat_terrain: TerrainAnalysisResult) -> None:
        assert flat_terrain.traversable is True
        assert flat_terrain.slope_degree == 2.0

    def test_cliff_terrain(self, cliff_terrain: TerrainAnalysisResult) -> None:
        assert cliff_terrain.traversable is False
        assert cliff_terrain.traversability_level == TraversabilityLevel.BLOCKED

    def test_frozen(self, flat_terrain: TerrainAnalysisResult) -> None:
        with pytest.raises(AttributeError):
            flat_terrain.slope_degree = 99.0

    def test_boundary_negative_slope(self) -> None:
        """TC-FUNC-BND-014: 음수 경사도 입력 (검증은 Service 책임)."""
        result = TerrainAnalysisResult(
            terrain_class=TerrainClass.UNKNOWN,
            slope_degree=-5.0,
            step_height_cm=0.0,
            roughness_score=0.0,
            obstacle_density=0.0,
            traversability_score=0.0,
            traversability_level=TraversabilityLevel.PASSABLE,
            traversable=True,
        )
        assert result.slope_degree == -5.0  # DTO는 값만 보관, 검증은 Service

    def test_boundary_extreme_values(self) -> None:
        """TC-FUNC-BND-014: 극단값 입력."""
        result = TerrainAnalysisResult(
            terrain_class=TerrainClass.STEEP_SLOPE,
            slope_degree=90.0,
            step_height_cm=500.0,
            roughness_score=1.0,
            obstacle_density=1.0,
            traversability_score=0.0,
            traversability_level=TraversabilityLevel.BLOCKED,
            traversable=False,
        )
        assert result.traversability_score == 0.0


# ---------------------------------------------------------------------------
# LocomotionDecision
# ---------------------------------------------------------------------------


class TestLocomotionDecision:
    def test_creation(self) -> None:
        decision = LocomotionDecision(
            target_mode=LocomotionMode.OBSTACLE_CLIMB,
            recommended_speed=0.3,
            reason="steep slope detected",
        )
        assert decision.target_mode == LocomotionMode.OBSTACLE_CLIMB

    def test_frozen(self) -> None:
        decision = LocomotionDecision(
            target_mode=LocomotionMode.WHEEL,
            recommended_speed=1.0,
            reason="flat",
        )
        with pytest.raises(AttributeError):
            decision.recommended_speed = 0.0


# ---------------------------------------------------------------------------
# SearchDriveProfile
# ---------------------------------------------------------------------------


class TestSearchDriveProfile:
    def test_creation(self) -> None:
        profile = SearchDriveProfile(
            search_method=SearchMethod.PARALLEL_SWEEP,
            locomotion_mode=LocomotionMode.WHEEL,
            speed_scale=1.0,
            min_clearance_cm=30.0,
            replan_required=False,
            scan_density="NORMAL",
            reason="flat terrain, sweep pattern",
        )
        assert profile.speed_scale == 1.0
        assert profile.replan_required is False

    def test_replan_required(self) -> None:
        profile = SearchDriveProfile(
            search_method=SearchMethod.FRONTIER_EXPLORATION,
            locomotion_mode=LocomotionMode.STOP_AND_REPLAN,
            speed_scale=0.0,
            min_clearance_cm=50.0,
            replan_required=True,
            scan_density="HIGH",
            reason="rubble terrain detected",
        )
        assert profile.replan_required is True
