"""Mission approval guard.

Enforces that a MissionDraft cannot become a SearchMissionPlan
without Mission Commander approval.
"""

from __future__ import annotations

from domain_types.mission import MissionDraft, SearchMissionPlan


def approve_mission(
    draft: MissionDraft,
    approved_by: str,
    approved_at_ms: int,
    plan_snapshot_id: str,
) -> SearchMissionPlan:
    """Approve a mission draft and produce a frozen SearchMissionPlan.

    Args:
        draft: The validated MissionDraft to approve.
        approved_by: ID of the Mission Commander granting approval.
        approved_at_ms: Deterministic timestamp of approval.
        plan_snapshot_id: Deterministic snapshot ID.

    Raises:
        ValueError: If the draft is not in PENDING_APPROVAL status.
    """
    if draft.validation_status != "PENDING_APPROVAL":
        raise ValueError(
            f"Cannot approve draft in status '{draft.validation_status}'. "
            f"Expected 'PENDING_APPROVAL'."
        )

    return SearchMissionPlan(
        mission_id=draft.mission_id,
        search_area=draft.request.search_area,
        search_method=draft.request.search_method,
        approved_by=approved_by,
        approved_at_ms=approved_at_ms,
        plan_snapshot_id=plan_snapshot_id,
    )
