"""Deterministic test support configuration.

Provides FakeClock and deterministic ID generators to ensure
reproducible test results per deterministic_validation_plan.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeClock:
    """Deterministic clock for testing — advances only when explicitly told.

    Usage::

        clock = FakeClock(base_ms=1700000000000)
        ts1 = clock.now_ms()    # 1700000000000
        clock.advance(1000)
        ts2 = clock.now_ms()    # 1700000001000
    """

    base_ms: int = 1_700_000_000_000
    _offset: int = 0

    def now_ms(self) -> int:
        """Return the current fake timestamp in milliseconds."""
        return self.base_ms + self._offset

    def advance(self, delta_ms: int) -> None:
        """Advance the clock by delta_ms milliseconds."""
        self._offset += delta_ms

    def reset(self) -> None:
        """Reset the clock offset to zero."""
        self._offset = 0


class DeterministicIdGenerator:
    """Generates predictable sequential IDs for testing.

    Usage::

        gen = DeterministicIdGenerator(prefix="EVT", seed=1)
        gen.next()  # "EVT-000001"
        gen.next()  # "EVT-000002"
    """

    def __init__(self, prefix: str = "ID", seed: int = 0) -> None:
        self._prefix = prefix
        self._counter = seed

    def next(self) -> str:
        """Generate the next sequential ID."""
        self._counter += 1
        return f"{self._prefix}-{self._counter:06d}"

    def reset(self, seed: int = 0) -> None:
        """Reset counter to the given seed."""
        self._counter = seed
