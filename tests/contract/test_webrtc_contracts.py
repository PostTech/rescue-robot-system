"""Contract tests for MockTrackSender verifying interface signature and track priority ordering."""

from __future__ import annotations

import inspect

from adapters.webrtc.mock_track_sender import MockTrackSender


class TestWebRTCContracts:
    def test_tc_webrtc_001_mock_track_sender_contract(self) -> None:
        """TC-WEBRTC-001: Verify MockTrackSender implements the IWebRTCTrackSender Protocol contract."""
        sender = MockTrackSender()

        # 1. Structural contract checking (Duck Typing signature verify)
        assert hasattr(sender, "send_video_packet")
        assert hasattr(sender, "send_audio_packet")

        # Verify send_video_packet signature accepts packet and returns bool
        sig_video = inspect.signature(sender.send_video_packet)
        assert "packet" in sig_video.parameters

        # Verify send_audio_packet signature accepts packet and returns bool
        sig_audio = inspect.signature(sender.send_audio_packet)
        assert "packet" in sig_audio.parameters

        # 2. Functional verify
        assert sender.send_video_packet("mock-thermal-frame") is True
        assert sender.send_audio_packet("mock-audio-frame") is True

        assert len(sender.sent_video_packets) == 1
        assert sender.sent_video_packets[0] == "mock-thermal-frame"

        assert len(sender.sent_audio_packets) == 1
        assert sender.sent_audio_packets[0] == "mock-audio-frame"

    def test_tc_webrtc_002_track_priority_ordering(self) -> None:
        """TC-WEBRTC-002: Verify stream prioritization ordering rule is strictly applied."""
        sender = MockTrackSender()

        # Chaos unordered track types
        unordered_tracks = ["PointCloud", "Audio", "Thermal", "Control", "RGB"]

        # Expected priorities: Control > Thermal > RGB > Audio > PointCloud
        expected_sorted = ["Control", "Thermal", "RGB", "Audio", "PointCloud"]

        sorted_tracks = sender.sort_tracks_by_priority(unordered_tracks)
        assert sorted_tracks == expected_sorted

        # Test with duplicate/partial values
        partial_tracks = ["Audio", "Control", "Audio", "PointCloud"]
        expected_partial = ["Control", "Audio", "Audio", "PointCloud"]
        assert sender.sort_tracks_by_priority(partial_tracks) == expected_partial
