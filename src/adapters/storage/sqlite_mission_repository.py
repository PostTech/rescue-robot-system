"""SQLite Mission Repository.

Implements IMissionRepository using SQLite for true file-based persistence,
resolving the memory loss vulnerability on server crash or restart.
"""

from __future__ import annotations

import json
import sqlite3

from domain_types.mission import MissionDraft, SearchMissionPlan, SearchMissionRequest


class SqliteMissionRepository:
    """File-based persistent storage for rescue robot missions using SQLite."""

    def __init__(self, db_path: str = "rescue_robot.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize SQLite tables for drafts and plans if not exist."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS drafts (
                    mission_id TEXT PRIMARY KEY,
                    request_json TEXT NOT None,
                    validation_status TEXT NOT None,
                    sop_constraints_json TEXT NOT None,
                    draft_snapshot_id TEXT NOT None
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS plans (
                    mission_id TEXT PRIMARY KEY,
                    search_area_json TEXT NOT None,
                    search_method TEXT NOT None,
                    approved_by TEXT NOT None,
                    approved_at_ms INTEGER NOT None,
                    plan_snapshot_id TEXT NOT None
                )
                """
            )
            conn.commit()

    def save_draft(self, draft: MissionDraft) -> None:
        # Serialize request data
        req = draft.request
        req_dict = {
            "request_id": req.request_id,
            "operator_id": req.operator_id,
            "mission_name": req.mission_name,
            "search_area": {
                "area_type": req.search_area.area_type,
                "frame_id": req.search_area.frame_id,
                "coordinates": [{"x": c.x, "y": c.y, "z": c.z} for c in req.search_area.coordinates]
                if req.search_area.coordinates
                else [],
            }
            if req.search_area
            else None,
            "search_method": req.search_method,
            "sop_profile_id": req.sop_profile_id,
            "priority": req.priority,
            "created_at_ms": req.created_at_ms,
        }

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO drafts
                (mission_id, request_json, validation_status, sop_constraints_json, draft_snapshot_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    draft.mission_id,
                    json.dumps(req_dict),
                    draft.validation_status,
                    json.dumps(draft.sop_constraints),
                    draft.draft_snapshot_id,
                ),
            )
            conn.commit()

    def save_plan(self, plan: SearchMissionPlan) -> None:
        # Serialize search area coordinates
        area = plan.search_area
        area_dict = (
            {
                "area_type": area.area_type,
                "frame_id": area.frame_id,
                "coordinates": [{"x": c.x, "y": c.y, "z": c.z} for c in area.coordinates]
                if area.coordinates
                else [],
            }
            if area
            else None
        )

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO plans
                (mission_id, search_area_json, search_method, approved_by, approved_at_ms, plan_snapshot_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    plan.mission_id,
                    json.dumps(area_dict),
                    plan.search_method,
                    plan.approved_by,
                    plan.approved_at_ms,
                    plan.plan_snapshot_id,
                ),
            )
            conn.commit()

    def get_draft(self, mission_id: str) -> MissionDraft | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM drafts WHERE mission_id = ?", (mission_id,)
            ).fetchone()
            if not row:
                return None

            # Reconstruct request DTO
            req_data = json.loads(row["request_json"])

            # Lazy imports to avoid circular dependency
            from domain_types.common import Pose3D
            from domain_types.mission import SearchArea

            coords = []
            if req_data["search_area"] and req_data["search_area"]["coordinates"]:
                for c in req_data["search_area"]["coordinates"]:
                    coords.append(Pose3D(c["x"], c["y"], c["z"], 0.0, 0.0, 0.0))

            area = (
                SearchArea(
                    area_type=req_data["search_area"]["area_type"],
                    coordinates=tuple(coords),
                    frame_id=req_data["search_area"]["frame_id"],
                )
                if req_data["search_area"]
                else None
            )

            request = SearchMissionRequest(
                request_id=req_data["request_id"],
                operator_id=req_data["operator_id"],
                mission_name=req_data["mission_name"],
                search_area=area,
                search_method=req_data["search_method"],
                sop_profile_id=req_data["sop_profile_id"],
                priority=req_data["priority"],
                created_at_ms=req_data["created_at_ms"],
            )

            return MissionDraft(
                mission_id=row["mission_id"],
                request=request,
                validation_status=row["validation_status"],
                sop_constraints=json.loads(row["sop_constraints_json"]),
                draft_snapshot_id=row["draft_snapshot_id"],
            )

    def get_plan(self, mission_id: str) -> SearchMissionPlan | None:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM plans WHERE mission_id = ?", (mission_id,)).fetchone()
            if not row:
                return None

            # Reconstruct SearchArea
            area_data = json.loads(row["search_area_json"])
            from domain_types.common import Pose3D
            from domain_types.mission import SearchArea

            coords = []
            if area_data and area_data["coordinates"]:
                for c in area_data["coordinates"]:
                    coords.append(Pose3D(c["x"], c["y"], c["z"], 0.0, 0.0, 0.0))

            area = (
                SearchArea(
                    area_type=area_data["area_type"],
                    coordinates=tuple(coords),
                    frame_id=area_data["frame_id"],
                )
                if area_data
                else None
            )

            return SearchMissionPlan(
                mission_id=row["mission_id"],
                search_area=area,
                search_method=row["search_method"],
                approved_by=row["approved_by"],
                approved_at_ms=row["approved_at_ms"],
                plan_snapshot_id=row["plan_snapshot_id"],
            )

    def list_drafts(self) -> list[MissionDraft]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT mission_id FROM drafts").fetchall()
            drafts = []
            for r in rows:
                d = self.get_draft(r["mission_id"])
                if d:
                    drafts.append(d)
            return drafts

    def list_plans(self) -> list[SearchMissionPlan]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT mission_id FROM plans").fetchall()
            plans = []
            for r in rows:
                p = self.get_plan(r["mission_id"])
                if p:
                    plans.append(p)
            return plans

    def clear(self) -> None:
        """Clear all table records for test suite cleanup."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM drafts")
            conn.execute("DELETE FROM plans")
            conn.commit()
