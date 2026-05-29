"""Dependencies for FastAPI routes — provides singleton ApplicationService."""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from service.application_service import ApplicationService

# Instantiate a single static instance for the application lifespan
_clock = FakeClock(base_ms=1_700_000_000_000)
_id_gen = DeterministicIdGenerator("M", 0)
_app_service = ApplicationService(_clock, _id_gen)


def get_application_service() -> ApplicationService:
    """Dependency provider for ApplicationService singleton."""
    return _app_service


def get_clock() -> FakeClock:
    """Dependency provider for FakeClock."""
    return _clock


def get_id_generator() -> DeterministicIdGenerator:
    """Dependency provider for DeterministicIdGenerator."""
    return _id_gen
