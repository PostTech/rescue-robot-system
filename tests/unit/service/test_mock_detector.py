"""TC-DETECT-001/002: Mock detector tests."""

from __future__ import annotations

from service.mock_detector import DetectionLabel, MockDetector


class TestMockDetector:
    def test_tc_detect_001_thermal_fixed_result(self) -> None:
        """TC-DETECT-001: Mock thermal detector returns fixed result."""
        det = MockDetector("THERMAL", DetectionLabel.VICTIM_ALIVE, 0.95)
        r = det.detect(timestamp_ms=1000)
        assert r.sensor_type == "THERMAL"
        assert r.label == DetectionLabel.VICTIM_ALIVE
        assert r.confidence == 0.95
        assert r.bounding_box is not None
        assert r.timestamp_ms == 1000

    def test_tc_detect_002_rgb_fixed_result(self) -> None:
        """TC-DETECT-002: Mock RGB detector returns fixed result."""
        det = MockDetector("RGB", DetectionLabel.VICTIM_BODY_PART, 0.8)
        r = det.detect()
        assert r.sensor_type == "RGB"
        assert r.label == DetectionLabel.VICTIM_BODY_PART

    def test_no_detection(self) -> None:
        det = MockDetector("AUDIO")
        r = det.detect()
        assert r.label == DetectionLabel.NO_DETECTION
        assert r.confidence == 0.0
        assert r.bounding_box is None

    def test_set_result(self) -> None:
        det = MockDetector("THERMAL")
        det.set_result(DetectionLabel.VICTIM_ALIVE, 0.9)
        r = det.detect()
        assert r.label == DetectionLabel.VICTIM_ALIVE
        assert r.confidence == 0.9

    def test_deterministic(self) -> None:
        det = MockDetector("THERMAL", DetectionLabel.VICTIM_ALIVE, 0.95)
        r1 = det.detect(1000)
        r2 = det.detect(1000)
        assert r1 == r2

    def test_result_is_frozen(self) -> None:
        import pytest

        det = MockDetector("THERMAL", DetectionLabel.VICTIM_ALIVE, 0.95)
        r = det.detect()
        with pytest.raises(AttributeError):
            r.confidence = 0.1
