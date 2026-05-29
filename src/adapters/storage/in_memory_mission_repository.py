"""In-memory mission repository.

Implements IMissionRepository for testing without external DB.
"""

from __future__ import annotations

from domain_types.mission import MissionDraft, SearchMissionPlan


class InMemoryMissionRepository:
    """Thread-safe in-memory implementation of IMissionRepository."""

    def __init__(self) -> None:
        self._drafts: dict[str, MissionDraft] = {}
        self._plans: dict[str, SearchMissionPlan] = {}

    def save_draft(self, draft: MissionDraft) -> None:
        self._drafts[draft.mission_id] = draft

    def save_plan(self, plan: SearchMissionPlan) -> None:
        self._plans[plan.mission_id] = plan

    def get_draft(self, mission_id: str) -> MissionDraft | None:
        return self._drafts.get(mission_id)

    def get_plan(self, mission_id: str) -> SearchMissionPlan | None:
        return self._plans.get(mission_id)

    def list_drafts(self) -> list[MissionDraft]:
        return list(self._drafts.values())

    def list_plans(self) -> list[SearchMissionPlan]:
        return list(self._plans.values())

    def clear(self) -> None:
        self._drafts.clear()
        self._plans.clear()
