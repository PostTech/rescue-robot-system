"""Server-1: Mission Core interface contracts."""

from __future__ import annotations

from typing import Protocol

from domain_types.mission import (
    MissionDraft,
    SearchMissionPlan,
    SearchMissionRequest,
)


class IMissionCreationService(Protocol):
    """Creates and manages mission drafts."""

    def create_draft(self, request: SearchMissionRequest) -> MissionDraft: ...


class IMissionRepository(Protocol):
    """Persists mission drafts and approved plans."""

    def save_draft(self, draft: MissionDraft) -> None: ...

    def save_plan(self, plan: SearchMissionPlan) -> None: ...

    def get_draft(self, mission_id: str) -> MissionDraft | None: ...

    def get_plan(self, mission_id: str) -> SearchMissionPlan | None: ...

    def list_drafts(self) -> list[MissionDraft]: ...

    def list_plans(self) -> list[SearchMissionPlan]: ...

    def clear(self) -> None: ...
