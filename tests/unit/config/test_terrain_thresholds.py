"""Tests for terrain_thresholds config."""

from __future__ import annotations

import pytest

from config.terrain_thresholds import DEFAULT_TERRAIN_THRESHOLDS, TerrainThresholds


class TestTerrainThresholds:
    def test_default_slope_thresholds(self) -> None:
        t = DEFAULT_TERRAIN_THRESHOLDS
        assert t.mild_slope_max < t.steep_slope_max < t.cliff_slope_min

    def test_default_traversability_ordering(self) -> None:
        t = DEFAULT_TERRAIN_THRESHOLDS
        assert t.stop_threshold < t.replan_min < t.caution_min < t.passable_min

    def test_default_speed_ordering(self) -> None:
        t = DEFAULT_TERRAIN_THRESHOLDS
        assert t.crawl_speed < t.slow_speed < t.normal_speed

    def test_custom_thresholds(self) -> None:
        t = TerrainThresholds(mild_slope_max=10.0, steep_slope_max=25.0)
        assert t.mild_slope_max == 10.0
        assert t.steep_slope_max == 25.0

    def test_frozen(self) -> None:
        with pytest.raises(AttributeError):
            DEFAULT_TERRAIN_THRESHOLDS.normal_speed = 2.0
