"""Mock WebRTC Track Sender implementation.

Satisfies IWebRTCTrackSender protocol, registers packet delivery logs for testing,
and implements dynamic stream/track priority ordering based on bandwidth QoS specs.
"""

from __future__ import annotations

from typing import Any


class MockTrackSender:
    """Mock implementation of the IWebRTCTrackSender interface.

    Allows deterministic validation of track transmissions and supports track priority sorting.
    """

    # Specified track/stream priorities (P0 to P4)
    TRACK_PRIORITY_ORDER = {
        "Control": 0,
        "Thermal": 1,
        "RGB": 2,
        "Audio": 3,
        "PointCloud": 4,
    }

    def __init__(self) -> None:
        self.sent_video_packets: list[Any] = []
        self.sent_audio_packets: list[Any] = []

    def send_video_packet(self, packet: Any) -> bool:
        """Simulates transmission of video packet (e.g. Thermal or RGB frame)."""
        self.sent_video_packets.append(packet)
        return True

    def send_audio_packet(self, packet: Any) -> bool:
        """Simulates transmission of audio packet (e.g. Robot or Environment audio)."""
        self.sent_audio_packets.append(packet)
        return True

    def sort_tracks_by_priority(self, tracks: list[str]) -> list[str]:
        """Sorts a list of track names/types based on the strict QoS specifications.

        Priority order: Control > Thermal > RGB > Audio > PointCloud
        """
        return sorted(tracks, key=lambda track: self.TRACK_PRIORITY_ORDER.get(track, 99))
