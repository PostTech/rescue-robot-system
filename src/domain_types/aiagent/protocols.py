"""Server-4: AI Agent / SOP interface contracts."""

from __future__ import annotations

from typing import Any, Protocol

from domain_types.mission import (
    MissionSetupRecommendation,
    SearchMissionRequest,
)


class ISopMissionConfigurator(Protocol):
    """SOP-based mission configuration recommender (never starts missions)."""

    def apply_profile(self, request: SearchMissionRequest) -> MissionSetupRecommendation: ...


class ISopAgent(Protocol):
    """SOP AI agent – generates text recommendations from context."""

    def generate(self, context: Any) -> str: ...
