"""TC-DETECT-003/004/005, TC-DETVAL-002: Fusion logic tests."""

from __future__ import annotations

from service.fusion_logic import DecisionLevel, fuse_detections
from service.mock_detector import DetectionLabel, DetectionResult


def _thermal(conf: float = 0.95) -> DetectionResult:
    return DetectionResult("THERMAL", DetectionLabel.VICTIM_ALIVE, conf, (0.2, 0.2, 0.6, 0.6), 1000)


def _rgb(conf: float = 0.8) -> DetectionResult:
    return DetectionResult("RGB", DetectionLabel.VICTIM_BODY_PART, conf, (0.3, 0.3, 0.4, 0.4), 1000)


def _audio(conf: float = 0.6) -> DetectionResult:
    return DetectionResult("AUDIO", DetectionLabel.VICTIM_AUDIO, conf, None, 1000)


def _no_detect(sensor: str = "THERMAL") -> DetectionResult:
    return DetectionResult(sensor, DetectionLabel.NO_DETECTION, 0.0, None, 1000)


class TestFusionLogic:
    def test_tc_detect_003_thermal_plus_rgb(self) -> None:
        """TC-DETECT-003: Fusion combines thermal + RGB."""
        decision = fuse_detections([_thermal(), _rgb()])
        assert decision.detected is True
        assert len(decision.contributing_results) == 2

    def test_tc_detect_004_thermal_priority(self) -> None:
        """TC-DETECT-004: Thermal takes priority over RGB."""
        decision = fuse_detections([_rgb(0.99), _thermal(0.7)])
        assert decision.primary_sensor == "THERMAL"

    def test_tc_detect_005_below_threshold_rejected(self) -> None:
        """TC-DETECT-005: Below-threshold confidence is rejected."""
        decision = fuse_detections([_thermal(0.3), _rgb(0.2)], confidence_threshold=0.5)
        assert decision.detected is False
        assert decision.label == DetectionLabel.NO_DETECTION

    def test_single_thermal(self) -> None:
        decision = fuse_detections([_thermal(0.95)])
        assert decision.detected is True
        assert decision.decision_level == DecisionLevel.HIGH

    def test_medium_confidence(self) -> None:
        decision = fuse_detections([_thermal(0.75)])
        assert decision.decision_level == DecisionLevel.MEDIUM

    def test_low_confidence(self) -> None:
        decision = fuse_detections([_thermal(0.55)])
        assert decision.decision_level == DecisionLevel.LOW

    def test_all_no_detection(self) -> None:
        decision = fuse_detections([_no_detect("THERMAL"), _no_detect("RGB")])
        assert decision.detected is False

    def test_audio_only(self) -> None:
        decision = fuse_detections([_audio(0.7)])
        assert decision.detected is True
        assert decision.primary_sensor == "AUDIO"

    def test_tc_detval_002_deterministic(self) -> None:
        """TC-DETVAL-002: Same inputs produce same fusion result."""
        inputs = [_thermal(0.9), _rgb(0.8), _audio(0.6)]
        d1 = fuse_detections(inputs)
        d2 = fuse_detections(inputs)
        assert d1 == d2

    def test_empty_input(self) -> None:
        decision = fuse_detections([])
        assert decision.detected is False
