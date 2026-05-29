"""TC-GUARD-001/002: Test beartype runtime type safety and gRPC process fault isolation."""

from __future__ import annotations

import pytest
from beartype.roar import BeartypeCallHintParamViolation

from adapters.ros.grpc_process_gateway import GrpcProcessGateway
from domain_types.mission import SearchMethod
from domain_types.terrain import LocomotionMode, TerrainAnalysisResult, TerrainClass, TraversabilityLevel
from service.search_drive_policy import decide_drive_profile


class TestBeartypeRuntimeGuard:
    """beartype 런타임 타입 가드 검증 테스트."""

    def test_beartype_param_type_violations(self) -> None:
        """When an invalid type is passed at runtime, beartype throws hint violation immediately."""
        terrain = TerrainAnalysisResult(
            terrain_class=TerrainClass.FLAT_OPEN,
            slope_degree=3.0,
            step_height_cm=1.0,
            roughness_score=0.1,
            obstacle_density=0.05,
            traversability_score=0.9,
            traversability_level=TraversabilityLevel.PASSABLE,
            traversable=True,
        )

        # 1. Standard execution passes
        profile = decide_drive_profile(terrain, SearchMethod.PARALLEL_SWEEP)
        assert profile.locomotion_mode == LocomotionMode.WHEEL

        # 2. Injecting illegal string to 'method' param violating SearchMethod enum type
        # Pydantic or Mypy is silent at runtime, but beartype intercepts immediately!
        with pytest.raises(BeartypeCallHintParamViolation):
            decide_drive_profile(terrain, "ILLEGAL_STRING_METHOD")


class TestGrpcProcessIsolationGuard:
    """gRPC 기반 마이크로서비스 프로세스 결함 격리 검증 테스트."""

    def test_remote_perception_isolation(self) -> None:
        """Isolated YOLO process failure is gracefully bypassed without main thread panic."""
        gateway = GrpcProcessGateway(target_address="127.0.0.1:50051")

        # 1. Success execution
        res = gateway.call_remote_yolo_inference("F-001", b"\x00\x01\x02")
        assert res["success"] is True
        assert res["detections"][0]["label"] == "VICTIM"

        # 2. Chaos Engineering: Simulates Remote YOLO Process Death
        gateway.inject_network_fault(1)
        res_fail = gateway.call_remote_yolo_inference("F-002", b"\x00")

        # Absolute fault isolation: main application thread is completely safe!
        assert res_fail["success"] is False
        assert "Remote Perception process (Client-2) is dead" in res_fail["error"]
        assert len(res_fail["detections"]) == 0
