"""FastAPI router for Asynchronous Automated SAR Demo Scenarios."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_application_service
from api.websocket_manager import manager
from domain_types.common import Pose3D
from domain_types.events import BaseEvent, EventType
from domain_types.mission import SearchArea, SearchAreaType, SearchMethod, SearchMissionRequest
from domain_types.terrain import LocomotionMode
from service.application_service import ApplicationService
from service.mock_detector import DetectionLabel, DetectionResult

router = APIRouter(prefix="/api/demo", tags=["demo"])

# Global reference to keep track of active background demo tasks to prevent overlap
_active_demo_task: asyncio.Task[None] | None = None


def broadcast_stage_description(stage_num: int, text: str) -> None:
    """Helper to broadcast scenario stage explanations to frontend WebSocket clients."""
    manager.broadcast_json_sync("demo.stage", {"stage": stage_num, "description": text})


async def run_mountain_scenario(app: ApplicationService) -> None:
    """Scenario 1: Mountain Search & Success (WHEEL -> TRACK -> WHEEL & Complete)"""
    try:
        broadcast_stage_description(1, "산악 실종 사고 SAR 드래프트 임무를 자동 생성 중입니다...")
        await asyncio.sleep(1.5)

        # 1. Create Mission Request
        req = SearchMissionRequest(
            request_id="REQ-MNT-DEMO",
            operator_id="OP-AUTO-DASH",
            mission_name="[시연] 산악 사고 실종자 정밀 수색",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(-12.0, -8.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(15.0, -4.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(3.0, 18.0, 0.0, 0.0, 0.0, 0.0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.GRID_COVERAGE,
            sop_profile_id="mountain_missing_person",
            priority="HIGH",
            created_at_ms=app._clock.now_ms(),
        )
        draft = app.create_mission(req)
        broadcast_stage_description(
            2,
            f"드래프트 {draft.mission_id} 생성 완료. 적용된 SOP 제약조건: 배터리 20% 보존, 최대 경사 25°.",
        )
        await asyncio.sleep(1.8)

        # 2. Approve Plan
        app.approve_mission(draft.mission_id, "COMMANDER-DASHBOARD")
        broadcast_stage_description(3, "현장 지휘관 서명 승인 완료. 정식 미션 탐색 계획 수립.")
        await asyncio.sleep(1.5)

        # 3. Start Execution
        app.start_mission(draft.mission_id)
        broadcast_stage_description(
            4, "로봇 주행 개시! SLAM 맵 커버리지를 늘려가며 나선형 궤적 탐색을 가동합니다."
        )
        ctx = app.get_mission_context(draft.mission_id)
        await asyncio.sleep(1.8)

        # 4. Telemetry Loop
        # Step 4-1: Flat Open
        ctx.map_coverage_ratio = 0.2
        ctx.current_pose = Pose3D(3.5, 2.0, 0.0, 0.0, 0.0, 1.2)
        app.process_terrain(draft.mission_id, 3.0, 1.0, 0.02, 0.05, 0.95)
        broadcast_stage_description(
            5, "1단계 (평지): 평탄 지형 진입. 로봇 주행 장치: WHEEL (바퀴주행) 구동."
        )
        await asyncio.sleep(2.0)

        # Step 4-2: Steep Slope
        ctx.map_coverage_ratio = 0.5
        ctx.current_pose = Pose3D(8.0, 6.5, 0.0, 0.0, 0.0, 2.4)
        app.process_terrain(draft.mission_id, 28.0, 5.0, 0.15, 0.1, 0.65)
        broadcast_stage_description(
            6,
            "2단계 (급경사): 28° 경사지 감지. 로봇 안전 전이: 주행 장치를 TRACK (무한궤도)로 실시간 스위칭!",
        )
        await asyncio.sleep(2.5)

        # Step 4-3: Victim Detected
        ctx.map_coverage_ratio = 0.75
        ctx.current_pose = Pose3D(2.0, 11.0, 0.0, 0.0, 0.0, 3.1)
        det = DetectionResult(
            sensor_type="THERMAL",
            label=DetectionLabel.VICTIM_ALIVE,
            confidence=0.92,
            bounding_box=(120, 140, 45, 45),
            timestamp_ms=app._clock.now_ms(),
        )
        app.process_detections(draft.mission_id, [det])
        broadcast_stage_description(
            7, "🚨 실종 생존자 감지! 열화상 적외선 복합 센서가 92% 신뢰도로 인명을 포착했습니다!"
        )
        await asyncio.sleep(2.5)

        # Step 4-4: Flat return & Complete
        ctx.map_coverage_ratio = 1.0
        ctx.current_pose = Pose3D(1.0, 2.0, 0.0, 0.0, 0.0, 0.5)
        app.process_terrain(draft.mission_id, 2.0, 0.5, 0.01, 0.02, 0.98)
        app.complete_mission(draft.mission_id)
        broadcast_stage_description(
            8,
            "임무 구역 SLAM 100% 매핑 달성! 생존자 수색 임무를 성공적으로 종료하고 로봇 복귀를 하달합니다.",
        )

    except asyncio.CancelledError:
        print("[Demo Task] Mountain Scenario cancelled.")
    except Exception as e:
        print(f"[Demo Task] Mountain Error: {e}")


async def run_collapsed_scenario(app: ApplicationService) -> None:
    """Scenario 2: Collapsed Void & Safety Retreat (WHEEL -> CLIMB & Gas Alert -> Safe Retreat Abort)"""
    try:
        broadcast_stage_description(
            1, "재난 건물 붕괴 구조물 SAR 임무 드래프트를 자동 생성 중입니다..."
        )
        await asyncio.sleep(1.5)

        # 1. Create Mission Request
        req = SearchMissionRequest(
            request_id="REQ-COL-DEMO",
            operator_id="OP-AUTO-DASH",
            mission_name="[시연] 붕괴 건물 잔해 더미 인명 구조",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(-8.0, -8.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(10.0, -2.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(1.0, 12.0, 0.0, 0.0, 0.0, 0.0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.PARALLEL_SWEEP,
            sop_profile_id="collapsed_structure",
            priority="CRITICAL",
            created_at_ms=app._clock.now_ms(),
        )
        draft = app.create_mission(req)
        broadcast_stage_description(
            2,
            f"드래프트 {draft.mission_id} 생성 완료. 적용된 SOP 제약조건: 장애물 밀도 0.6 한계, 배터리 30% 보존.",
        )
        await asyncio.sleep(1.8)

        # 2. Approve Plan
        app.approve_mission(draft.mission_id, "COMMANDER-DASHBOARD")
        broadcast_stage_description(3, "붕괴 잔해물 내부 진입 계획 지휘관 서명 승인.")
        await asyncio.sleep(1.5)

        # 3. Start Execution
        app.start_mission(draft.mission_id)
        broadcast_stage_description(
            4, "로봇 잔해 구역 진입! 3D LiDAR와 복합 가스 센서 계측을 동시에 시작합니다."
        )
        ctx = app.get_mission_context(draft.mission_id)
        await asyncio.sleep(1.8)

        # 4. Telemetry Loop
        # Step 4-1: Rough Rubble
        ctx.map_coverage_ratio = 0.3
        ctx.current_pose = Pose3D(2.0, 1.5, 0.0, 0.0, 0.0, 0.8)
        app.process_terrain(draft.mission_id, 8.0, 18.0, 0.45, 0.4, 0.7)
        broadcast_stage_description(
            5,
            "1단계 (잔해더미): 파편 지대 돌입. 거칠기 지수 0.45 상승. 로봇 주행 전이: OBSTACLE_CLIMB (사족 크롤링) 스위칭.",
        )
        await asyncio.sleep(2.5)

        # Step 4-2: Multi-Sensor Detections
        ctx.map_coverage_ratio = 0.55
        ctx.current_pose = Pose3D(5.0, 4.0, 0.0, 0.0, 0.0, 1.9)
        det_thermal = DetectionResult(
            sensor_type="THERMAL",
            label=DetectionLabel.VICTIM_ALIVE,
            confidence=0.95,
            bounding_box=(200, 100, 30, 30),
            timestamp_ms=app._clock.now_ms(),
        )
        det_audio = DetectionResult(
            sensor_type="AUDIO",
            label=DetectionLabel.VICTIM_AUDIO,
            confidence=0.88,
            bounding_box=None,
            timestamp_ms=app._clock.now_ms(),
        )
        app.process_detections(draft.mission_id, [det_thermal, det_audio])
        broadcast_stage_description(
            6,
            "🚨 복합 생존 신호 탐지! 열화상 카메라(95%) 및 음향 센서(88% 구조 요청 소리)가 동시에 융합 감지되었습니다.",
        )
        await asyncio.sleep(2.5)

        # Step 4-3: Gas leak & Safety Safe Mode Trigger
        ctx.map_coverage_ratio = 0.7
        ctx.current_pose = Pose3D(3.0, 8.0, 0.0, 0.0, 0.0, 2.7)

        # Publish Gas Hazard event manually to event bus
        gas_event = BaseEvent(
            event_id=app._id_gen.next(),
            mission_id=draft.mission_id,
            robot_id="R-001",
            event_type=EventType.GAS_HAZARD,
            timestamp_ms=app._clock.now_ms(),
            source_module="mock_gas_sensor",
        )
        app._event_bus.publish(gas_event)

        broadcast_stage_description(
            7,
            "⚠️ 경보: 유독성 메탄 가스 유출 유발 감지! Safety Manager가 즉시 SAFE_MODE(2단계) 안전 제어를 하달합니다.",
        )
        await asyncio.sleep(2.5)

        # Step 4-4: Abort mission gracefully
        app.abort_mission(draft.mission_id)
        broadcast_stage_description(
            8,
            "임무 중단(ABORTED) 지령 송신! 가스 농도 증가에 따라 로봇 주행 모드를 STOP_AND_REPLAN으로 감속하고 안전 구역으로 자동 후퇴시킵니다.",
        )

    except asyncio.CancelledError:
        print("[Demo Task] Collapsed Scenario cancelled.")
    except Exception as e:
        print(f"[Demo Task] Collapsed Error: {e}")


async def run_tunnel_scenario(app: ApplicationService) -> None:
    """Scenario 3: Tunnel Hazard & E-STOP (WHEEL -> EDGE_FOLLOW & CO2 Gas Explode -> EMERGENCY_STOP)"""
    try:
        broadcast_stage_description(
            1, "침수 지형 터널 특수 SAR 임무 드래프트를 자동 생성 중입니다..."
        )
        await asyncio.sleep(1.5)

        # 1. Create Mission Request
        req = SearchMissionRequest(
            request_id="REQ-TNL-DEMO",
            operator_id="OP-AUTO-DASH",
            mission_name="[시연] 침수 터널 붕괴 위험 및 특수 가스 정밀 수색",
            search_area=SearchArea(
                area_type=SearchAreaType.POLYGON,
                coordinates=(
                    Pose3D(-15.0, -15.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(15.0, -15.0, 0.0, 0.0, 0.0, 0.0),
                    Pose3D(0.0, 15.0, 0.0, 0.0, 0.0, 0.0),
                ),
                frame_id="map",
            ),
            search_method=SearchMethod.CONTOUR_SEARCH,
            sop_profile_id="flooded_tunnel",
            priority="CRITICAL",
            created_at_ms=app._clock.now_ms(),
        )
        draft = app.create_mission(req)
        broadcast_stage_description(
            2,
            f"드래프트 {draft.mission_id} 생성 완료. 적용된 SOP 제약조건: 침수 수심 10cm 한계, 통신 음영 구역 주의.",
        )
        await asyncio.sleep(1.8)

        # 2. Approve Plan
        app.approve_mission(draft.mission_id, "COMMANDER-DASHBOARD")
        broadcast_stage_description(3, "터널 내부 가스 탐색 계획 승인. 광대역 라이더 맵 병합 가동.")
        await asyncio.sleep(1.5)

        # 3. Start Execution
        app.start_mission(draft.mission_id)
        broadcast_stage_description(
            4, "로봇 터널 입구 진입 완료! 벽면 유도 센서 제어를 개시합니다."
        )
        ctx = app.get_mission_context(draft.mission_id)
        await asyncio.sleep(1.8)

        # 4. Telemetry Loop
        # Step 4-1: Narrow Passage
        ctx.map_coverage_ratio = 0.4
        ctx.current_pose = Pose3D(-5.0, -5.0, 0.0, 0.0, 0.0, 0.78)

        # We manually update robot to show EDGE_FOLLOW (Crawler/Slow Safe)
        app._robot.set_locomotion(LocomotionMode.EDGE_FOLLOW, app._clock.now_ms())
        app.process_terrain(draft.mission_id, 1.0, 2.0, 0.05, 0.2, 0.85)

        broadcast_stage_description(
            5,
            "1단계 (협소구역): 좁은 침수 Lane 진입. 로봇 정밀 벽면 밀착 주행: EDGE_FOLLOW 모드 구동.",
        )
        await asyncio.sleep(2.5)

        # Step 4-2: Gas Explosion & EMERGENCY STOP
        ctx.map_coverage_ratio = 0.55
        ctx.current_pose = Pose3D(0.0, 0.0, 0.0, 0.0, 0.0, 1.57)

        # Publish Critical Gas Alert event manually to event bus, then call emergency stop
        gas_event = BaseEvent(
            event_id=app._id_gen.next(),
            mission_id=draft.mission_id,
            robot_id="R-001",
            event_type=EventType.GAS_HAZARD,
            timestamp_ms=app._clock.now_ms(),
            source_module="mock_gas_sensor",
        )
        app._event_bus.publish(gas_event)

        broadcast_stage_description(
            6,
            "⚠️ 치명적 위험 감지: 일산화탄소 CO2 수치 폭증 및 통신 음영 발생! E-STOP 차단을 연쇄 트리거합니다.",
        )
        await asyncio.sleep(2.0)

        # Trigger emergency stop
        app.emergency_stop(draft.mission_id)
        broadcast_stage_description(
            7,
            "🚨 비상 제동 강제 발령(EMERGENCY STOPPED)! 전체 시스템 락다운 및 로봇 하드웨어 물리 멈춤 실행!",
        )

    except asyncio.CancelledError:
        print("[Demo Task] Tunnel Scenario cancelled.")
    except Exception as e:
        print(f"[Demo Task] Tunnel Error: {e}")


@router.post("/start/{scenario}", status_code=status.HTTP_200_OK)
def start_demo_scenario(
    scenario: str,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, str]:
    """Start one of the three automated background SAR demonstration scenarios."""
    global _active_demo_task

    # 1. Abort existing active demo background task to avoid concurrency collision
    if _active_demo_task and not _active_demo_task.done():
        _active_demo_task.cancel()
        print("[Demo Router] Cancelled preceding demo task.")

    # 2. Reset Mock elements to ensure clean state
    app._robot.reset()
    app._safety.reset()

    # 3. Spawn the requested scenario coroutine in the background loop
    loop = asyncio.get_running_loop()
    if scenario == "mountain":
        _active_demo_task = loop.create_task(run_mountain_scenario(app))
    elif scenario == "collapsed":
        _active_demo_task = loop.create_task(run_collapsed_scenario(app))
    elif scenario == "tunnel":
        _active_demo_task = loop.create_task(run_tunnel_scenario(app))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown scenario type: {scenario}. Choose from mountain, collapsed, tunnel.",
        )

    return {
        "status": "STARTED",
        "scenario": scenario,
        "message": f"Demo scenario {scenario} has started in the background.",
    }


class VideoFramePayload(BaseModel):
    """Payload representing a base64 encoded raw thermal or RGB video frame."""

    frame_data: str
    sensor_type: str = "THERMAL"
    timestamp_ms: int | None = None


@router.post("/send-frame", status_code=status.HTTP_200_OK)
async def send_video_frame(
    payload: VideoFramePayload,
    app: ApplicationService = Depends(get_application_service),
) -> dict[str, str]:
    """Broadcast raw base64 frame payload to all dashboard WebSockets dynamically."""
    ts = payload.timestamp_ms or app._clock.now_ms()
    await manager.broadcast_json(
        "video.frame",
        {"frame_data": payload.frame_data, "sensor_type": payload.sensor_type, "timestamp_ms": ts},
    )
    return {"status": "BROADCASTED"}
