"""Unit tests for the FastAPI REST API Server using TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.server import app
from service.mission_state_machine import MissionState


@pytest.fixture()
def client() -> TestClient:
    """Fixture providing TestClient instance."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Validate health check endpoint returns 200 and green status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "GREEN"


def test_get_sop_profiles(client: TestClient) -> None:
    """Validate SOP profiles retrieval is available."""
    response = client.get("/api/sop/profiles")
    assert response.status_code == 200
    profiles = response.json()
    assert len(profiles) == 3
    assert profiles[0]["id"] == "mountain_missing_person"


def test_full_api_mission_flow(client: TestClient) -> None:
    """Validate full mission lifecycle flow via REST endpoints:

    Create -> Approve -> Start -> Tick -> Analyze Terrain/Detection -> Stop.
    """
    # 1. Create Mission Request
    req_payload = {
        "request_id": "REQ-API-001",
        "operator_id": "OP-API",
        "mission_name": "API Flow Test",
        "search_area": {
            "area_type": "POLYGON",
            "coordinates": [
                {"x": 0.0, "y": 0.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0},
                {"x": 10.0, "y": 0.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0},
                {"x": 10.0, "y": 10.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            ],
            "frame_id": "map",
        },
        "search_method": "PARALLEL_SWEEP",
        "sop_profile_id": "mountain_missing_person",
        "priority": "HIGH",
        "created_at_ms": 1700000000000,
    }
    response = client.post("/api/missions", json=req_payload)
    assert response.status_code == 201
    draft = response.json()
    assert draft["mission_id"] is not None
    mission_id = draft["mission_id"]

    # 2. List Missions
    response = client.get("/api/missions")
    assert response.status_code == 200
    missions_list = response.json()
    assert len(missions_list) >= 1
    assert any(m["mission_id"] == mission_id for m in missions_list)

    # 3. Get Mission Details (Draft)
    response = client.get(f"/api/missions/{mission_id}")
    assert response.status_code == 200
    details = response.json()
    assert details["status"] == MissionState.DRAFT
    assert len(details["search_area"]["coordinates"]) == 3

    # 4. Approve Mission Plan
    response = client.post(f"/api/missions/{mission_id}/approve", json={"approver": "FIELD_CDR"})
    assert response.status_code == 200
    plan = response.json()
    assert plan["approved_by"] == "FIELD_CDR"

    # 5. Start Mission
    response = client.post(f"/api/missions/{mission_id}/start")
    assert response.status_code == 200
    assert response.json()["state"] == MissionState.ACTIVE

    # 6. Simulate Telemetry: Process Terrain Scan
    terrain_payload = {
        "slope": 15.0,
        "step_height": 2.5,
        "roughness": 0.15,
        "obstacle_density": 0.1,
        "traversability": 0.8,
    }
    response = client.post(f"/api/terrain/{mission_id}/analyze", json=terrain_payload)
    assert response.status_code == 200
    t_res = response.json()
    assert t_res["traversable"] is True
    assert t_res["slope_degree"] == 15.0

    # 7. Get Terrain Log History
    response = client.get(f"/api/terrain/{mission_id}/history")
    assert response.status_code == 200
    t_history = response.json()
    assert len(t_history) == 1
    assert t_history[0]["slope_degree"] == 15.0

    # 8. Simulate Telemetry: Multi-Sensor Detection
    detection_payload = {
        "results": [
            {
                "sensor_type": "THERMAL",
                "label": "VICTIM_ALIVE",
                "confidence": 0.94,
                "bounding_box": [50.0, 50.0, 20.0, 20.0],
                "timestamp_ms": 1700000010000,
            }
        ],
        "confidence_threshold": 0.6,
    }
    response = client.post(f"/api/detection/{mission_id}/analyze", json=detection_payload)
    assert response.status_code == 200
    det_res = response.json()
    assert det_res["detected"] is True
    assert det_res["primary_sensor"] == "THERMAL"

    # 9. Trigger Tick Simulation
    response = client.post(f"/api/missions/{mission_id}/tick")
    assert response.status_code == 200
    tick_details = response.json()
    # Ticking an ACTIVE mission should increase map coverage
    assert tick_details["status"] == MissionState.ACTIVE
    assert tick_details["map_coverage_ratio"] > 0.0

    # 10. Fetch Safety Status
    response = client.get("/api/safety/status")
    assert response.status_code == 200
    safety = response.json()
    assert safety["level"] == "NORMAL"
    assert safety["is_safe_to_operate"] is True

    # 11. Fetch Global Event History
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1

    # 12. Trigger Emergency Stop
    response = client.post(f"/api/missions/{mission_id}/emergency-stop")
    assert response.status_code == 200
    assert response.json()["state"] == MissionState.EMERGENCY_STOPPED

    # Safety status should now reflect Emergency Stop
    response = client.get("/api/safety/status")
    assert response.status_code == 200
    safety_after = response.json()
    assert safety_after["emergency_stopped"] is True
    assert safety_after["level"] == "EMERGENCY_STOP"


def test_invalid_mission_id_returns_errors(client: TestClient) -> None:
    """Validate requesting missing mission triggers correct status codes."""
    response = client.get("/api/missions/MISSING_ID")
    assert response.status_code == 404

    response = client.post("/api/missions/MISSING_ID/approve", json={"approver": "CDR"})
    assert response.status_code == 400
