# 재난 구조용 바퀴형 사족로봇 시스템 마스터 계획서

## 1. 문서 목적

본 문서는 다음 기존 Markdown 문서를 기반으로 재난 구조용 바퀴형 사족로봇 시스템의 개발, 통합, 시험, 배포, 운영, 유지보수 계획을 하나의 실행 가능한 상위 계획으로 정리한다.

- `sdd.md`: Software Design Description
- `interface.md`: Interface Specification
- `implementation_roadmap.md`: Implementation Roadmap
- `integration_plan.md`: System Integration Plan
- `test_plan.md`: Compact Test Plan
- `operation_plan.md`: Operation & Maintenance Plan
- `requirements_spec.md`: 요구사항 명세서
- `wbs_schedule.md`: WBS 및 일정 계획
- `detailed_interface_schema.md`: 상세 Interface 및 데이터 스키마
- `interface_baseline_freeze.md`: Interface Baseline Freeze 정책
- `mission_creation_plan.md`: 탐색 임무 생성, 구역 지정, 방법 선택, SOP 설정 계획
- `dependency_direction_plan.md`: `Types -> Config -> Service -> UI` 의존성 방향 고정 계획
- `pre_implementation_checklist.md`: 코드 작성 전 구조 점검 및 구현 시작 승인 체크리스트
- `implementation_start_check_result.md`: 구현 시작 전 점검 결과 및 첫 구현 대상
- `detailed_test_case_spec.md`: 상세 테스트 케이스 명세서
- `layer_tdd_harness_matrix.md`: 계층별 TDD 및 Test Harness 매트릭스
- `deterministic_validation_plan.md`: Deterministic Validation 계획
- `function_unit_test_plan.md`: 결정/경계 로직 함수 단위 테스트 계획
- `risk_management_plan.md`: 리스크 관리 계획서
- `quality_lint_plan.md`: Python 품질 및 Lint 계획서
- `ros_layering_plan.md`: ROS 기반 경량 계층화 계획
- `environment_profile_plan.md`: Windows/Linux 환경 프로파일 및 전환 계획
- `raci_matrix.md`: 역할 책임 매트릭스
- `deployment_environment_spec.md`: 배포 환경 명세서
- `security_plan.md`: 보안 계획서
- `safety_sop.md`: 안전 및 현장 SOP
- `traceability_matrix.md`: 요구사항 추적성 매트릭스

본 문서의 목적은 세부 설계 문서의 내용을 실행 관점에서 연결하고, 단계별 산출물과 완료 기준을 명확히 하는 것이다.

---

## 2. 프로젝트 개요

### 2.1 시스템 목표

재난 구조용 바퀴형 사족로봇 시스템은 산악, 붕괴 구조물, 지하 공동구, 화재 및 연기 환경에서 요구조자 탐색과 구조 지원을 수행하는 AI 기반 로봇 시스템이다.

핵심 기능은 다음과 같다.

- 험지 이동 및 장애물 극복
- 열화상, RGB, 오디오 기반 요구조자 탐지
- LiDAR/IMU 기반 SLAM 및 자율주행
- 가스 위험 감지 및 안전 모드 전환
- WebRTC 기반 원격 관제 및 제어
- 관제자 기반 탐색 임무 생성, 탐색 구역 지정, 탐색 방법 선택
- 통신 단절 시 Local Autonomous Mode 유지
- 이벤트, 영상, PointCloud, 미션 로그 저장
- AI/SOP 기반 상황 요약 및 권고 제공

### 2.2 적용 환경

| 환경 | 주요 검증 대상 |
|---|---|
| 산악 | 경사, 암석, 진흙, 수목 뿌리, 불규칙 지형 |
| 터널 | 저조도, GPS 손실, 통신 손실, 가스 위험 |
| 붕괴 구조물 | 잔해, 협소 통로, 부분 은폐 요구조자 |
| 화재/연기 | 열원, 연기, 저시야, 오탐 제어 |

### 2.3 개발 및 실행 환경 프로파일

현재 기본 개발 환경은 Windows 기반 `dev-windows-local`이다.

향후 ROS2 Runtime과 실제 로봇/센서 통합은 Linux 기반 `target-linux-ros` 프로파일로 전환한다.

```text
dev-windows-local
    = Domain/Application/Interface/Mock Test

target-linux-ros
    = ROS2 Runtime/Node/Topic/Hardware Integration
```

Windows 기본 테스트는 ROS단까지 진행하지 않는다.

---

## 3. 핵심 원칙

### 3.1 Safety First

모든 설계와 구현은 다음 우선순위를 따른다.

```text
Emergency Stop
    >
Safe Mode
    >
Operator Command
    >
Autonomous Navigation
    >
Mission Performance
```

### 3.2 Business Logic 독립성

비즈니스 로직은 ROS2, WebRTC, DB, YOLO, SLAM, Robot SDK, UI에 직접 의존하지 않는다.

```text
Business Logic
    !=
Middleware / Hardware / Transport
```

### 3.3 Interface First

외부 시스템 통합 전 핵심 Interface를 먼저 정의하고 검증한다.

```text
Domain Logic
    ↓
Interface
    ↓
Adapter
    ↓
Middleware / Hardware
```

### 3.4 ROS 경량 계층화

ROS2는 내부 통신 Runtime이며, Business Logic의 중심이 아니다.

```text
Domain / Business Logic
    ↓
Application Service / State Machine
    ↓
Interface
    ↓
ROS Adapter
    ↓
ROS Topic / Node
```

Domain과 Application Service는 ROS Message, `rclpy`, ROS Runtime에 직접 의존하지 않는다.

### 3.5 의존성 방향 고정

구현 코드는 반드시 다음 계층 순서를 지킨다.

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
```

허용:

```text
UI → Service/Config/Types
Service → Config/Types
Config → Types
```

금지:

```text
Types → Config/Service/UI
Config → Service/UI
Service → UI
UI → DB Driver / ROS Runtime / Robot SDK 직접 접근
```

이 규칙은 `dependency_direction_plan.md` 기준으로 고정하며, `TC-DEP-*` 테스트로 강제한다.

### 3.6 Mock First

실제 장비 연결 전 Mock 기반으로 상태 전이, 이벤트 흐름, 장애 대응을 검증한다.

### 3.7 Deterministic Validation

Windows 기본 테스트는 동일 입력에서 동일 Event, 동일 State Transition, 동일 Output을 생성해야 한다.

```text
Same Input
    =
Same Output
```

실제 시간, 실제 난수, 실제 네트워크, ROS Runtime, 외부 DB/API에 의존하지 않고 `FakeClock`, fixed seed, fixed fixture, Mock Adapter를 사용한다.

### 3.8 Event-Driven Architecture

센서 입력, 판단, 상태 전이, 제어 동작은 Event 중심으로 연결한다.

```text
Input
    ↓
Business Event
    ↓
State Transition
    ↓
Action
```

### 3.9 Failure Isolation

단일 장애가 전체 시스템 장애로 확산되지 않도록 한다.

| 장애 | 영향 범위 | 유지 기능 |
|---|---|---|
| YOLO Failure | Detection 제한 | Video 송신 유지 |
| WebRTC Failure | 원격 관제 제한 | Local Autonomous 유지 |
| SLAM Failure | Navigation 제한 | Detection 유지 |
| DB Failure | 원격 저장 제한 | Local Save 유지 |
| LiDAR Failure | Mapping 제한 | Safe Mode 전환 |
| Motor Failure | Motion 제한 | Emergency/Safety 유지 |

### 3.10 AI Recommendation Only

AI/SOP Agent는 권고만 생성하며, 로봇 직접 제어 명령을 생성하지 않는다.

```text
AI Recommendation
    !=
Direct Motion Control
```

---

## 4. 전체 시스템 구조

### 4.1 Layer 구조

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
```

Runtime Adapter 구조는 Service 바깥 경계에 두되, Service는 Protocol/Interface를 통해서만 Adapter를 사용한다.

```text
Service
    ↓ Protocol
Adapter Layer
    ↓
ROS2 / WebRTC / Storage / Hardware
```

### 4.2 Robot Side

```text
Thermal Camera / RGB Camera / LiDAR / IMU / Gas Sensor / Microphone
    ↓
Sensor Adapter
    ↓
Perception / Detector Adapter
    ↓
Decision Engine
    ↓
SLAM / Navigation / Robot Controller
    ↓
WebRTC / Storage / ROS2 Bridge
```

### 4.3 Control Center Side

```text
WebRTC Receiver
    ↓
Mission Core
    ├── Operator UI / Mission Setup
    ├── Storage / DB
    └── SOP Agent
```

---

## 5. 주요 Interface 계획

### 5.1 핵심 Interface

| Interface | 역할 |
|---|---|
| `IDetector` | Thermal/RGB/Audio Detection 추상화 |
| `ISlamEngine` | SLAM 엔진 교체 가능성 확보 |
| `ITerrainAnalyzer` | 3D LiDAR 기반 지형 분석 추상화 |
| `ISearchDrivePolicy` | 지형과 탐색 방법 기반 주행 정책 추상화 |
| `INavigationEngine` | 경로 계획 및 지형 대응 추상화 |
| `IWebRTCTrackSender` | 영상/오디오 패킷 송신 추상화 |
| `IDataChannelSender` | Event/Status/Control 송신 추상화 |
| `IEventRepository` | Event 저장소 교체 가능성 확보 |
| `IRobotController` | Move/Stop/Locomotion 제어 추상화 |
| `ISopAgent` | SOP 권고 생성 추상화 |
| `IMissionSetupSender` | UI의 탐색 임무 생성 요청 추상화 |
| `IMissionCreationService` | Mission Draft 생성, 구역/방법 검증, 승인 요청 추상화 |
| `IMissionRepository` | Mission Draft/Plan 저장소 추상화 |
| `ISopMissionConfigurator` | SOP Profile 기반 임무 설정 추천 추상화 |

핵심 Interface는 `interface_baseline_freeze.md` 기준으로 고정하며, 변경 시 Change Request와 영향 분석이 필요하다.

### 5.1.1 구현 전 점검 기준

실제 코드를 작성하기 전 `pre_implementation_checklist.md`를 기준으로 다음을 확인한다.

```text
Requirements
    ↓
Types
    ↓
Config
    ↓
Service
    ↓
UI
    ↓
Test Gate
```

Types 정의 없이 Service/UI부터 구현하지 않는다.

### 5.2 Client / Server 분리 기준

| 영역 | 모듈 | 분리 기준 |
|---|---|---|
| Client | Client-1 ROS2/WebRTC Bridge | Transport와 Bridge만 담당하며 Detector/SLAM/DB를 직접 호출하지 않는다. |
| Client | Client-2 Thermal/RGB + AI Detection | Detection 결과를 Event/ROS2 Contract로 발행하며 WebRTC Track을 직접 송신하지 않는다. |
| Client | Client-3 SLAM + Navigation + Robot Control | 3D LiDAR 지형 분석, 탐색 주행 정책, Navigation/Control만 담당하며 UI/SOP를 직접 호출하지 않는다. |
| Server | Server-1 Mission Core | Mission 판단과 탐색 임무 Draft/Plan 검증 중심이며 UI/Storage/SOP는 Interface로만 호출한다. |
| Server | Server-2 UI | Operator 입출력과 탐색 임무 생성 요청만 담당하며 DB에 직접 저장하지 않는다. |
| Server | Server-3 Storage / DB | 저장과 Sync만 담당하며 Mission 판단을 수행하지 않는다. |
| Server | Server-4 AI Agent / SOP | Recommendation과 Mission 설정 추천만 생성하며 ControlCommand와 Mission Start를 생성하지 않는다. |

이 분리 기준은 `interface.md`의 Client/Server Interface 적용 매트릭스와 `detailed_test_case_spec.md`의 `TC-MOD-*` 테스트로 검증한다.

Client 3개와 Server 4개의 Inbound/Outbound Contract는 Baseline으로 고정한다.

### 5.3 탐색 임무 생성 정책

탐색 임무 생성은 `mission_creation_plan.md`를 기준으로 수행한다.

```text
Operator UI
    ↓ SearchMissionRequest
Mission Core
    ↓ validate SearchArea / SearchMethod
SOP Mission Configurator
    ↓ MissionSetupRecommendation
Mission Repository
    ↓ Mission Draft / Search Mission Plan
Mission Commander Approval
```

원칙:

- Server-2 UI는 `SearchMissionRequest`만 생성하고 Mission DB에 직접 저장하지 않는다.
- Server-1 Mission Core는 Draft 생성, 검증, 승인 요청, Plan 확정의 단일 책임 지점이다.
- Server-3 Storage는 Mission Draft/Plan 저장과 조회만 담당한다.
- Server-4 SOP는 설정 추천만 수행하고 Mission Start 또는 ControlCommand를 생성하지 않는다.
- Windows 기본 테스트에서는 실제 ROS Runtime 없이 `TC-MISSION-*`로 검증한다.

### 5.4 3D LiDAR 지형 분석 및 탐색 주행 정책

Client-3는 3D LiDAR PointCloud를 ROS Adapter 내부에서 Domain DTO로 변환한 뒤 지형 분석을 수행한다.

```text
3D LiDAR PointCloud
    ↓
Elevation Grid Map
    ↓
TerrainAnalysisResult
    ↓
SearchMethod Compatibility
    ↓
SearchDriveProfile
    ↓
NavigationPath / LocomotionDecision
```

핵심 판단 기준:

- slope
- roughness
- step height
- obstacle density
- traversability score
- TerrainClass

탐색 주행은 SearchMethod만으로 결정하지 않고 TerrainAnalysisResult와 결합해 결정한다.

### 5.5 ROS2 정책

ROS2는 내부 모듈 간 상태, 판단, 이벤트 전달에 사용한다.

ROS2 Topic과 Message는 ROS Adapter 내부에서만 다루며, Domain/Application 계층은 Python DTO와 Interface만 사용한다.

단, 현재 Windows 기본 테스트에서는 실제 ROS2 Runtime, `rclpy`, ROS Node, ROS Topic Publish/Subscribe를 실행하지 않는다.

주요 Topic:

```text
/imu/data
/gas/data
/lidar/points_raw
/robot/pose
/slam/map
/navigation/path
/terrain/analysis
/locomotion/mode
/perception/victim_decision
/system/events
/system/status
/control/command
/control/emergency_stop
```

Critical Topic은 Reliable QoS를 적용한다.

### 5.6 WebRTC 정책

영상과 오디오는 ROS2 Topic을 통과하지 않고 WebRTC Direct Track으로 전송한다.

```text
Thermal/RGB/Audio
    !=
ROS2 Topic
```

Track 및 DataChannel:

| 구분 | 대상 |
|---|---|
| `video1` | Thermal |
| `video2` | RGB |
| `audio1` | Robot/Operator Audio |
| `audio2` | Environment Audio |
| `data_sensor` | IMU/Gas/Status |
| `data_pointcloud` | PointCloud |
| `data_event` | Event |
| `data_status` | System Status |
| `data_control` | Remote Control |

네트워크 우선순위:

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

## 6. 구현 로드맵

### 6.1 단계 요약

| Phase | 목표 | 주요 산출물 | 완료 기준 |
|---|---|---|---|
| 1. Foundation | 핵심 구조 정의 | Data Structure, Event Schema, Interface | Python Syntax Check, Interface Contract 검증 |
| 2. Mock/TDD | HW 없이 흐름 검증 | Mock Adapter, Test Harness, Lint Gate, Layer Test | Unit Test, Failure Injection, Python Lint, Layer Test 통과 |
| 3. Business Logic | Middleware 독립 로직 구현 | Event System, State Machine, Fusion Logic | 상태 전이, 복구, Safe Mode 검증 |
| 4. Detector Integration | AI Detection 연결 | Thermal/RGB/Audio Detector Adapter | 정확도, 지연, AI Failure 격리 검증 |
| 5. SLAM/Navigation | 자율주행 연결 | SLAM, Terrain Analysis, Path Planning | Localization, Drift Recovery 검증 |
| 6. ROS2 Integration | 내부 모듈 연결 | Topic, QoS, Namespace | Topic Flow, Latency 검증 |
| 7. WebRTC Integration | 원격 관제 연결 | Track, DataChannel, Reconnect | ICE Recovery, Thermal Priority 검증 |
| 8. Storage Integration | Event/Media 저장 | Local Save, Remote Sync | DB Failure, Storage Full 대응 검증 |
| 9. Deployment | 실행 환경 구성 | Container, Monitoring, Rollback | Docker/GPU/Network Health Check |
| 10. Simulation | 안전한 전체 흐름 검증 | Simulation Scenario Report | Mission Flow, Failure 대응 통과 |
| 11. Field Test | 실제 환경 검증 | Field Test Report | KPI 기준 만족 |
| 12. Acceptance | 운영 가능성 승인 | Acceptance Report | Critical Failure 없음 |

### 6.2 우선 구현 대상

1. Emergency Stop
2. AI Agent 직접 제어 금지
3. Thermal 우선 요구조자 판단
4. WebRTC 송신 경로와 AI Decode 경로 분리
5. Video/Audio ROS2 Topic 미사용
6. Local Autonomous Mode 전환
7. Thermal Failure 격리
8. Control 우선 전송
9. Critical Event Local Save
10. 복구 후 Sync

### 6.3 Python 품질 Gate

Python 구현물은 기능 테스트 전 다음 품질 Gate를 통과해야 한다.

```text
ruff check
ruff format --check
mypy
pytest tests/unit tests/contract tests/layer tests/dependency tests/module_boundary tests/mission_creation tests/terrain
```

보안 및 배포 단계에서는 다음 검사를 추가한다.

```text
bandit -r src
pip-audit
```

---

## 7. 통합 계획

### 7.1 Adapter 통합 구조

| Adapter | 역할 | 주요 연결 |
|---|---|---|
| ROS2Adapter | 내부 Topic/Event 통신 | Module ↔ Module |
| WebRTCAdapter | 원격 Streaming/Control | Robot ↔ Control Center |
| DetectorAdapter | Thermal/RGB/Audio Detection | Camera ↔ AI |
| SLAMAdapter | Localization/Mapping | LiDAR/IMU ↔ Navigation |
| TerrainAnalyzerAdapter | 3D LiDAR 지형 분석 | PointCloud ↔ TerrainAnalysisResult |
| SearchDrivePolicyAdapter | 지형+탐색 방법 기반 주행 정책 | TerrainAnalysisResult ↔ SearchDriveProfile |
| StorageAdapter | DB/Object/Local Save | Event/Media 저장 |
| RobotControllerAdapter | Motion/Locomotion | Navigation ↔ Motor |
| SensorAdapter | Device Driver 연결 | Sensor ↔ Adapter |
| SOPAgentAdapter | AI 권고 | Event ↔ Operator |

### 7.2 센서 통합

| 센서 | 처리 경로 | 핵심 검증 |
|---|---|---|
| Thermal Camera | GStreamer Parsing → WebRTC Track + Detector Decode | 영상 유지, 요구조자 탐지 |
| RGB Camera | Encoded Packet → WebRTC + AI Decode | 보조 탐지, 영상 분리 |
| LiDAR | PointCloud Adapter → SLAM Adapter + TerrainAnalyzerAdapter | Pose/Map 생성, 지형 분석 |
| IMU | ROS2 Topic → SLAM Adapter | 자세 보정 |
| Gas Sensor | ROS2 Topic → Business Logic | Hazard Decision |

### 7.3 Local Autonomous 통합

진입 조건:

```text
WebRTC disconnected
AND
5G disconnected
```

유지 기능:

- Local SLAM
- Obstacle Avoidance
- Victim Detection
- Critical Event Save
- Terrain Following

복구 흐름:

```text
Reconnect
    ↓
Local Data Sync
    ↓
Mission Resume
```

---

## 8. 시험 및 검증 계획

### 8.1 시험 단계

```text
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

품질 검사는 기능 테스트보다 먼저 수행한다.

```text
Lint / Static Analysis
    ↓
Unit Test
```

### 8.2 테스트 우선순위

| Priority | 영역 | 목적 |
|---|---|---|
| P0 | Safety | Emergency Stop / Safe Mode |
| P0 | Victim Decision | Thermal 우선 요구조자 판단 |
| P0 | Communication Failover | Local Autonomous 진입 |
| P0 | AI/WebRTC Isolation | AI 장애 시 영상 유지 |
| P0 | Control Authority | 승인 없는 제어 차단 |
| P1 | Storage/Sync | Local Save 및 복구 후 Sync |
| P1 | SLAM/Navigation | Localization / Path Planning |
| P1 | Network Priority | Control/Event/Thermal 우선 |
| P2 | UI/SOP | Alert 및 권고 검증 |
| P2 | Multi Robot | Namespace / Map Sharing |

### 8.3 필수 Failure Injection

| 장애 주입 | 기대 결과 |
|---|---|
| Thermal Failure | RGB/Audio 보조 판단 |
| YOLO Timeout | 영상 송신 유지 |
| CUDA Error / OOM | AI Pipeline 재시작 또는 FPS 감소 |
| ICE Disconnect | DISCONNECTED 전이 후 Local Autonomous |
| SLAM Drift | Recovery 또는 Safe Mode |
| DB Failure | Local Save 유지 |
| Storage Full | Low Priority 삭제, Critical Event 유지 |
| Robot Control Timeout | Stop 또는 Safe Mode |

### 8.4 Acceptance 기준

| 영역 | 기준 |
|---|---|
| Detection | Victim Detection Accuracy ≥ 90% |
| Streaming | Thermal Stream ≥ 15 FPS |
| SLAM | Localization Update ≥ 10Hz |
| Communication | Reconnect < 10 sec |
| Failover | Disconnect 시 Local Autonomous 진입 |
| Safety | Emergency Stop 즉시 정지 |
| Storage | Critical Event Loss = 0 |
| Mission | Mission Success Rate ≥ 95% |
| Mobility | Obstacle Traversal Success ≥ 90% |
| Availability | Mission Availability ≥ 99% |
| Code Quality | Ruff, Format, mypy, Windows 기본 pytest 통과 |
| Deterministic Validation | 동일 입력에서 동일 Event/State/Output 보장 |

---

## 9. 운영 계획

### 9.1 운영 조직

| 역할 | 책임 |
|---|---|
| Mission Commander | 전체 임무 통제 |
| Robot Operator | 로봇 운용 |
| Safety Officer | 안전 관리 |
| Communication Operator | 통신 관리 |
| AI/SOP Operator | AI 권고 모니터링 |
| Technical Support | 장애 대응 |
| Maintenance Manager | 유지보수 총괄 |

### 9.2 Mission 시작 전 점검

필수 점검 항목:

- Battery
- Sensor 상태
- Storage 상태
- Network 상태
- SLAM 상태
- WebRTC 상태
- Emergency Stop
- Thermal/RGB Video 출력
- Pose/Map/Event Stream 출력

점검 흐름:

```text
Self Check
    ↓
Operator Confirm
    ↓
Mission Approval
```

### 9.3 통신 상태별 운영

| 상태 | 동작 |
|---|---|
| CONNECTED | Real-Time Monitoring, Remote Control, Event Streaming |
| DEGRADED | Thermal Priority 유지, RGB Bitrate 감소, PointCloud Drop |
| DISCONNECTED | Reconnect Attempt, Local Autonomous Mode 진입 |
| RECONNECTING | Local Save 유지, 복구 후 Sync |

### 9.4 Emergency 운영

Emergency Stop Trigger:

- Operator Stop
- Collision Risk
- Gas Hazard
- Hardware Failure
- Control Authority Violation

Emergency 흐름:

```text
Emergency Stop
    ↓
All Motion Stop
    ↓
Safety Confirm
    ↓
Recovery Decision
```

---

## 10. 배포 및 운영 환경 계획

### 10.1 Robot Side 배포 대상

```text
Sensor
ROS2
Detector
SLAM
Navigation
Robot Controller
WebRTC
Storage
```

### 10.2 Control Center 배포 대상

```text
WebRTC Receiver
Mission Management
Operator UI
SOP Agent
Storage
```

### 10.3 Container 구조

```text
detector_container
slam_container
navigation_container
webrtc_container
storage_container
```

Container 단위로 독립 재시작, 독립 업데이트, Health Check, Rollback을 지원한다.

### 10.4 OTA / Update 절차

```text
Offline Validation
    ↓
Simulation Validation
    ↓
Controlled Deployment
    ↓
Field Deployment
    ↓
Monitoring
```

Rollback 조건:

- Critical Failure
- Performance Degradation
- Safety Regression
- Reconnect/Local Save 실패

---

## 11. 유지보수 및 모니터링 계획

### 11.1 Hardware Maintenance

대상:

- Thermal Camera
- RGB Camera
- LiDAR
- IMU
- Gas Sensor
- Motor
- Battery

점검 항목:

- Calibration
- Temperature
- Noise
- Torque
- Vibration
- Packet Loss

점검 주기:

```text
Pre-Mission
Weekly
Monthly
```

### 11.2 Software Maintenance

대상:

- ROS2 Node
- YOLO / Detector
- Fusion Logic
- TensorRT
- SLAM
- Navigation
- WebRTC
- Storage

점검 항목:

- Latency
- Memory Leak
- Inference Time
- Localization Drift
- Reconnect
- GPU Usage

### 11.3 Monitoring 항목

```text
CPU
GPU
Memory
Temperature
Battery
Network
FPS
Latency
Storage
```

Alert Level:

| Level | 의미 |
|---|---|
| INFO | 정상 범위 경고 |
| WARNING | 성능 저하 가능성 |
| CRITICAL | Mission 영향 가능 |

---

## 12. 리스크 및 대응 계획

| 리스크 | 영향 | 대응 |
|---|---|---|
| AI 탐지 지연 또는 OOM | 요구조자 탐지 지연 | FPS 감소, AI Pipeline 재시작, 영상 송신 유지 |
| 통신 단절 | 원격 관제 불가 | Local Autonomous, Local Save, Reconnect Retry |
| SLAM Drift | 위치 오차 증가 | Drift Detection, Re-localization, Safe Mode |
| Storage Failure | 데이터 손실 위험 | Local Save, Sync Queue, Critical Event 우선 |
| Sensor Failure | 탐지/주행 제한 | Fallback Sensor, Unknown Event, Safe Mode |
| Motor Failure | 이동 제한 | All Motion Stop, Safety Confirm |
| AI 직접 제어 위험 | 안전 사고 가능 | SOP Agent 권고 전용, Operator 승인 필수 |
| Field 환경 편차 | 성능 저하 | Simulation 다양화, 단계적 Field Test |

---

## 13. 산출물 계획

| 단계 | 산출물 |
|---|---|
| 요구사항 | Requirements Specification, Traceability Matrix |
| 설계 | SDD, Interface Specification, Interface Baseline Freeze, Event Schema, Detailed Interface Schema, ROS Layering Plan |
| 환경 | Environment Profile Plan, Deployment Environment Spec |
| 일정/역할 | WBS Schedule, RACI Matrix |
| 구현 준비 | Layer TDD/Harness Matrix, Deterministic Validation Plan, Function Unit Test Plan, Test Harness, Mock Adapter, Interface Contract Test, Quality Lint Plan |
| 핵심 구현 | Business Logic, State Machine, Fusion Logic |
| 통합 | ROS2 Adapter, WebRTC Adapter, Detector Adapter, SLAM Adapter |
| 검증 | Detailed Test Case Spec, Unit/Integration/Failure/Simulation/Field Test Report |
| 리스크 | Risk Management Plan, Known Risk Register |
| 운영 | Operation Manual, Maintenance Checklist, Safety SOP, Recovery SOP |
| 보안 | Security Plan, Access Control Matrix, Audit Log Policy |
| 배포 | Deployment Environment Spec, Container Definition, Deployment Guide, Rollback Guide |
| 승인 | Acceptance Report, KPI Result, Known Issue List |

---

## 14. 최종 완료 기준

본 프로젝트는 다음 조건을 만족할 때 완료로 판단한다.

1. Business Logic이 Middleware/HW 없이 독립 실행 및 테스트 가능하다.
2. Domain/Application 계층은 ROS Message와 `rclpy`에 직접 의존하지 않는다.
3. ROS2, WebRTC, SLAM, Detector, Storage, Robot Controller가 Adapter 기반으로 교체 가능하다.
4. Thermal/RGB/Audio 영상은 ROS2 Topic을 통과하지 않고 WebRTC Direct Track으로 송신된다.
5. WebRTC 송신 경로와 AI Decode/Inference 경로가 분리된다.
6. AI Failure 시 영상 송신이 유지된다.
7. 통신 단절 시 Local Autonomous Mode로 전환된다.
8. Emergency Stop은 모든 상태보다 우선 동작한다.
9. SOP Agent는 직접 제어 명령을 생성하지 않는다.
10. Critical Event는 Local Storage에 우선 저장되며 복구 후 Sync된다.
11. Windows 기본 테스트는 ROS단까지 진행하지 않고 Mock/Contract/Layer/Module Boundary 범위에서 통과한다.
12. Linux/ROS 전환은 `target-linux-ros` 프로파일에서만 수행한다.
13. Deterministic Validation은 실제 시간, 난수, 네트워크, ROS Runtime에 의존하지 않고 통과한다.
14. 결정 로직과 경계 로직은 함수 단위 테스트를 통과한다.
15. Client/Server Interface Baseline 변경은 승인 절차 없이 수행하지 않는다.
16. Python Lint, Formatting Check, Type Check, Unit Test, Layer Test를 통과한다.
17. P0 테스트와 Acceptance 기준을 모두 통과한다.
18. Simulation 통과 후 Field Test를 완료한다.
19. 요구사항, 설계, 구현, 테스트 간 추적성이 유지된다.
20. 실제 재난 환경에서 Mission Continuity를 유지할 수 있다.

---

## 15. 최종 실행 흐름

```text
Design Baseline
    ↓
Interface First
    ↓
Mock / TDD
    ↓
Business Logic
    ↓
Adapter Integration
    ↓
ROS2 / WebRTC / Storage Integration
    ↓
Simulation Test
    ↓
Field Test
    ↓
Acceptance
    ↓
Deployment
    ↓
Operation / Maintenance
```

---

## 16. 결론

본 마스터 계획서는 재난 구조용 바퀴형 사족로봇 시스템을 안전하게 구현하고 실제 현장 운영까지 연결하기 위한 상위 실행 문서이다.

핵심은 다음 네 가지다.

1. `Business Logic`은 독립적으로 유지한다.
2. 모든 외부 시스템은 `Interface + Adapter`로 연결한다.
3. 통신, AI, 저장, SLAM 장애는 격리하고 Local Autonomous를 유지한다.
4. Simulation, Field Test, Acceptance를 순서대로 통과한 뒤 운영 배포한다.
