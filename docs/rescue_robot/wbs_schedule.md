# 재난 구조용 바퀴형 사족로봇 시스템 WBS 및 일정 계획

## 1. 목적

본 문서는 구현 단계를 작업 단위로 나누고, 산출물, 의존성, 완료 기준을 정의한다.

---

## 2. 일정 기준

실제 착수일이 정해지지 않았으므로 `T`를 프로젝트 시작일로 정의한다.

| 구간 | 의미 |
|---|---|
| T+0~2주 | 설계 기준선 확정 |
| T+3~6주 | Mock/TDD 및 Business Logic |
| T+7~12주 | 핵심 Adapter 통합 |
| T+13~18주 | Simulation 및 안정화 |
| T+19~24주 | Field Test 및 Acceptance |

---

## 3. WBS

| WBS | 작업 | 기간 | 주요 산출물 | 의존성 | 완료 기준 |
|---|---|---|---|---|---|
| 1.1 | 요구사항 확정 | T+0~1 | 요구사항 명세서 | 기존 문서 | P0/P1/P2 확정 |
| 1.2 | Interface Baseline | T+0~2 | Interface Spec, Schema | 1.1 | Python Protocol/Data Schema 확정 |
| 1.3 | ROS Layer Boundary | T+1~2 | ROS Layering Plan | 1.2 | Domain/Application ROS 독립성 기준 확정 |
| 1.4 | Environment Profile | T+1~2 | Environment Profile Plan | 1.2 | Windows 기본/ Linux ROS 전환 기준 확정 |
| 1.5 | Event Schema | T+1~2 | Event Catalog | 1.1 | Event Priority 정의 |
| 1.6 | Mission Creation Baseline | T+1~2 | Mission Creation Plan, Search Mission Schema | 1.1, 1.2 | 구역/방법/SOP 설정 Interface 확정 |
| 2.1 | Test Harness | T+3~4 | Scenario Runner, Mock Layer | 1.2 | Mock 기반 실행 가능 |
| 2.2 | Lint/CI/Layer Gate | T+3~4 | Ruff, mypy, Windows 기본 pytest, Layer Test Gate | 1.2 | ROS Runtime 없이 로컬/CI 통과 |
| 2.3 | Business Logic | T+4~6 | State Machine, Fusion Logic | 2.1 | Unit Test 통과 |
| 2.4 | Mission Creation Logic | T+4~6 | MissionCreationService, SearchAreaValidator, SOP Configurator Mock | 1.6, 2.1 | `TC-MISSION-*` 통과 |
| 2.5 | Terrain Driven Navigation Logic | T+4~6 | TerrainAnalyzer, SearchDrivePolicy, Terrain Fixture | 1.2, 2.1 | `TC-TERRAIN-*` 통과 |
| 3.1 | Detector Adapter | T+7~9 | Thermal/RGB/Audio Adapter | 2.3 | AI/WebRTC 분리 검증 |
| 3.2 | SLAM/Navigation Adapter | T+7~10 | SLAM, 3D LiDAR Terrain Analysis, Path Planning | 2.3, 2.5 | Localization ≥ 10Hz, Terrain Driven Navigation 검증 |
| 3.3 | WebRTC Adapter | T+9~11 | Track/DataChannel | 2.3 | Reconnect < 10 sec |
| 3.4 | Storage Adapter | T+10~12 | Local Save, Sync Queue | 2.3 | Critical Event Loss = 0 |
| 4.1 | Containerization | T+13~14 | Container Definition | 3.x | Health Check 통과 |
| 4.2 | Simulation Scenario | T+14~16 | Simulation Test Report | 3.x | P0 Scenario 통과 |
| 4.3 | Performance Tuning | T+16~18 | KPI Report | 4.2 | FPS/Latency 기준 만족 |
| 5.1 | Field Test 준비 | T+19~20 | Field SOP, Checklist | 4.2 | Safety Review 완료 |
| 5.2 | Field Test | T+20~23 | Field Test Report | 5.1 | Mission Success ≥ 95% |
| 5.3 | Acceptance | T+23~24 | Acceptance Report | 5.2 | Critical Failure 없음 |

---

## 4. 마일스톤

| Milestone | 목표 | 승인 기준 |
|---|---|---|
| M1 | 설계 기준선 확정 | 요구사항, Interface, Event Schema, Mission Creation Baseline 승인 |
| M2 | Mock 기반 핵심 로직 검증 | P0 Unit/Interface/Mission Creation/Terrain Test 통과 |
| M3 | 핵심 Adapter 통합 | Detector/SLAM/WebRTC/Storage 통합 |
| M4 | Simulation 통과 | 장애/복구/Local Autonomous 검증 |
| M5 | Field Test 통과 | KPI 및 Safety 기준 만족 |
| M6 | 운영 배포 승인 | Acceptance Report 승인 |

---

## 5. 관리 원칙

- P0 작업은 일정 지연 시에도 범위를 줄이지 않는다.
- P1/P2 작업은 M4 이후 조정 가능하다.
- Lint/Type Check 실패는 해당 Sprint 완료로 인정하지 않는다.
- Safety 관련 결함은 모든 기능 개발보다 우선 처리한다.
