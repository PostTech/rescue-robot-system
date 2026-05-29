"""Deterministic validation helpers.

Provides utility functions to create deterministic Mission Drafts
and SearchDriveProfiles for reproducible test results.
"""

from __future__ import annotations

from config.deterministic import DeterministicIdGenerator, FakeClock
from domain_types.mission import (
    MissionDraft,
    SearchMissionRequest,
)


def create_deterministic_draft(
    request: SearchMissionRequest,
    clock: FakeClock,
    id_gen: DeterministicIdGenerator,
    sop_constraints: dict[str, object] | None = None,
) -> MissionDraft:
    """Create a MissionDraft with deterministic ID and snapshot.

    Guarantees: same (request, clock state, id_gen state) => same draft.
    """
    mission_id = id_gen.next()
    snapshot_id = f"SNAP-{mission_id}-{clock.now_ms()}"

    return MissionDraft(
        mission_id=mission_id,
        request=request,
        validation_status="PENDING_APPROVAL",
        sop_constraints=sop_constraints or {},
        draft_snapshot_id=snapshot_id,
    )


def create_deterministic_storage_key(
    entity_type: str,
    entity_id: str,
    timestamp_ms: int,
) -> str:
    """Create a deterministic storage key.

    Guarantees: same inputs => same key.
    """
    return f"{entity_type}:{entity_id}:{timestamp_ms}"
