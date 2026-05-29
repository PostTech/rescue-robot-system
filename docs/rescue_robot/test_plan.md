# test_plan.md
# 재난 구조용 바퀴형 사족로봇 시스템
## Compact Test Plan

---

# 1. 목적

본 문서는 재난 구조용 바퀴형 사족로봇 시스템의 전체 테스트 전략을 정의한다.

통합 대상:

- TDD 전략
- Test Case
- Test Harness
- Simulation Test
- Field Test
- Acceptance Test

핵심 목적:

```text
1. Business Logic을 Middleware/HW 없이 먼저 검증
2. Mock 기반으로 장애와 상태 전이를 검증
3. Adapter 통합 후 ROS2/WebRTC/Storage를 검증
4. Simulation 이후 Field Test로 확장
5. Acceptance 기준으로 최종 운영 가능성 판단
```

---

# 2. 테스트 핵심 원칙

## 2.1 Safety First

우선순위:

```text
Emergency Stop
    >
Safe Mode
    >
Mission
    >
Performance
```

---

## 2.2 Windows Default Test Scope

현재 기본 작업 환경은 Windows이므로 기본 테스트는 ROS단까지 진행하지 않는다.

```text
Default Profile = dev-windows-local
```

Windows 기본 테스트 범위:

```text
Lint / Static Analysis
Layer Dependency Test
Unit Test
Interface Contract Test
Module Boundary Test
Mock 기반 Failure Test
```

Windows 기본 테스트 제외 범위:

```text
rclpy
ROS Runtime
ROS Node Launch
Real ROS Topic Publish/Subscribe
Sensor / Robot HW Runtime
```

---

## 2.3 Mock First

실제 장비 없이 먼저 검증한다.

```text
Mock Sensor
Mock Detector
Mock SLAM
Mock WebRTC
Mock Storage
Mock Robot Controller
```

---

## 2.4 Business Logic 독립 검증

Business Logic은 아래 시스템 없이 테스트 가능해야 한다.

```text
ROS2
WebRTC
DB
YOLO
SLAM
Robot HW
LLM/SOP Agent
```

---

## 2.5 ROS 계층 독립성 검증

Domain/Application 계층은 ROS Runtime 없이 테스트 가능해야 한다.

```text
Domain
    !=
rclpy / ROS Message / ROS Topic Name
```

Windows 기본 테스트에서는 실제 ROS Adapter Runtime까지 가지 않고, Fake Envelope와 Mapper Contract만 검증한다.

---

## 2.6 의존성 방향 검증 필수

코드 의존성 방향은 반드시 다음 순서를 지킨다.

```text
Types -> Config -> Service -> UI
```

검증 기준:

```text
Types는 Config/Service/UI를 import하지 않음
Config는 Service/UI를 import하지 않음
Service는 UI를 import하지 않음
UI는 DB Driver/ROS Runtime/Robot SDK를 직접 import하지 않음
```

---

## 2.7 Failure Injection 필수

테스트는 정상 시나리오뿐 아니라 장애 주입을 포함한다.

```text
Sensor Failure
AI Timeout
CUDA OOM
SLAM Drift
WebRTC Disconnect
DB Failure
Storage Full
Robot Control Timeout
```

---

## 2.8 Acceptance 중심 종료

최종 판단 기준은 기능 존재 여부가 아니라 실제 임무 수행 가능성이다.

```text
Feature Exists
    !=
Mission Capable
```

---

## 2.9 Lint / Static Analysis 필수

Python 구현물은 기능 테스트 전에 정적 품질 검사를 통과해야 한다.

```text
ruff check
ruff format --check
mypy
pytest tests/unit tests/contract tests/layer tests/dependency tests/module_boundary tests/mission_creation tests/terrain
```

Lint 실패는 테스트 실패로 간주하며, 예외는 Safety 또는 현장 Hotfix 상황에서만 승인 기록을 남기고 허용한다.

---

## 2.10 Deterministic Validation 필수

Windows 기본 테스트는 동일 입력에서 동일 결과를 생성해야 한다.

```text
FakeClock
Fixed Seed
Fixed Fixture
InMemoryRepository
Mock Adapter
Fake ROS Envelope
```

실제 시간, 실제 난수, 실제 네트워크, ROS Runtime, 외부 DB/API에 의존하지 않는다.

---

# 3. 테스트 단계

```text
Lint / Static Analysis
    ↓
Layer Dependency Test
    ↓
Dependency Direction Test
    ↓
Deterministic Validation
    ↓
Unit Test
    ↓
Interface Test
    ↓
Integration Test
    ↓
Failure Test
    ↓
Simulation Test
    ↓
Field Test
    ↓
Acceptance Test
```

---

# 4. 테스트 우선순위

| Priority | 영역 | 목적 |
|---|---|---|
| P0 | Safety | Emergency Stop / Safe Mode |
| P0 | Victim Decision | Thermal 우선 요구조자 판단 |
| P0 | Communication Failover | Local Autonomous 진입 |
| P0 | AI/WebRTC Isolation | AI 장애 시 영상 유지 |
| P0 | Control Authority | 승인 없는 제어 차단 |
| P0 | Code Quality Gate | Lint / Type Check 통과 |
| P0 | Layer Boundary | Domain/Application의 ROS 의존성 차단 |
| P0 | Deterministic Validation | 동일 입력에서 동일 Event/State/Output 보장 |
| P1 | Storage/Sync | Local Save 및 복구 후 Sync |
| P1 | SLAM/Navigation | Localization / Path Planning |
| P1 | Network Priority | Control/Event/Thermal 우선 |
| P2 | UI/SOP | Alert 및 권고 검증 |
| P2 | Multi Robot | Namespace / Map Sharing |

---

# 5. Test Harness 구조

## 5.1 전체 구조

```text
Test Scenario
    ↓
Fake Input Generator
    ↓
Mock Interface Layer
    ↓
Business Logic
    ↓
Event Bus
    ↓
State Machine
    ↓
Assertion Engine
    ↓
Test Report
```

---

## 5.2 Harness 구성 요소

| 구성 요소 | 역할 |
|---|---|
| Scenario Runner | 테스트 시나리오 실행 |
| Fake Sensor Generator | 가짜 센서 입력 생성 |
| Failure Injector | 장애 주입 |
| Event Recorder | Event 기록 |
| State Recorder | 상태 전이 기록 |
| Assertion Engine | 기대 결과 검증 |
| Report Generator | 결과 리포트 생성 |

---

## 5.3 Mock 대상

```text
MockThermalDetector
MockRGBDetector
MockAudioDetector
MockGasSensor
MockLiDAR
MockSLAM
MockNavigation
MockRobotController
MockWebRTC
MockDataChannel
MockDB
MockObjectStorage
MockLocalStorage
MockSOPAgent
MockUI
```

---

## 5.4 계층별 TDD / Harness 매트릭스

계층별 TDD 대상, Mock/Fake, Test Harness, 테스트 ID는 `layer_tdd_harness_matrix.md`를 기준으로 관리한다.

핵심 적용 범위:

| 계층 | 테스트 기준 |
|---|---|
| Domain / Business Logic | ROS Runtime 없이 Unit Test |
| Application / State Machine | Event 기반 상태 전이 Test |
| Interface | Protocol 기반 Contract Test |
| ROS Adapter Contract | Fake ROS Envelope ↔ Domain DTO Mapper Contract Test |
| WebRTC / Storage Adapter | Mock Adapter + Failure Injection |
| Client / Server Boundary | `TC-MOD-*` 분리 검증 |

---

## 5.5 함수 단위 테스트 범위

함수 단위 테스트는 `function_unit_test_plan.md`를 기준으로 결정 로직과 경계 로직에 집중한다.

필수 범위:

```text
TC-FUNC-DEC-*
TC-FUNC-BND-*
```

제외 범위:

```text
단순 getter/setter
단순 pass-through wrapper
실제 ROS Node 실행 함수
실제 DB/WebRTC 연결 함수
```

---

# 6. Unit Test

## 목적

개별 비즈니스 룰과 상태 전이를 검증한다.

---

## 주요 테스트

| Test ID | 목적 | 기대 결과 |
|---|---|---|
| TC-UNIT-001 | Thermal 우선 판단 | VictimCandidate 생성 |
| TC-UNIT-002 | RGB 보조 판단 | RGB 기반 후보 생성 |
| TC-UNIT-003 | Audio 보조 판단 | SuspiciousEvent 생성 |
| TC-UNIT-004 | Multi Sensor Fusion | High Confidence 후보 생성 |
| TC-UNIT-005 | Gas Hazard 우선 | Safe Mode 또는 Stop 권고 |
| TC-UNIT-011 | CommunicationState 전이 | CONNECTED → LOCAL_AUTONOMOUS |
| TC-UNIT-012 | Emergency Stop | 즉시 정지 |

---

## 함수 단위 테스트 매핑

| Test ID | 검증 |
|---|---|
| TC-FUNC-DEC-001 | Thermal 요구조자 판단 함수 |
| TC-FUNC-DEC-002 | RGB 보조 판단 함수 |
| TC-FUNC-DEC-003 | Audio help 판단 함수 |
| TC-FUNC-DEC-004 | Multi Sensor Fusion 함수 |
| TC-FUNC-DEC-005 | Gas Hazard 판단 함수 |
| TC-FUNC-DEC-006 | Locomotion Mode 결정 함수 |
| TC-FUNC-DEC-007 | Emergency Stop 우선순위 함수 |
| TC-FUNC-DEC-008 | Local Autonomous 진입 조건 함수 |
| TC-FUNC-DEC-010 | 탐색 방법 추천/선택 판단 함수 |
| TC-FUNC-DEC-012 | 지형 기반 주행 정책 판단 함수 |
| TC-FUNC-DEC-013 | 지형 기반 속도 제한 판단 함수 |
| TC-FUNC-BND-001 | Event Priority 정렬 함수 |
| TC-FUNC-BND-002 | State Transition Guard 함수 |
| TC-FUNC-BND-003 | Control Authority 검증 함수 |
| TC-FUNC-BND-004 | Storage Key 생성 함수 |
| TC-FUNC-BND-005 | Retry Backoff 계산 함수 |
| TC-FUNC-BND-006 | Sync Queue 순서 결정 함수 |
| TC-FUNC-BND-007 | DataChannel Priority 결정 함수 |
| TC-FUNC-BND-008 | Fake ROS Envelope Mapper 함수 |
| TC-FUNC-BND-010 | SearchArea Validation 함수 |
| TC-FUNC-BND-011 | Mission Approval Guard 함수 |
| TC-FUNC-BND-012 | SearchMissionRequest Validation 함수 |
| TC-FUNC-BND-013 | Search Grid 생성 함수 |
| TC-FUNC-BND-014 | TerrainAnalysisResult Validation 함수 |
| TC-FUNC-BND-015 | SearchMethod-Terrain Compatibility 함수 |

---

# 7. Interface Test

## 목적

Adapter 교체 가능성과 Interface 계약을 검증한다.

---

## 주요 테스트

| Test ID | Interface | 검증 |
|---|---|---|
| TC-IF-001 | IDetector | DetectionResult 반환 |
| TC-IF-002 | IDetector 교체 | Business Logic 변경 없음 |
| TC-IF-010 | IWebRTCTrackSender | 압축 패킷 Track 송신 |
| TC-IF-011 | IDataChannelSender | Event/Status/Control 송신 |
| TC-IF-020 | IRepository | 저장 계약 유지 |
| TC-IF-030 | IRobotController | Move/Stop 계약 유지 |
| TC-IF-040 | ISopAgent | Recommendation만 생성 |
| TC-IF-050 | IMissionCreationService | SearchMissionRequest → MissionDraft |
| TC-IF-051 | IMissionRepository | Mission Draft/Plan 저장 계약 |
| TC-IF-052 | ISopMissionConfigurator | SOP Profile → MissionSetupRecommendation |
| TC-IF-060 | ITerrainAnalyzer | PointCloud → TerrainAnalysisResult |
| TC-IF-061 | ISearchDrivePolicy | TerrainAnalysisResult + SearchMethod → SearchDriveProfile |

---

## ROS Layer Boundary Test

| Test ID | 검증 |
|---|---|
| TC-LAYER-001 | Domain Layer에서 `rclpy`, ROS Message import 없음 |
| TC-LAYER-002 | Application Service가 ROS Message를 직접 받지 않음 |
| TC-LAYER-003 | Fake ROS Envelope ↔ Domain DTO 변환 Contract 검증 |
| TC-LAYER-004 | ROS Runtime 없이 Business Logic Unit Test 실행 |
| TC-LAYER-005 | Mock Topic Timeout이 Business Logic 장애로 직접 전파되지 않고 Event로 변환 |

---

## Dependency Direction Test

| Test ID | 검증 |
|---|---|
| TC-DEP-001 | Types에서 Config/Service/UI import 없음 |
| TC-DEP-002 | Config에서 Service/UI import 없음 |
| TC-DEP-003 | Service에서 UI import 없음, `import ... from "../ui/..."` 발견 시 즉시 수정 요청 |
| TC-DEP-004 | UI에서 DB Driver/ROS Runtime/Robot SDK 직접 import 없음 |
| TC-DEP-005 | Types/Config/Service/UI 순환 의존성 없음 |
| TC-DEP-006 | 신규 기능은 Types 정의부터 시작 |

---

## Deterministic Validation Test

| Test ID | 검증 |
|---|---|
| TC-DETVAL-001 | FakeClock 기반 timestamp 고정 |
| TC-DETVAL-002 | Fixed seed 기반 Detection/Fusion 결과 고정 |
| TC-DETVAL-003 | Event priority 기반 처리 순서 고정 |
| TC-DETVAL-004 | 동일 시나리오의 State Snapshot 고정 |
| TC-DETVAL-005 | Fake ROS Envelope 기반 Mapper 결과 고정 |
| TC-DETVAL-006 | 동일 Event의 Storage Key 고정 |
| TC-DETVAL-007 | 동일 장애 시나리오의 Retry/Sync 순서 고정 |
| TC-DETVAL-008 | 동일 임무 생성 입력의 Mission Draft Snapshot 고정 |
| TC-DETVAL-009 | 동일 지형/탐색 방법 입력의 SearchDriveProfile 고정 |

---

# 8. Terrain Driven Navigation Test

## 목적

3D LiDAR 지형 분석 결과와 탐색 방법을 결합해 주행 정책을 결정하는지 검증한다.

---

## 주요 테스트

| Test ID | 검증 |
|---|---|
| TC-TERRAIN-001 | `ITerrainAnalyzer`가 Mock PointCloud를 TerrainAnalysisResult로 변환 |
| TC-TERRAIN-002 | slope, roughness, step height, obstacle density 산출 |
| TC-TERRAIN-003 | TerrainClass 분류 |
| TC-TERRAIN-004 | SearchMethod와 TerrainClass 호환성 검증 |
| TC-TERRAIN-005 | SearchDriveProfile 결정 |
| TC-TERRAIN-006 | Cliff/Drop 구간 STOP_AND_REPLAN |
| TC-TERRAIN-007 | Flat terrain + Parallel Sweep 주행 profile |
| TC-TERRAIN-008 | Rough rubble + Frontier Exploration 주행 profile |

---

# 9. Integration Test

## 목적

모듈 간 연결과 Adapter 연동을 검증한다.

---

## Client-1 ROS2/WebRTC Bridge

| Test ID | 검증 |
|---|---|
| TC-INT-001 | IMU/Gas/Pose → DataChannel 송신 |
| TC-INT-002 | Control DataChannel → ROS2 Control Topic 발행 |
| TC-INT-003 | Event Topic → data_event 송신 |

---

## Client-2 Detection Integration

| Test ID | 검증 |
|---|---|
| TC-INT-010 | Thermal/RGB 압축 패킷 WebRTC 직접 송신 |
| TC-INT-011 | WebRTC 송신 경로와 AI Decode 경로 분리 |
| TC-INT-012 | Detection Result ROS2 Topic 발행 |

---

## Client-3 SLAM/Navigation/Control

| Test ID | 검증 |
|---|---|
| TC-INT-020 | PointCloud 기반 Pose/Map 생성 |
| TC-INT-021 | Navigation Path 생성 |
| TC-INT-022 | Locomotion Mode 기반 Robot Control |

---

## Server Integration

| Test ID | 검증 |
|---|---|
| TC-INT-030 | Event 수신 후 DB 저장 |
| TC-INT-031 | Critical Event UI Alert 표시 |
| TC-INT-032 | SOP Agent 권고 생성 |

---

# 9. Failure Test

## 목적

단일 장애가 전체 시스템 장애로 확산되지 않는지 검증한다.

---

## Sensor Failure

| Test ID | 장애 | 기대 결과 |
|---|---|---|
| TC-FAIL-001 | Thermal Failure | RGB/Audio 보조 판단 |
| TC-FAIL-002 | RGB Failure | Thermal 유지 |
| TC-FAIL-003 | LiDAR Failure | Safe Mode |
| TC-FAIL-004 | Gas Sensor Failure | Gas Unknown Event |

---

## AI Failure

| Test ID | 장애 | 기대 결과 |
|---|---|---|
| TC-FAIL-010 | YOLO Timeout | 영상 송신 유지 |
| TC-FAIL-011 | CUDA Error | AI Pipeline 재시작 |
| TC-FAIL-012 | OOM | FPS 감소 또는 재시작 |

---

## Communication Failure

| Test ID | 장애 | 기대 결과 |
|---|---|---|
| TC-FAIL-020 | ICE Disconnect | DISCONNECTED 전이 |
| TC-FAIL-021 | Disconnect 지속 | Local Autonomous 진입 |
| TC-FAIL-022 | Reconnect | Local Data Sync |

---

## Navigation / Storage Failure

| Test ID | 장애 | 기대 결과 |
|---|---|---|
| TC-FAIL-030 | SLAM Drift | Recovery 또는 Safe Mode |
| TC-FAIL-031 | Path Planning Failure | Stop 또는 Replan |
| TC-STO-003 | Storage Failure | Local Save 유지 |

---

# 10. Network Priority Test

## 우선순위

```text
Emergency Stop
    >
Control
    >
Critical Event
    >
Thermal Video
    >
RGB Video
    >
Audio
    >
PointCloud
```

---

## 주요 테스트

| Test ID | 검증 |
|---|---|
| TC-NET-001 | Control 우선 전송 |
| TC-NET-002 | PointCloud 우선 Drop/Downsample |
| TC-NET-003 | Thermal이 RGB보다 우선 유지 |

---

# 11. SOP / AI Agent Test

## 원칙

```text
AI Recommendation
    !=
Direct Robot Control
```

---

## 주요 테스트

| Test ID | 검증 |
|---|---|
| TC-SOP-001 | SOP Agent 권고 생성 |
| TC-SOP-002 | 직접 제어 금지 |
| TC-SOP-003 | Operator 승인 후 Control 변환 |
| TC-SOP-004 | SOP Profile 기반 Mission 설정 추천 |
| TC-SOP-005 | SOP Agent의 Mission Start 직접 수행 금지 |

---

# 12. Mission Creation Test

## 원칙

```text
Mission Setup
    =
Operator Request
    +
SOP Recommendation
    +
Mission Commander Approval
```

SOP는 설정 추천만 수행하고, Mission Start와 ControlCommand 생성은 수행하지 않는다.

---

## 주요 테스트

| Test ID | 검증 |
|---|---|
| TC-MISSION-001 | Operator가 탐색 임무를 생성 |
| TC-MISSION-002 | 탐색 구역 지정 및 검증 |
| TC-MISSION-003 | 탐색 방법 선택 및 검증 |
| TC-MISSION-004 | SOP Profile 기반 설정 적용 |
| TC-MISSION-005 | Mission Commander 승인 전 활성화 차단 |
| TC-MISSION-006 | Server-2 UI의 Mission Repository 직접 접근 금지 |
| TC-MISSION-007 | Server-4 SOP의 Mission Start/ControlCommand 생성 금지 |
| TC-MISSION-008 | 동일 입력의 Mission Draft Snapshot 결정성 |

---

# 13. E2E Scenario Test

## 산악 실종자 수색

```text
Mission Start
    ↓
Terrain Navigation
    ↓
Thermal Detection
    ↓
Victim Event
    ↓
UI Alert / DB Save
```

기대 결과:

```text
VictimDetectedEvent 생성
Thermal Stream 유지
DB 저장
```

---

## 붕괴 현장 탐색

```text
부분 은폐 요구조자
    ↓
Thermal + RGB Fusion
    ↓
Critical Event
```

기대 결과:

```text
Thermal 기준 VictimCandidate 생성
```

---

## 지하 공동구 선탐색

```text
Gas Hazard
    ↓
Safe Mode
    ↓
SOP Recommendation
```

기대 결과:

```text
GasHazardEvent 우선 처리
```

---

## 통신 단절 시나리오

```text
WebRTC Disconnect
    ↓
LOCAL_AUTONOMOUS_MODE
    ↓
Local Navigation
    ↓
Local Save
```

기대 결과:

```text
Mission 중단 없음
```

---

# 13. Simulation Test

## 목적

Field Test 이전에 안전하게 전체 흐름을 검증한다.

---

## 환경

```text
Isaac Sim
Gazebo
Unity
Mujoco
```

---

## 시뮬레이션 시나리오

| 환경 | 검증 |
|---|---|
| Mountain | Slope / Rock / Mud |
| Tunnel | Darkness / Communication Loss / Gas Hazard |
| Debris | Obstacle / Collapse |
| Fire/Smoke | Low Visibility / Heat Source |

---

## 성능 목표

| 항목 | 목표 |
|---|---|
| Victim Detection Latency | < 200ms |
| Localization Update | > 10Hz |
| Thermal FPS | ≥ 15 |
| Reconnect | < 10s |

---

# 14. Field Test

## 목적

실제 환경에서 Navigation, Detection, Communication, Safety를 검증한다.

---

## 테스트 환경

```text
산악
터널
붕괴 구조물
화재/연기 환경
```

---

## 주요 KPI

| KPI | 목표 |
|---|---|
| Victim Detection Accuracy | ≥ 90% |
| Thermal Stream FPS | ≥ 15 FPS |
| Localization Update | ≥ 10Hz |
| Reconnect Time | < 10 sec |
| Mission Success Rate | ≥ 95% |
| Obstacle Traversal Success | ≥ 90% |

---

# 15. Acceptance Test

## 목적

운영 가능한 수준인지 최종 승인한다.

---

## Acceptance 기준

| 영역 | 기준 |
|---|---|
| Detection | Victim Detection Accuracy ≥ 90% |
| Communication | Disconnect 시 Local Autonomous 진입 |
| Streaming | Thermal Stream ≥ 15 FPS |
| SLAM | Localization Update ≥ 10Hz |
| Recovery | Reconnect < 10 sec |
| Safety | Emergency Stop 즉시 정지 |
| Storage | Critical Event Loss 없음 |
| Mission | Mission Success Rate ≥ 95% |
| Mission Creation | 탐색 구역, 탐색 방법, SOP Profile 기반 임무 생성 및 승인 가능 |
| Terrain Driven Navigation | 3D LiDAR 지형 분석 기반 탐색 주행 가능 |

---

## Pass / Fail

```text
PASS
    모든 Critical Acceptance 만족

CONDITIONAL PASS
    Minor Issue 존재, Mission 수행 가능

FAIL
    Critical Safety Failure
    Mission Failure
    Recovery 불가
```

---

# 16. 우선 구현 테스트 10개

| 순서 | Test ID | 이유 |
|---|---|---|
| 1 | TC-UNIT-012 | Emergency Stop 최우선 |
| 2 | TC-SOP-002 | AI Agent 직접 제어 금지 |
| 3 | TC-UNIT-001 | Thermal 우선 판단 |
| 4 | TC-INT-011 | AI/WebRTC 분리 |
| 5 | TC-INT-010 | Video/Audio ROS2 Topic 미사용 |
| 6 | TC-FAIL-021 | Local Autonomous 전환 |
| 7 | TC-FAIL-001 | Thermal Failure 격리 |
| 8 | TC-NET-001 | Control 우선 전송 |
| 9 | TC-STO-003 | Critical Event Local Save |
| 10 | TC-MISSION-001 | 탐색 임무 생성 기능 확보 |

---

# 17. 완료 기준

테스트 완료 기준:

```text
1. P0 테스트는 모두 통과해야 한다.
2. Python Lint, Formatting Check, Type Check를 통과해야 한다.
3. `TC-LAYER-*` 테스트를 통과해야 한다.
4. `TC-DEP-*` 의존성 방향 테스트를 통과해야 한다.
5. `TC-DETVAL-*` 테스트를 통과해야 한다.
6. `TC-FUNC-DEC-*`, `TC-FUNC-BND-*` 함수 단위 테스트를 통과해야 한다.
7. `TC-MISSION-*` 탐색 임무 생성 테스트를 통과해야 한다.
8. `TC-TERRAIN-*` 지형 분석 기반 주행 테스트를 통과해야 한다.
9. Windows 기본 테스트에서는 ROS Runtime, rclpy, ROS Node, 실제 Topic Publish/Subscribe를 실행하지 않아야 한다.
10. Business Logic은 실제 Middleware 없이 실행 가능해야 한다.
11. Failure Injection이 가능해야 한다.
12. AI 장애가 WebRTC 송신 장애로 전파되지 않아야 한다.
13. 통신 장애 시 Local Autonomous로 전환되어야 한다.
14. Emergency Stop은 모든 상태보다 우선해야 한다.
15. SOP Agent는 직접 제어 명령이나 Mission Start를 생성하지 않아야 한다.
16. Critical Event는 Local Storage에 우선 저장되어야 한다.
17. Linux/ROS 전환 후 별도 ROS Runtime Test로 확장한다.
18. Simulation 통과 후 Field Test로 진입한다.
19. Acceptance 기준 통과 후 운영 배포한다.
```

---

# 18. 최종 핵심

```text
Test Plan의 핵심은
실제 로봇 없이 먼저 검증하고,
Adapter 통합 후 Simulation,
Field Test,
Acceptance 순서로 확장하는 것이다.
```
