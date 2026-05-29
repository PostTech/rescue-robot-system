"""SOP (Standard Operating Procedure) profile definitions.

Each profile provides defaults, constraints, and sensor priorities
for a specific disaster scenario.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from domain_types.mission import SearchMethod


@dataclass(frozen=True)
class SopProfile:
    """Immutable SOP profile for a disaster scenario."""

    profile_id: str
    name: str
    description: str
    recommended_methods: tuple[SearchMethod, ...]
    sensor_priority: tuple[str, ...]
    max_slope_degree: float
    gas_stop_enabled: bool
    requires_commander_approval: bool
    constraints: dict[str, object] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Pre-defined SOP profiles (from mission_creation_plan.md §6)
# ---------------------------------------------------------------------------

MOUNTAIN_MISSING_PERSON = SopProfile(
    profile_id="mountain_missing_person",
    name="산악 실종자 수색",
    description="산악 지형에서 실종자를 탐색하는 SOP",
    recommended_methods=(
        SearchMethod.CONTOUR_SEARCH,
        SearchMethod.EXPANDING_SQUARE,
        SearchMethod.SECTOR_SEARCH,
    ),
    sensor_priority=("thermal", "rgb", "audio"),
    max_slope_degree=35.0,
    gas_stop_enabled=False,
    requires_commander_approval=True,
)

COLLAPSED_STRUCTURE = SopProfile(
    profile_id="collapsed_structure",
    name="붕괴 구조물 탐색",
    description="붕괴된 건물 내부 요구조자 탐색 SOP",
    recommended_methods=(
        SearchMethod.FRONTIER_EXPLORATION,
        SearchMethod.SINGLE_FILE,
        SearchMethod.MANUAL_ASSISTED,
    ),
    sensor_priority=("thermal", "audio", "rgb"),
    max_slope_degree=20.0,
    gas_stop_enabled=True,
    requires_commander_approval=True,
)

TUNNEL_GAS_RISK = SopProfile(
    profile_id="tunnel_gas_risk",
    name="지하 공동구 가스 위험",
    description="가스 위험이 있는 지하 공동구 탐색 SOP",
    recommended_methods=(
        SearchMethod.TRACKLINE_SEARCH,
        SearchMethod.SINGLE_FILE,
    ),
    sensor_priority=("gas", "thermal", "rgb"),
    max_slope_degree=15.0,
    gas_stop_enabled=True,
    requires_commander_approval=True,
    constraints={"max_gas_co2_ppm": 5000, "retreat_on_gas": True},
)

_SOP_PROFILES: dict[str, SopProfile] = {
    MOUNTAIN_MISSING_PERSON.profile_id: MOUNTAIN_MISSING_PERSON,
    COLLAPSED_STRUCTURE.profile_id: COLLAPSED_STRUCTURE,
    TUNNEL_GAS_RISK.profile_id: TUNNEL_GAS_RISK,
}


def get_sop_profile(profile_id: str) -> SopProfile:
    """Retrieve an SOP profile by ID."""
    profile = _SOP_PROFILES.get(profile_id)
    if profile is None:
        raise ValueError(
            f"Unknown SOP profile: {profile_id!r}. Available: {list(_SOP_PROFILES.keys())}"
        )
    return profile


def list_sop_profiles() -> list[str]:
    """Return all available SOP profile IDs."""
    return list(_SOP_PROFILES.keys())
