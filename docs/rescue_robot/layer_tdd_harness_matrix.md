# 계층별 TDD 및 Test Harness 매트릭스

## 1. 목적

본 문서는 ROS 경량 계층화 구조의 각 계층에 TDD와 Test Harness가 어떻게 적용되는지 정의한다.

대상 계층:

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
    ↓
Adapter
    ↓
Runtime / Middleware
```

기존 문서의 `Domain / Business Logic`, `Application Service / State Machine`, `Interface` 용어는 구현 계층을 새로 추가하는 의미가 아니다.

구현 시에는 다음 매핑을 적용한다.

| 기존 표현 | 구현 기준 매핑 |
|---|---|
| Domain / Business Logic | Types + Service의 순수 결정 함수 |
| Application Service / State Machine | Service |
| Interface | Types의 Protocol/DTO + Adapter Contract |
| Adapter | Service 바깥 Runtime Adapter |

따라서 코드 의존성은 항상 `Types -> Config -> Service -> UI`를 따른다.

---

## 2. 계층별 TDD 적용 매트릭스

| 계층 | TDD 대상 | 선행 테스트 | Mock/Fake | 주요 테스트 ID | 완료 기준 |
|---|---|---|---|---|---|
| Types | DTO, Enum, Value Object, Validation Result | Type Contract Test | Fixed DTO Fixture | `TC-DEP-001`, `TC-FUNC-BND-*` | Config/Service/UI import 없음 |
| Config | Runtime Profile, SOP Profile, Threshold, Policy Config | Config Unit Test | Fixed Config Fixture | `TC-DEP-002`, `TC-DETVAL-*` | Service/UI import 없음 |
| Service | Mission Creation, Terrain Driven Navigation, State Machine, Failover, Safety Rule | Unit + State Transition Test | Fake Event Queue, Fake Clock, InMemoryMissionRepository, FakeElevationGrid | `TC-DEP-003`, `TC-LAYER-*`, `TC-MISSION-*`, `TC-TERRAIN-*` | UI import 없이 Service 테스트 통과 |
| UI | Mission Setup View, Status ViewModel, Operator Input | ViewModel Contract Test | Mock Service, FakeOperatorCommand | `TC-DEP-004`, `TC-MOD-005`, `TC-MOD-008` | DB Driver/ROS Runtime/Robot SDK 직접 import 없음 |
| Domain / Business Logic | 요구조자 판단, Gas Hazard, Fusion Rule, Locomotion Rule, SearchArea/SearchMethod Rule, Terrain-Drive Rule | Function Unit Test | Fake PerceptionFrame, Fake Sensor Value, Fixed SearchArea, Fixed TerrainAnalysisResult | `TC-FUNC-DEC-*`, `TC-FUNC-BND-*`, `TC-UNIT-*`, `TC-DET-*`, `TC-SAFE-*`, `TC-TERRAIN-*` | ROS Runtime 없이 순수 Python 테스트 통과 |
| Application Service / State Machine | Mission State, Mission Creation, Terrain Driven Navigation, Failover, Recovery, Emergency Stop 우선순위 | Unit + State Transition Test | Fake Event Queue, Fake Clock, Fake State Recorder, InMemoryMissionRepository, FakeElevationGrid | `TC-LAYER-002`, `TC-DETVAL-*`, `TC-MISSION-*`, `TC-TERRAIN-*`, `TC-SAFE-*`, `TC-COMM-*` | 상태 전이와 우선순위가 기대 결과와 일치 |
| Interface | Protocol 계약, DTO 입출력, Adapter 교체 가능성 | Contract Test | MockDetector, MockSLAM, MockTerrainAnalyzer, MockSearchDrivePolicy, MockStorage, MockWebRTC, MockMissionRepository | `TC-IF-*` | Mock 교체 시 Business Logic 변경 없음 |
| ROS Adapter Contract | Fake ROS Envelope ↔ Domain DTO 변환, Topic Gateway 계약 | Contract Test | FakeRosEnvelope, Mock IRosTopicGateway | `TC-LAYER-003` | Windows 기본 테스트에서 ROS Runtime 실행 없음 |
| WebRTC Adapter | Track 송신, DataChannel 송수신, Reconnect | Adapter + Failure Test | MockWebRTC, MockDataChannel, Fake Packet | `TC-IF-002`, `TC-COMM-*`, `TC-NET-*` | AI 장애와 WebRTC 장애가 분리됨 |
| Storage Adapter | Local Save, Sync Queue, DB Failure | Adapter + Failure Test | MockDB, MockObjectStorage, MockLocalStorage | `TC-IF-003`, `TC-STO-*` | Critical Event Loss = 0 |
| Robot Controller Adapter | Move/Stop, Emergency Stop, Locomotion Mode | Contract + Safety Test | MockRobotController, Fake MotionCommand | `TC-SAFE-001`, `TC-IF-*` | Emergency Stop이 모든 제어보다 우선 |
| Client Module Boundary | Client-1/2/3 직접 의존 차단, Client-3 지형 주행 책임 검증 | Module Boundary Test | Mock ROS Topic, Mock DataChannel, Mock Terrain Adapter, Mock Adapter | `TC-MOD-001`~`TC-MOD-003`, `TC-MOD-011` | Client 간 직접 호출 없음 |
| Server Module Boundary | Server-1/2/3/4 책임 분리, Mission Creation 책임 분리 | Module Boundary Test | Mock UI, Mock Storage, Mock SOP Agent, MockMissionRepository | `TC-MOD-004`~`TC-MOD-010` | UI 직접 DB 저장, SOP 직접 제어/시작 없음 |
| Runtime / Middleware | ROS2, WebRTC, Container, Monitoring | Integration + Simulation Test | Simulation Environment, Fault Injector | `TC-INT-*`, `TC-FAIL-*`, `TC-ACC-*` | 실제 Runtime 통합 기준 만족 |

---

## 3. Test Harness 구성 매트릭스

| Harness 구성 요소 | 적용 계층 | 역할 |
|---|---|---|
| Scenario Runner | Application, Adapter, E2E | 테스트 시나리오 실행 순서 제어 |
| Fake Input Generator | Domain, Application | Thermal/RGB/Audio/Gas/LiDAR 입력 생성 |
| Mock Interface Layer | Interface, Adapter | Protocol 기반 외부 의존성 대체 |
| Failure Injector | Application, Adapter, Runtime | AI Timeout, ROS Topic Timeout, WebRTC Disconnect, DB Failure 주입 |
| Event Recorder | Domain, Application, Server-1 | Event 생성 순서와 우선순위 기록 |
| State Recorder | Application / State Machine | Mission State 전이 기록 |
| Mission Setup Fixture | Domain, Application, Interface | SearchArea, SearchMethod, SOP Profile 고정 입력 제공 |
| Message Mapper Test Fixture | ROS Adapter Contract | Fake ROS Envelope와 Domain DTO 변환 검증 |
| Terrain Fixture | Domain, Application, Interface | Fixed PointCloud, ElevationGrid, TerrainAnalysisResult 제공 |
| Assertion Engine | 전체 계층 | 기대 결과, 금지 의존성, KPI 검증 |
| Snapshot Comparator | Domain, Application, Storage | 동일 입력의 Event/State/Storage 결과 비교 |
| Report Generator | 전체 계층 | 테스트 결과와 Acceptance Report 생성 |

---

## 4. 계층별 Mock 목록

| 계층 | Mock / Fake |
|---|---|
| Domain | Fake PerceptionFrame, Fake GasValue, Fake TerrainAnalysisResult |
| Application | Fake EventQueue, Fake StateStore, Fake Clock, InMemoryMissionRepository |
| Interface | MockDetector, MockSLAM, MockTerrainAnalyzer, MockSearchDrivePolicy, MockNavigation, MockRobotController, MockMissionCreationService |
| ROS Adapter Contract | FakeRosEnvelope, MockRosTopicGateway, FakeQoSProfile |
| WebRTC Adapter | MockWebRTCTrackSender, MockDataChannelSender, FakeEncodedPacket |
| Storage Adapter | MockEventRepository, MockMediaRepository, MockMissionRepository, MockLocalStorage, MockSyncQueue |
| SOP Agent | MockSopAgent, MockSopMissionConfigurator, FakeMissionContext |
| UI | MockUiNotifier, FakeOperatorCommand, FakeSearchMissionRequest |

---

## 5. TDD 실행 순서

```text
1. Domain Unit Test 작성
2. Application State/Failover Test 작성
3. Interface Contract Test 작성
4. Adapter Mapper Test 작성
5. Client/Server Module Boundary Test 작성
6. Failure Injection Test 작성
7. Integration Test 작성
8. Simulation / Acceptance Test 작성
```

---

## 6. 계층별 완료 기준

| 계층 | 완료 기준 |
|---|---|
| Domain | `rclpy`, ROS Message, DB, WebRTC import 없이 Unit Test 통과 |
| Application | Event 입력으로 상태 전이 검증 가능 |
| Interface | 모든 Protocol이 Mock 구현체로 대체 가능 |
| ROS Adapter Contract | ROS Runtime 없이 Mapper와 Topic Gateway Contract 테스트 통과 |
| WebRTC Adapter | Track/DataChannel Mock 테스트와 Reconnect 테스트 통과 |
| Storage Adapter | Local Save와 Sync Queue 장애 테스트 통과 |
| Client/Server Boundary | `TC-MOD-*` 테스트 통과 |
| Release Candidate | `TC-LINT-*`, `TC-LAYER-*`, `TC-DEP-*`, `TC-IF-*`, `TC-MOD-*`, P0 Safety Test 통과 |
| Deterministic Gate | `TC-DETVAL-*` 통과 |
| Function Unit Gate | `TC-FUNC-DEC-*`, `TC-FUNC-BND-*` 통과 |
| Mission Creation Gate | `TC-MISSION-*` 통과 |
| Terrain Driven Navigation Gate | `TC-TERRAIN-*` 통과 |
| Dependency Direction Gate | `TC-DEP-*` 통과 |

---

## 7. 최종 원칙

```text
TDD는 Types와 Service의 순수 로직부터 시작한다.
코드 의존성 방향은 `Types -> Config -> Service -> UI`를 따른다.
Test Harness는 Interface를 기준으로 외부 의존성을 대체한다.
Windows 기본 테스트에서는 ROS Runtime까지 진행하지 않는다.
ROS/WebRTC/DB/Robot HW는 Adapter Contract Test 이후 Linux/ROS 프로파일에서 실제 Runtime으로 통합한다.
```
