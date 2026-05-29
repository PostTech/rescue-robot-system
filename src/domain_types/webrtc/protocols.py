"""Client-1: ROS2 + WebRTC Bridge interface contracts."""

from __future__ import annotations

from typing import Any, Protocol


class IWebRTCTrackSender(Protocol):
    """WebRTC Track sender interface for video, audio, and high-priority data tracks."""

    def send_video_packet(self, packet: Any) -> bool: ...

    def send_audio_packet(self, packet: Any) -> bool: ...
