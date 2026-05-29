# implementation_roadmap.md
# 재난 구조용 바퀴형 사족로봇 시스템
## Compact Implementation Roadmap & Context Architecture

---

# 1. 목적 및 AI 하네스 문맥 관리 아키텍처

본 문서는 실제 개발자 및 AI 에이전트가 완벽한 자립적 컨텍스트(Context) 하에서 안전하게 시스템을 고립 빌드할 수 있는 구현 순서와 설계 방법론을 정의한다.

### 🔄 하향식 설계(Top-Down Design) & 상향식 구현(Bottom-Up Implementation)

본 로드맵은 AI 하네스의 높은 정밀도와 TDD의 무결성을 달성하기 위해 **"Top-Down 설계 후 Interface 동결 ➡️ Bottom-Up 개별 인프라 TDD 구현"**의 조화로운 아키텍처를 추종한다.

```text
[전체 요구사항 / 기획서] (requirements_spec.md)
       │
       ▼  【 Top-Down 설계 (하향식 설계 - Business Alignment) 】
 1단계: 비즈니스 로직 설계 (Plan Context)
       │  - 기술 스택 배제, 순수 비즈니스 목적 및 불변 도메인 룰 설계
       ▼
 2단계: 인터페이스 & 어댑터 정의 (Interface Context)
          - Hexagonal Port 계약 동결, 입출력 DTO 명세 고정 (Contract Freeze)
=============================================================================
          - 단단한 아키텍처적 경계(Boundary) 확정 이후, 인프라는 독립적으로 구현
       ▲
       │  【 Bottom-Up 구현 (상향식 TDD 구현 - Component Integration) 】
 3단계: 세부 기능 구현 (DB / 통신 / UI 구현 Context)
          - DB Persistence, Network/WebSocket 통신, Presentation UI 컴포넌트
          - 각 영역은 하단 단위 테스트부터 상향식으로 다져 올리며 Port에 결합
```

1.  **Top-Down 설계 (1~2단계)**: 기획 요구사항을 도메인 모델로 번역하고 모듈 간의 협력 규격(Port/Interface)을 동결하는 단계는 시스템의 거시적인 요구사항(Top)에서 시작하여 세부 규격(Down)으로 흘러야 비즈니스 정렬이 완벽하게 달성됩니다.
2.  **Bottom-Up 구현 (3단계)**: 2단계의 인터페이스 계약이 동결되는 순간, 하위 DB 영속성, 실시간 웹소켓 통신, 프론트 UI 등은 서로의 상세한 구현을 모른 채, 각각의 인프라 스택 최하단 단위 테스트부터 견고하게 조립하여 상위 포트에 끼워 맞추는 상향식 TDD 구현이 극히 유효합니다.

---

# 2. 핵심 개발 원칙

## 2.1 Interface First

외부 시스템보다 Interface를 먼저 구현한다. (Top-Down 설계의 핵심 관문)

```text
Business Logic
    ↓
Application Service
    ↓
Interface
    ↓
Middleware / HW
```

---

## 2.2 Mock First

실제 HW 연결 전에 Mock 기반 검증 수행.

```text
Mock Sensor
Mock SLAM
Mock WebRTC
Mock Storage
```

---

## 2.3 ROS Adapter Boundary

ROS2 Topic과 Message는 Adapter 밖으로 노출하지 않는다.

```text
Domain / Business Logic
    ↓
Application Service
    ↓
Interface
    ↓
ROS Adapter
    ↓
ROS Topic / Node
```

---

## 2.4 Event-Driven

모든 Module은 Event 기반으로 연결한다.

```text
Input
    ↓
Event
    ↓
State Transition
    ↓
Action
```

---

## 2.5 Failure Isolation

핵심 원칙:

```text
Single Failure
    !=
Whole System Failure
```

---

## 2.6 Safety First

우선순위:

```text
Emergency Stop
    >
Safe Mode
    >
Mission
```

---

# 3. 전체 구현 흐름

```text
SDD
    ↓
Interface
    ↓
TDD
    ↓
Mock
    ↓
Business Logic
    ↓
Adapter
    ↓
ROS2/WebRTC Integration
    ↓
Simulation
    ↓
Field Test
    ↓
Acceptance
```

---

# 4. Phase-1 Foundation

# 목표

핵심 구조 정의.

신규 기능은 반드시 Types 정의부터 시작한다.

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
```

Types 없이 Service 또는 UI부터 구현한 변경은 완료로 인정하지 않는다.

---

## 구현 대상

```text
Types Definition
Config Definition
Service Contract
UI Contract
Data Structure
Event Schema
State Definition
Interface
Layer Boundary
Types / Config / Service / UI Dependency Boundary
ROS Adapter Contract
```

---

## 주요 Interface

```python
from typing import Protocol


class IDetector(Protocol): ...
class ISlamEngine(Protocol): ...
class ITerrainAnalyzer(Protocol): ...
class ISearchDrivePolicy(Protocol): ...
class INavigationEngine(Protocol): ...
class IWebRTCTrackSender(Protocol): ...
class IEventRepository(Protocol): ...
class IMediaRepository(Protocol): ...
class IMissionSetupSender(Protocol): ...
class IMissionCreationService(Protocol): ...
class IMissionRepository(Protocol): ...
class ISopMissionConfigurator(Protocol): ...
class IRobotController(Protocol): ...
```

---

## 검증

```text
Python Syntax Check
Python Lint
Type Check
Dependency Injection
Interface Contract
Layer Dependency Check
Dependency Direction Check
```

---

# 5. Phase-2 Mock/TDD

# 목표

실제 HW 없이 전체 흐름 검증.

---

## 구현 대상

```text
Mock Detector
Mock SLAM
Mock Terrain Analyzer
Mock Search Drive Policy
Mock WebRTC
Mock Robot Controller
Mock Storage
Mock Mission Repository
Mock SOP Mission Configurator
```

---

## TDD 대상

```text
Thermal Detection
Gas Hazard
State Transition
Local Autonomous
Emergency Stop
Search Mission Creation
Search Area Validation
Search Method Selection
SOP Mission Setup
Terrain Analysis
Terrain Driven Search Drive Policy
```

---

## Test Harness

```text
Fake Sensor
    ↓
Business Logic
    ↓
Event System
    ↓
Result Checker
```

---

## 검증

```text
Unit Test
Failure Injection
State Validation
```

---

# 6. Phase-3 Business Logic

# 목표

Middleware 없는 핵심 로직 구현.

---

## 구현 대상

```text
Event System
State Machine
Fusion Logic
Mission Logic
Mission Creation Logic
Terrain Analysis Logic
Search Drive Policy Logic
Safety Logic
Application Service
```

---

## 핵심 규칙

```text
Thermal
    >
RGB
    >
Audio
```

---

## 주요 Event

```text
THERMAL_DETECTED
GAS_ALERT
SLAM_FAILURE
NETWORK_DISCONNECTED
EMERGENCY_STOP
SEARCH_MISSION_CREATED
SEARCH_AREA_UPDATED
SEARCH_METHOD_SELECTED
MISSION_SETUP_APPLIED
TERRAIN_ANALYZED
SEARCH_DRIVE_PROFILE_SELECTED
```

---

## 검증

```text
Event Ordering
Recovery
Failover
Safe Mode
Mission Draft Snapshot
Mission Approval Guard
Terrain Class Decision
SearchDriveProfile Decision
```

---

# 7. Phase-4 Detector Integration

# 목표

AI Detection 연결.

---

## 구성

```text
Thermal Detector
RGB Detector
Audio Detector
Fusion Logic
```

---

## 구조

```text
Encoded Packet
    ├── WebRTC Track
    └── Decode → Inference
```

---

## 핵심 원칙

```text
Video Transmission
    !=
AI Inference
```

---

## 검증

```text
Detection Accuracy
False Positive
Inference Latency
CUDA OOM
```

---

# 8. Phase-5 SLAM/Navigation

# 목표

자율주행 연결.

---

## 구성

```text
SLAM
Terrain Analysis
Path Planning
Obstacle Avoidance
Robot Controller
```

---

## Locomotion

```text
WHEEL
OBSTACLE_CLIMB
SAFE_MODE
```

---

## 검증

```text
Localization
Terrain Following
Obstacle Avoidance
Drift Recovery
```

---

# 9. Phase-6 ROS2 Integration

# 목표

내부 모듈 연결.

---

## 역할

```text
Module ↔ Module Communication
```

ROS2 Integration은 Adapter 구현 단계이며, Domain/Application 계층 변경을 최소화한다.

```text
ROS Message
    ↓
ROS Adapter Mapper
    ↓
Domain DTO
```

---

## 주요 Topic

```text
/slam/map
/robot/pose
/navigation/path
/perception/victim_decision
/system/events
```

---

## 핵심 원칙

```text
Video/Audio
    !=
ROS2 Topic
```

---

## 검증

```text
Topic Flow
QoS
Namespace
Latency
```

---

# 10. Phase-7 WebRTC Integration

# 목표

원격 관제 연결.

---

## Track

```text
Thermal Video
RGB Video
Audio
PointCloud
Event
Control
```

---

## 우선순위

```text
Control
    >
Thermal
    >
RGB
```

---

## 검증

```text
ICE Recovery
Packet Loss
Reconnect
Thermal Priority
```

---

# 11. Phase-8 Storage Integration

# 목표

Mission/Event 저장.

---

## 저장 대상

```text
Event
Video
PointCloud
Mission Log
```

---

## 구조

```text
Local Save
    ↓
Recovery
    ↓
Remote Sync
```

---

## 검증

```text
DB Failure
Storage Full
Sync Retry
Critical Event 유지
```

---

# 12. Phase-9 Deployment

# Robot Side

```text
Sensor
ROS2
Detector
SLAM
Navigation
WebRTC
Storage
```

---

# Control Center

```text
WebRTC Receiver
Mission UI
SOP Agent
Storage
```

---

# Container 구조

```text
detector_container
slam_container
navigation_container
webrtc_container
storage_container
```

---

# 검증

```text
Docker
GPU
Network
Monitoring
```

---

# 13. Phase-10 Simulation

# 환경

```text
Isaac Sim
Gazebo
Unity
Mujoco
```

---

# 시나리오

```text
Mountain
Tunnel
Debris
Low Light
Smoke
```

---

# 검증

```text
Victim Detection
Terrain Following
Communication Recovery
Local Autonomous
```

---

# 14. Phase-11 Field Test

# 환경

```text
산악
터널
붕괴지형
화재 환경
```

---

# 검증

```text
Mission Success
Obstacle Traversal
Thermal Detection
Recovery
```

---

# KPI

```text
Victim Detection ≥ 90%
Reconnect < 10 sec
Obstacle Success ≥ 90%
```

---

# 15. Phase-12 Acceptance

# 검증 대상

```text
Mission Capability
Safety
Recovery
Operational Deployment
```

---

# Pass 조건

```text
Critical Failure 없음
Mission 유지 가능
Recovery 가능
```

---

# 16. 운영 구조

# Operator 역할

```text
Monitoring
Approval
Emergency 대응
```

---

# AI/SOP 역할

```text
Recommendation Only
```

---

# 핵심 원칙

```text
AI Recommendation
    !=
Direct Motion Control
```

---

# 17. 유지보수 구조

# Monitoring

```text
CPU
GPU
Temperature
Battery
Network
Storage
```

---

# OTA 대상

```text
Detector
SLAM
Navigation
Container
```

---

# Recovery

```text
Restart
Rollback
Fallback
```

---

# 18. 최종 핵심

```text
1. Interface First
2. Mock First
3. Event-Driven
4. Failure Isolation
5. Local Autonomous
6. Thermal Priority
7. Safety First
8. Business Logic Independent
9. ROS Adapter Boundary
```
