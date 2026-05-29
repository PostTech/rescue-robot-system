"""Tests for runtime_profile config."""

from __future__ import annotations

import pytest

from config.runtime_profile import (
    DEV_WINDOWS_LOCAL,
    TARGET_LINUX_ROS,
    AdapterMode,
    RuntimeProfileName,
    get_profile,
)


class TestRuntimeProfile:
    def test_dev_windows_local_defaults(self) -> None:
        p = DEV_WINDOWS_LOCAL
        assert p.name == RuntimeProfileName.DEV_WINDOWS_LOCAL
        assert p.ros_runtime_enabled is False
        assert p.adapter_mode == AdapterMode.MOCK

    def test_target_linux_ros(self) -> None:
        p = TARGET_LINUX_ROS
        assert p.ros_runtime_enabled is True
        assert p.adapter_mode == AdapterMode.REAL

    def test_get_profile_default(self) -> None:
        p = get_profile()
        assert p.name == "dev-windows-local"

    def test_get_profile_by_name(self) -> None:
        p = get_profile("target-linux-ros")
        assert p.ros_runtime_enabled is True

    def test_get_profile_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown runtime profile"):
            get_profile("nonexistent")

    def test_frozen(self) -> None:
        with pytest.raises(AttributeError):
            DEV_WINDOWS_LOCAL.ros_runtime_enabled = True
