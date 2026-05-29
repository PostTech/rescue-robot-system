"""TC-LAYER-003/005, TC-IF-003/060/061: Adapter contract tests."""

from __future__ import annotations

from adapters.ros.fake_ros_envelope import (
    create_mission_command_envelope,
    create_terrain_envelope,
)
from adapters.ros.message_mapper import (
    envelope_to_terrain_result,
    terrain_result_to_envelope,
)
from adapters.storage.in_memory_mission_repository import InMemoryMissionRepository
from adapters.webrtc.mock_data_channel import MockDataChannel
from domain_types.common import Pose3D
from domain_types.mission import (
    MissionDraft,
    SearchArea,
    SearchAreaType,
    SearchMethod,
    SearchMissionPlan,
    SearchMissionRequest,
)
from domain_types.terrain import TerrainClass


class TestFakeRosEnvelope:
    def test_terrain_envelope_creation(self) -> None:
        env = create_terrain_envelope(30.0, 10.0, 0.3, 0.1, 0.6, timestamp_ms=1000)
        assert env.topic == "/terrain/analysis"
        assert env.data["slope_degree"] == 30.0
        assert env.timestamp_ms == 1000

    def test_mission_command_envelope(self) -> None:
        env = create_mission_command_envelope("M-001", "START", timestamp_ms=2000)
        assert env.topic == "/mission/command"
        assert env.data["mission_id"] == "M-001"

    def test_envelope_is_frozen(self) -> None:
        env = create_terrain_envelope(10.0, 5.0, 0.2, 0.1, 0.8)
        import pytest

        with pytest.raises(AttributeError):
            env.topic = "/other"


class TestMessageMapper:
    def test_tc_if_060_envelope_to_terrain_result(self) -> None:
        """TC-IF-060: Fake ROS Envelope -> Domain DTO."""
        env = create_terrain_envelope(5.0, 2.0, 0.1, 0.05, 0.9)
        result = envelope_to_terrain_result(env)
        assert result.terrain_class == TerrainClass.FLAT_OPEN
        assert result.slope_degree == 5.0

    def test_roundtrip_conversion(self) -> None:
        env1 = create_terrain_envelope(40.0, 10.0, 0.3, 0.1, 0.5)
        result = envelope_to_terrain_result(env1)
        env2 = terrain_result_to_envelope(result, timestamp_ms=env1.timestamp_ms)
        assert env2.data["slope_degree"] == env1.data["slope_degree"]
        assert env2.data["traversability_score"] == env1.data["traversability_score"]

    def test_deterministic_conversion(self) -> None:
        env = create_terrain_envelope(25.0, 8.0, 0.4, 0.2, 0.6)
        r1 = envelope_to_terrain_result(env)
        r2 = envelope_to_terrain_result(env)
        assert r1 == r2


def _make_request() -> SearchMissionRequest:
    return SearchMissionRequest(
        request_id="REQ-001",
        operator_id="OP-001",
        mission_name="test",
        search_area=SearchArea(
            area_type=SearchAreaType.POLYGON,
            coordinates=(
                Pose3D(0, 0, 0, 0, 0, 0),
                Pose3D(1, 0, 0, 0, 0, 0),
                Pose3D(1, 1, 0, 0, 0, 0),
            ),
            frame_id="map",
        ),
        search_method=SearchMethod.PARALLEL_SWEEP,
        sop_profile_id="mountain_missing_person",
        priority="HIGH",
        created_at_ms=1_700_000_000_000,
    )


class TestInMemoryMissionRepository:
    def test_tc_layer_005_save_and_get_draft(self) -> None:
        """TC-LAYER-005: Storage adapter save/retrieve."""
        repo = InMemoryMissionRepository()
        draft = MissionDraft(
            mission_id="M-001", request=_make_request(), validation_status="PENDING_APPROVAL"
        )
        repo.save_draft(draft)
        assert repo.get_draft("M-001") is draft
        assert repo.get_draft("NONEXISTENT") is None

    def test_save_and_get_plan(self) -> None:
        repo = InMemoryMissionRepository()
        req = _make_request()
        plan = SearchMissionPlan(
            mission_id="M-001",
            search_area=req.search_area,
            search_method=req.search_method,
            approved_by="CMDR",
            approved_at_ms=1_700_000_001_000,
            plan_snapshot_id="SNAP-1",
        )
        repo.save_plan(plan)
        assert repo.get_plan("M-001") is plan

    def test_list_drafts(self) -> None:
        repo = InMemoryMissionRepository()
        repo.save_draft(
            MissionDraft(
                mission_id="M-001", request=_make_request(), validation_status="PENDING_APPROVAL"
            )
        )
        repo.save_draft(
            MissionDraft(mission_id="M-002", request=_make_request(), validation_status="DRAFT")
        )
        assert len(repo.list_drafts()) == 2

    def test_clear(self) -> None:
        repo = InMemoryMissionRepository()
        repo.save_draft(
            MissionDraft(mission_id="M-001", request=_make_request(), validation_status="DRAFT")
        )
        repo.clear()
        assert len(repo.list_drafts()) == 0


class TestMockDataChannel:
    def test_tc_if_061_send_receive(self) -> None:
        """TC-IF-061: Mock WebRTC DataChannel send/receive."""
        ch = MockDataChannel(channel_id="ch-01")
        assert ch.send({"type": "CONTROL", "command": "START"}) is True
        assert len(ch.sent_messages) == 1
        ch.receive({"type": "EVENT", "event": "ACK"})
        assert len(ch.received_messages) == 1

    def test_send_when_closed(self) -> None:
        ch = MockDataChannel(channel_id="ch-02")
        ch.close()
        assert ch.send({"type": "CONTROL"}) is False
        assert len(ch.sent_messages) == 0

    def test_reset(self) -> None:
        ch = MockDataChannel(channel_id="ch-03")
        ch.send({"type": "TEST"})
        ch.close()
        ch.reset()
        assert ch.is_open is True
        assert len(ch.sent_messages) == 0
