"""Tests for sop_profiles config."""

from __future__ import annotations

import pytest

from config.sop_profiles import (
    COLLAPSED_STRUCTURE,
    MOUNTAIN_MISSING_PERSON,
    TUNNEL_GAS_RISK,
    get_sop_profile,
    list_sop_profiles,
)
from domain_types.mission import SearchMethod


class TestSopProfiles:
    def test_mountain_profile(self) -> None:
        p = MOUNTAIN_MISSING_PERSON
        assert p.profile_id == "mountain_missing_person"
        assert SearchMethod.CONTOUR_SEARCH in p.recommended_methods
        assert p.sensor_priority[0] == "thermal"

    def test_collapsed_structure_profile(self) -> None:
        p = COLLAPSED_STRUCTURE
        assert p.gas_stop_enabled is True
        assert SearchMethod.FRONTIER_EXPLORATION in p.recommended_methods

    def test_tunnel_gas_risk_profile(self) -> None:
        p = TUNNEL_GAS_RISK
        assert p.gas_stop_enabled is True
        assert "max_gas_co2_ppm" in p.constraints
        assert p.requires_commander_approval is True

    def test_get_sop_profile(self) -> None:
        p = get_sop_profile("mountain_missing_person")
        assert p is MOUNTAIN_MISSING_PERSON

    def test_get_sop_profile_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown SOP profile"):
            get_sop_profile("nonexistent")

    def test_list_sop_profiles(self) -> None:
        profiles = list_sop_profiles()
        assert len(profiles) == 3
        assert "mountain_missing_person" in profiles

    def test_all_profiles_require_commander_approval(self) -> None:
        for pid in list_sop_profiles():
            p = get_sop_profile(pid)
            assert p.requires_commander_approval is True
