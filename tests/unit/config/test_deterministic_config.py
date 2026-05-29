"""TC-DETVAL-001/008: Deterministic config tests — FakeClock and ID generator."""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock


class TestFakeClock:
    def test_initial_value(self) -> None:
        clock = FakeClock(base_ms=1_700_000_000_000)
        assert clock.now_ms() == 1_700_000_000_000

    def test_advance(self) -> None:
        clock = FakeClock(base_ms=1_700_000_000_000)
        clock.advance(1000)
        assert clock.now_ms() == 1_700_000_001_000

    def test_multiple_advances(self) -> None:
        clock = FakeClock(base_ms=0)
        clock.advance(100)
        clock.advance(200)
        assert clock.now_ms() == 300

    def test_reset(self) -> None:
        clock = FakeClock(base_ms=1000)
        clock.advance(500)
        clock.reset()
        assert clock.now_ms() == 1000

    def test_deterministic_same_sequence(self) -> None:
        """TC-DETVAL-001: 동일 시퀀스에서 동일 결과."""
        clock1 = FakeClock(base_ms=0)
        clock2 = FakeClock(base_ms=0)
        clock1.advance(100)
        clock2.advance(100)
        assert clock1.now_ms() == clock2.now_ms()


class TestDeterministicIdGenerator:
    def test_sequential_ids(self) -> None:
        gen = DeterministicIdGenerator(prefix="EVT", seed=0)
        assert gen.next() == "EVT-000001"
        assert gen.next() == "EVT-000002"
        assert gen.next() == "EVT-000003"

    def test_custom_seed(self) -> None:
        gen = DeterministicIdGenerator(prefix="M", seed=99)
        assert gen.next() == "M-000100"

    def test_reset(self) -> None:
        gen = DeterministicIdGenerator(prefix="X", seed=0)
        gen.next()
        gen.next()
        gen.reset()
        assert gen.next() == "X-000001"

    def test_deterministic_same_sequence(self) -> None:
        """TC-DETVAL-008: 동일 seed에서 동일 ID 시퀀스."""
        gen1 = DeterministicIdGenerator(prefix="M", seed=0)
        gen2 = DeterministicIdGenerator(prefix="M", seed=0)
        ids1 = [gen1.next() for _ in range(5)]
        ids2 = [gen2.next() for _ in range(5)]
        assert ids1 == ids2
