"""ROS message mapper.

Converts FakeRosEnvelope to Domain DTOs and vice versa.
No rclpy dependency.
"""

from __future__ import annotations

from adapters.ros.fake_ros_envelope import FakeRosEnvelope
from domain_types.terrain import TerrainAnalysisResult
from service.terrain_analyzer import analyze_terrain


def envelope_to_terrain_result(envelope: FakeRosEnvelope) -> TerrainAnalysisResult:
    """Convert a terrain analysis ROS envelope to a Domain DTO."""
    d = envelope.data
    return analyze_terrain(
        slope_degree=float(d["slope_degree"]),
        step_height_cm=float(d["step_height_cm"]),
        roughness_score=float(d["roughness_score"]),
        obstacle_density=float(d["obstacle_density"]),
        traversability_score=float(d["traversability_score"]),
    )


def terrain_result_to_envelope(
    result: TerrainAnalysisResult,
    timestamp_ms: int = 0,
) -> FakeRosEnvelope:
    """Convert a Domain DTO back to a fake ROS envelope."""
    return FakeRosEnvelope(
        topic="/terrain/analysis",
        message_type="rescue_robot_msgs/TerrainAnalysis",
        timestamp_ms=timestamp_ms,
        data={
            "slope_degree": result.slope_degree,
            "step_height_cm": result.step_height_cm,
            "roughness_score": result.roughness_score,
            "obstacle_density": result.obstacle_density,
            "traversability_score": result.traversability_score,
        },
    )
