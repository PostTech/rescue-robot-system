# Execution Order and Status

## Phase 1: Foundation (DONE) — 262 tests passed

| # | File | Status | Content |
|---|---|:---:|---|
| 01 | 01_DONE_pre_implementation_check | DONE | 구현 전 구조 점검 |
| 02 | 02_DONE_types_definition | DONE | Types 정의 (7 modules) |
| 03 | 03_DONE_types_tests_and_dependency_gate | DONE | Types 테스트 + TC-DEP |
| 04 | 04_DONE_config_definition | DONE | Config 정의 (5 modules) |
| 05 | 05_DONE_mission_creation_service | DONE | 탐색 임무 생성 Service |
| 06 | 06_DONE_terrain_drive_service | DONE | 지형 기반 주행 Service |
| 07 | 07_DONE_deterministic_validation | DONE | 결정론적 검증 |
| 08 | 08_DONE_ui_integration | DONE | ViewModel 연결 |
| 09 | 09_DONE_adapter_contracts | DONE | Adapter Contract |
| 10 | 10_DONE_final_verification | DONE | Phase 1 최종 검증 |
| 11 | 11_DONE_event_system_state_machine | DONE | Event Bus, State Machine, Safety |
| 12 | 12_DONE_mock_detector_fusion | DONE | Mock Detector, Fusion Logic |
| 13 | 13_DONE_mock_slam_navigation | DONE | Mock SLAM, Navigation, Controller |

---

## Phase 2: MVP Web Dashboard (TODO) ← CURRENT PRIORITY

| # | File | Status | Content | Output |
|---|---|:---:|---|---|
| **14** | 14_TODO_application_service_integration | **DONE** | Application Service 완성 | `src/service/application_service.py` |
| **15** | 15_TODO_fastapi_rest_api | **DONE** | FastAPI REST API | `src/api/` |
| **16** | 16_TODO_web_dashboard_frontend | **DONE** | Web Dashboard (Dark theme) | `src/web/` |
| **17** | 17_TODO_websocket_realtime | **DONE** | WebSocket 실시간 업데이트 | `src/api/routes_ws.py` |
| **18** | 18_TODO_demo_scenario_runner | **DONE** | 3개 SOP 시나리오 데모 | `src/api/routes_demo.py` |
| **19** | 19_TODO_terrain_detection_viz | **DONE** | 지형/탐지 시각화 | Canvas + Cards |
| **20** | 20_DONE_mvp_polish_launch | **DONE** | `python run_mvp.py` 한 줄 실행 | README + launcher |

---

## Phase 3: Quality & Extensions (DONE)

| # | File | Status | Content |
|---|---|:---:|---|
| 21 | 21_DONE_webrtc_mock_integration | **DONE** | Mock WebRTC Track/Control |
| 22 | 22_DONE_storage_integration | **DONE** | Event/Media Storage |
| 23 | 23_DONE_e2e_scenario_tests | **DONE** | SOP Scenario E2E Tests |
| 24 | 24_DONE_lint_typecheck_quality | **DONE** | ruff, mypy, Quality Gate |

---

## MVP Architecture

```text
Browser (Dashboard)
    ↕ fetch() + WebSocket
FastAPI Server (:8000)
    ↕ DI
ApplicationService
    ↕
┌────────────┬──────────┬──────────────┐
│ MissionSvc │ Terrain  │ Detector     │
│ StateMach  │ Analyzer │ Fusion       │
│ SafetyMgr  │ DrivePol │ SLAM/Nav     │
└────────────┴──────────┴──────────────┘
    ↕
Types → Config (deterministic)
```

## MVP Goal

```text
python run_mvp.py
→ FastAPI server starts on :8000
→ Browser opens dashboard
→ Click "Demo: Mountain Search" button
→ Watch mission flow in real-time
```
