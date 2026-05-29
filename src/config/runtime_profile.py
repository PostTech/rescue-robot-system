"""Runtime profile configuration.

Defines environment profiles for dev-windows-local and target-linux-ros.
Determines which adapters (mock vs real) are active.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RuntimeProfileName(StrEnum):
    """Supported runtime environment profiles."""

    DEV_WINDOWS_LOCAL = "dev-windows-local"
    TARGET_LINUX_ROS = "target-linux-ros"


class AdapterMode(StrEnum):
    """Whether to use mock or real adapter implementations."""

    MOCK = "mock"
    REAL = "real"


@dataclass(frozen=True)
class RuntimeProfile:
    """Immutable runtime profile that controls adapter selection and test scope."""

    name: RuntimeProfileName
    ros_runtime_enabled: bool
    adapter_mode: AdapterMode
    test_exclude_patterns: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Pre-defined profiles
# ---------------------------------------------------------------------------

DEV_WINDOWS_LOCAL = RuntimeProfile(
    name=RuntimeProfileName.DEV_WINDOWS_LOCAL,
    ros_runtime_enabled=False,
    adapter_mode=AdapterMode.MOCK,
    test_exclude_patterns=("ros_runtime", "sensor_hw", "field_test"),
)

TARGET_LINUX_ROS = RuntimeProfile(
    name=RuntimeProfileName.TARGET_LINUX_ROS,
    ros_runtime_enabled=True,
    adapter_mode=AdapterMode.REAL,
    test_exclude_patterns=(),
)

_PROFILES: dict[str, RuntimeProfile] = {
    DEV_WINDOWS_LOCAL.name: DEV_WINDOWS_LOCAL,
    TARGET_LINUX_ROS.name: TARGET_LINUX_ROS,
}


def get_profile(name: str = "dev-windows-local") -> RuntimeProfile:
    """Retrieve a runtime profile by name. Defaults to dev-windows-local."""
    profile = _PROFILES.get(name)
    if profile is None:
        raise ValueError(f"Unknown runtime profile: {name!r}. Available: {list(_PROFILES.keys())}")
    return profile
