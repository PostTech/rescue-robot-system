"""Fake ROS Envelope for Windows testing.

Simulates a ROS message container without rclpy dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FakeRosEnvelope:
    """Immutable fake ROS message envelope.

    Simulates sensor_msgs, geometry_msgs, etc. with plain Python dicts.
    """

    topic: str
    message_type: str
    timestamp_ms: int
    frame_id: str = "map"
    data: dict[str, object] = field(default_factory=dict)


def create_terrain_envelope(
    slope: float,
    step_height: float,
    roughness: float,
    obstacle_density: float,
    traversability: float,
    timestamp_ms: int = 0,
) -> FakeRosEnvelope:
    """Create a fake terrain analysis ROS envelope."""
    return FakeRosEnvelope(
        topic="/terrain/analysis",
        message_type="rescue_robot_msgs/TerrainAnalysis",
        timestamp_ms=timestamp_ms,
        data={
            "slope_degree": slope,
            "step_height_cm": step_height,
            "roughness_score": roughness,
            "obstacle_density": obstacle_density,
            "traversability_score": traversability,
        },
    )


def create_mission_command_envelope(
    mission_id: str,
    command: str,
    timestamp_ms: int = 0,
) -> FakeRosEnvelope:
    """Create a fake mission command ROS envelope."""
    return FakeRosEnvelope(
        topic="/mission/command",
        message_type="rescue_robot_msgs/MissionCommand",
        timestamp_ms=timestamp_ms,
        data={"mission_id": mission_id, "command": command},
    )
