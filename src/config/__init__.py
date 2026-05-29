# Config Layer — Threshold, Profile, Feature Flag
# 이 계층은 Types만 import할 수 있습니다. Service/UI import 금지.
"""Public re-exports for the ``config`` package."""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from config.mission_policy import (
    TERRAIN_METHOD_COMPATIBILITY,
    SearchAreaPolicy,
    is_method_compatible,
)
from config.runtime_profile import (
    DEV_WINDOWS_LOCAL,
    TARGET_LINUX_ROS,
    AdapterMode,
    RuntimeProfile,
    RuntimeProfileName,
    get_profile,
)
from config.sop_profiles import (
    COLLAPSED_STRUCTURE,
    MOUNTAIN_MISSING_PERSON,
    TUNNEL_GAS_RISK,
    SopProfile,
    get_sop_profile,
    list_sop_profiles,
)
from config.terrain_thresholds import DEFAULT_TERRAIN_THRESHOLDS, TerrainThresholds

__all__ = [
    # runtime
    "RuntimeProfileName",
    "AdapterMode",
    "RuntimeProfile",
    "DEV_WINDOWS_LOCAL",
    "TARGET_LINUX_ROS",
    "get_profile",
    # mission policy
    "SearchAreaPolicy",
    "TERRAIN_METHOD_COMPATIBILITY",
    "is_method_compatible",
    # terrain
    "TerrainThresholds",
    "DEFAULT_TERRAIN_THRESHOLDS",
    # sop
    "SopProfile",
    "MOUNTAIN_MISSING_PERSON",
    "COLLAPSED_STRUCTURE",
    "TUNNEL_GAS_RISK",
    "get_sop_profile",
    "list_sop_profiles",
    # deterministic
    "FakeClock",
    "DeterministicIdGenerator",
]
