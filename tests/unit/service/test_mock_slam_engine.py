"""TC-SLAM-001/002: Mock SLAM engine tests."""

from __future__ import annotations

import pytest

from domain_types.common import Pose3D
from service.mock_slam_engine import MockSlamEngine


class TestMockSlamEngine:
    def test_tc_slam_001_fixed_pose(self) -> None:
        """TC-SLAM-001: Mock SLAM returns fixed pose."""
        slam = MockSlamEngine(initial_pose=Pose3D(1.0, 2.0, 0.0, 0.0, 0.0, 0.5))
        pose = slam.get_pose()
        assert pose.x == 1.0
        assert pose.y == 2.0
        assert pose.yaw == 0.5

    def test_tc_slam_002_failure_raises(self) -> None:
        """TC-SLAM-002: SLAM failure raises RuntimeError."""
        slam = MockSlamEngine()
        slam.inject_failure()
        with pytest.raises(RuntimeError, match="SLAM failure"):
            slam.get_pose()

    def test_failure_blocks_update(self) -> None:
        slam = MockSlamEngine()
        slam.inject_failure()
        with pytest.raises(RuntimeError):
            slam.update(1000)

    def test_map_update(self) -> None:
        slam = MockSlamEngine()
        update = slam.update(1000)
        assert update.cells_updated == 10
        assert update.map_coverage_ratio == 0.05
        update2 = slam.update(2000)
        assert update2.cells_updated == 20
        assert update2.map_coverage_ratio == 0.10

    def test_recover_from_failure(self) -> None:
        slam = MockSlamEngine()
        slam.inject_failure()
        assert slam.is_active is False
        slam.recover()
        assert slam.is_active is True
        pose = slam.get_pose()
        assert pose is not None

    def test_set_pose(self) -> None:
        slam = MockSlamEngine()
        new_pose = Pose3D(5.0, 5.0, 1.0, 0.0, 0.0, 1.57)
        slam.set_pose(new_pose)
        assert slam.get_pose() == new_pose

    def test_reset(self) -> None:
        slam = MockSlamEngine(initial_pose=Pose3D(10.0, 10.0, 0.0, 0.0, 0.0, 0.0))
        slam.inject_failure()
        slam.reset()
        assert slam.is_active is True
        assert slam.get_pose() == Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def test_deterministic(self) -> None:
        s1 = MockSlamEngine(initial_pose=Pose3D(1.0, 2.0, 0.0, 0.0, 0.0, 0.0))
        s2 = MockSlamEngine(initial_pose=Pose3D(1.0, 2.0, 0.0, 0.0, 0.0, 0.0))
        assert s1.get_pose() == s2.get_pose()
        assert s1.update(1000) == s2.update(1000)
