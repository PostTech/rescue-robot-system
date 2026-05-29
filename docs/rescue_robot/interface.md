# interface.md
# 재난 구조용 바퀴형 사족로봇 시스템
## Compact Interface Specification

---

# 1. 목적

본 문서는 재난 구조용 바퀴형 사족로봇 시스템의 핵심 Interface 구조를 정의한다.

핵심 목표:

```text
1. Module 독립성
2. Replaceable Architecture
3. Failure Isolation
4. TDD/Test Harness 가능 구조
5. ROS2/WebRTC/HW 분리
6. Event-Driven Architecture
7. Mission Creation Contract 고정
```

---

# 2. 핵심 설계 원칙

## 2.1 역할 분리

```text
ROS2 = 내부 모듈 통신
WebRTC = 외부 관제 통신
Event = 시스템 계약(Contract)
```

---

## 2.2 Dependency Rule

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
```

코드 계층의 고정 순서는 `Types -> Config -> Service -> UI`이다.

해석:

```text
UI는 Service/Config/Types를 사용할 수 있다.
Service는 Config/Types를 사용할 수 있다.
Config는 Types만 사용할 수 있다.
Types는 Config/Service/UI를 사용할 수 없다.
```

금지:

```text
Types → Config
Types → Service
Types → UI
Config → Service
Config → UI
Service → UI
UI → DB Driver
UI → ROS Runtime
UI → Robot SDK
```

---

## 2.3 ROS 경량 계층화 정책

ROS2는 내부 통신 Runtime이며, Domain/Application 계층은 ROS2에 직접 의존하지 않는다.

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

금지:

```text
Domain → rclpy
Domain → ROS Message
Application Service → ROS Message
Business Rule → ROS Topic Name
```

허용:

```text
ROS Adapter → ROS Message 변환
ROS Adapter → IRosTopicGateway
ROS Adapter → Application Service 호출
```

이 ROS 계층화는 코드 의존성 순서 `Types -> Config -> Service -> UI`를 침해할 수 없다.

---

## 2.4 Video/Audio 정책

```text
Thermal/RGB/Audio
    !=
ROS2 Topic
```

즉:

```text
Compressed Packet
    ↓
WebRTC Direct Track
```

구조를 사용한다.

---

## 2.5 Failure Isolation

```text
YOLO Failure
    !=
WebRTC Failure

DB Failure
    !=
Robot Stop
```

---

# 3. 전체 시스템 구조

## Robot Side

```text
Sensor Layer
    ↓
Perception Layer
    ↓
Decision Layer
    ↓
Navigation Layer
    ↓
ROS2-WebRTC Bridge
```

---

## Control Center

```text
WebRTC Receiver
    ↓
Mission Core
    ├── Mission Setup UI
    ├── Storage
    └── SOP Agent
```

---

# 4. Robot 영역 분리

## Client-1

```text
ROS2 + WebRTC Bridge
```

역할:

```text
Track 송신
DataChannel 송신
Control 수신
Connection Monitoring
```

---

## Client-2

```text
Thermal/RGB + AI Detection
```

역할:

```text
Decode
YOLO
Thermal Detection
Fusion
Event 생성
```

---

## Client-3

```text
SLAM + Navigation + Robot Control
```

역할:

```text
Localization
Terrain Analysis
Path Planning
Locomotion
```

---

# 5. Control Center 영역 분리

## Server-1

```text
Mission Core
```

---

## Server-2

```text
UI
```

---

## Server-3

```text
Storage / DB
```

---

## Server-4

```text
AI Agent / SOP
```

---

# 6. Client / Server Interface 적용 매트릭스

## 6.1 Client 모듈 Interface

| 모듈 | 책임 | Inbound Interface | Outbound Interface | 직접 의존 금지 |
|---|---|---|---|---|
| Client-1 | ROS2 + WebRTC Bridge | `IDataChannelReceiver`, `IControlCommandReceiver` | `IWebRTCTrackSender`, `IDataChannelSender`, `IRosTopicGateway` | Detector, SLAM Engine, DB |
| Client-2 | Thermal/RGB + AI Detection | `IDetector`, `IMediaPacketReceiver` | `IPerceptionEventPublisher`, `IRosTopicGateway` | WebRTC Session, Robot Motor, DB |
| Client-3 | SLAM + Navigation + Robot Control | `ISlamEngine`, `ITerrainAnalyzer`, `ISearchDrivePolicy`, `INavigationEngine`, `IRobotController` | `IRosTopicGateway`, `IEventPublisher` | WebRTC Track, UI, SOP Agent |

적용 원칙:

```text
Client-1 = Transport / Bridge
Client-2 = Perception / Detection
Client-3 = Navigation / Control
```

Client 간 직접 호출은 금지하고, ROS2 Topic 또는 Event Contract를 통해 연결한다.

---

## 6.2 Server 모듈 Interface

| 모듈 | 책임 | Inbound Interface | Outbound Interface | 직접 의존 금지 |
|---|---|---|---|---|
| Server-1 | Mission Core | `IMissionCore`, `IMissionCreationService`, `IEventSubscriber` | `IUiNotifier`, `IStorageWriter`, `IMissionRepository`, `ISopAgent`, `ISopMissionConfigurator` | WebRTC 내부 구현, DB Driver |
| Server-2 | UI | `IUiNotifier`, `IStatusView` | `IMissionSetupSender`, `IControlCommandSender` | Mission DB, Robot SDK |
| Server-3 | Storage / DB | `IEventRepository`, `IMediaRepository`, `IMissionLogRepository`, `IMissionRepository` | `ISyncQueue` | UI, SOP Agent, Robot Controller |
| Server-4 | AI Agent / SOP | `ISopAgent`, `ISopMissionConfigurator` | `IRecommendationPublisher` | Control Command, Robot Controller, Mission Start |

적용 원칙:

```text
Server-1 = Mission 판단 중심
Server-2 = Operator 입출력 및 임무 생성 요청
Server-3 = 저장 및 Sync
Server-4 = Recommendation Only
```

Server 간 직접 DB 접근 또는 직접 제어 명령 생성을 금지하고, Mission Core와 명시 Interface를 통해 연결한다.

---

## 6.3 모듈 간 허용 통신

| From | To | 허용 경로 | 계약 |
|---|---|---|---|
| Client-2 | Client-1 | ROS2 `/perception/victim_decision`, `/system/events` | `BaseEvent`, `VictimDecision` |
| Client-3 | Client-1 | ROS2 `/robot/pose`, `/navigation/path`, `/system/events` | `Pose3D`, `BaseEvent` |
| Client-1 | Client-3 | ROS2 `/control/command`, `/control/emergency_stop` | `ControlCommand` |
| Client-1 | Server-1 | WebRTC DataChannel `data_event`, `data_status` | `BaseEvent`, `SystemStatus` |
| Server-2 | Client-1 | WebRTC DataChannel `data_control` | `ControlCommand` |
| Server-1 | Server-3 | `IStorageWriter` | Event/Media/Mission Log |
| Server-1 | Server-4 | `ISopAgent.generate()` | Context → Recommendation |
| Server-2 | Server-1 | `IMissionSetupSender.submit_mission_request()` | `SearchMissionRequest` |
| Server-1 | Server-3 | `IMissionRepository` | `MissionDraft`, `SearchMissionPlan` |
| Server-1 | Server-4 | `ISopMissionConfigurator.apply_profile()` | `SearchMissionRequest` → `MissionSetupRecommendation` |
| Server-1 | Server-2 | `IUiNotifier` | Alert/Status/ViewModel |

---

## 6.4 분리 검증 기준

```text
1. Client-2는 WebRTC Track Sender를 직접 호출하지 않는다.
2. Client-3는 UI 또는 SOP Agent를 직접 호출하지 않는다.
3. Server-2는 DB에 직접 저장하지 않는다.
4. Server-4는 ControlCommand를 생성하지 않는다.
5. Server-3는 Mission 판단을 수행하지 않는다.
6. Server-2는 SearchMissionRequest만 생성하고 Mission Draft/Plan 저장은 직접 수행하지 않는다.
7. Server-4는 SOP 기반 Mission 설정 추천만 수행하고 Mission Start를 수행하지 않는다.
8. 모든 모듈은 Protocol 기반 Mock으로 교체 가능해야 한다.
```

---

# 7. 핵심 Domain Data

## 공통 식별자

```python
from typing import NewType

MissionId = NewType("MissionId", str)
RobotId = NewType("RobotId", str)
EventId = NewType("EventId", str)
```

---

## Pose

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Pose3D:
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float
```

---

## VictimDecision

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class VictimDecision:
    victim_detected: bool
    confidence: float
    reason: str
```

---

## CommunicationStatus

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CommunicationStatus:
    webrtc_connected: bool
    fiveg_connected: bool
    packet_loss_rate: float
```

---

## Search Mission Setup

```python
from dataclasses import dataclass, field
from enum import StrEnum


class SearchAreaType(StrEnum):
    POLYGON = "POLYGON"
    WAYPOINT_ROUTE = "WAYPOINT_ROUTE"
    GRID = "GRID"
    GEOFENCE = "GEOFENCE"


class SearchMethod(StrEnum):
    AREA_SWEEP = "AREA_SWEEP"
    PARALLEL_SWEEP = "PARALLEL_SWEEP"
    CREEPING_LINE = "CREEPING_LINE"
    EXPANDING_SQUARE = "EXPANDING_SQUARE"
    SECTOR_SEARCH = "SECTOR_SEARCH"
    TRACKLINE_SEARCH = "TRACKLINE_SEARCH"
    CONTOUR_SEARCH = "CONTOUR_SEARCH"
    TRACK_SWEEP = "TRACK_SWEEP"
    SINGLE_FILE = "SINGLE_FILE"
    GRID_COVERAGE = "GRID_COVERAGE"
    FRONTIER_EXPLORATION = "FRONTIER_EXPLORATION"
    WAYPOINT_ROUTE = "WAYPOINT_ROUTE"
    SPIRAL_SEARCH = "SPIRAL_SEARCH"
    PERIMETER_SEARCH = "PERIMETER_SEARCH"
    MANUAL_ASSISTED = "MANUAL_ASSISTED"


@dataclass(frozen=True)
class SearchArea:
    area_type: SearchAreaType
    coordinates: tuple[Pose3D, ...]
    frame_id: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchMissionRequest:
    request_id: str
    operator_id: str
    mission_name: str
    search_area: SearchArea
    search_method: SearchMethod
    sop_profile_id: str
    priority: str
    created_at_ms: int


@dataclass(frozen=True)
class MissionDraft:
    mission_id: str
    request: SearchMissionRequest
    validation_status: str
    sop_constraints: dict[str, object]
    draft_snapshot_id: str


@dataclass(frozen=True)
class SearchMissionPlan:
    mission_id: str
    search_area: SearchArea
    search_method: SearchMethod
    approved_by: str
    approved_at_ms: int
    plan_snapshot_id: str


@dataclass(frozen=True)
class MissionSetupRecommendation:
    recommended_method: SearchMethod
    constraints: dict[str, object]
    warnings: tuple[str, ...]
    recommendation_only: bool = True
```

---

# 8. Event 구조

## Event 원칙

```text
Event = Immutable
```

---

## BaseEvent

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseEvent:
    event_id: str
    mission_id: str
    robot_id: str
    event_type: str
    timestamp_ms: int
    source_module: str
```

---

## 핵심 Event

```text
THERMAL_ALIVE
RGB_BODY_PART
GAS_HAZARD
SLAM_FAILURE
WEBRTC_DISCONNECTED
EMERGENCY_STOP
SEARCH_MISSION_CREATED
SEARCH_AREA_UPDATED
SEARCH_METHOD_SELECTED
MISSION_SETUP_APPLIED
MISSION_APPROVAL_REQUESTED
TERRAIN_ANALYZED
SEARCH_DRIVE_PROFILE_SELECTED
```

---

## Event Priority

```text
CRITICAL
    >
HIGH
    >
NORMAL
    >
LOW
```

---

# 9. ROS2 Interface

## 핵심 원칙

```text
ROS2 = 내부 상태/결정/Event 전달
```

ROS2 Message는 ROS Adapter 내부에서 Domain DTO로 변환한 뒤 Application Service로 전달한다.

```text
ROS Message
    ↓
ROS Adapter Mapper
    ↓
Domain DTO
    ↓
Application Service
```

---

## 주요 Topic

| Topic | 목적 |
|---|---|
| /imu/data | IMU |
| /gas/data | 가스 데이터 |
| /lidar/points_raw | PointCloud |
| /robot/pose | 위치 |
| /slam/map | 맵 |
| /navigation/path | 경로 |
| /terrain/analysis | 지형 분석 |
| /locomotion/mode | 주행 모드 |
| /perception/victim_decision | 요구조자 판단 |
| /system/events | 시스템 Event |
| /control/command | 원격 제어 |
| /control/emergency_stop | 비상 정지 |

---

## Critical QoS

대상:

```text
/system/events
/control/emergency_stop
/perception/victim_decision
```

정책:

```text
Reliable
KeepLast(10)
```

---

## High Bandwidth QoS

대상:

```text
/lidar/points_raw
```

정책:

```text
BestEffort
KeepLast(3)
```

---

# 10. WebRTC Interface

## Track 구조

| Track | 데이터 |
|---|---|
| video1 | Thermal |
| video2 | RGB |
| audio1 | Robot Audio |
| audio2 | Environment Audio |

---

## DataChannel 구조

| Channel | 데이터 |
|---|---|
| data_sensor | IMU/Gas/Status |
| data_pointcloud | PointCloud |
| data_event | Event |
| data_control | Remote Control |
| data_ack | ACK |

---

## Video Pipeline

```text
Compressed Packet
    ↓
Packet Parser
    ↓
RTP Packetizer
    ↓
WebRTC Track
```

---

## AI Pipeline

```text
Compressed Packet
    ↓
Hardware Decode
    ↓
YOLO / Thermal Detector
    ↓
ROS2 Perception Topic
```

---

## 핵심 원칙

```text
WebRTC Track
    !=
AI Decode Pipeline
```

---

# 11. Navigation Interface

## TerrainAnalysisResult

```python
from dataclasses import dataclass
from enum import StrEnum


class TerrainClass(StrEnum):
    FLAT_OPEN = "FLAT_OPEN"
    MILD_SLOPE = "MILD_SLOPE"
    STEEP_SLOPE = "STEEP_SLOPE"
    ROUGH_RUBBLE = "ROUGH_RUBBLE"
    NARROW_PASSAGE = "NARROW_PASSAGE"
    OBSTACLE_DENSE = "OBSTACLE_DENSE"
    CLIFF_OR_DROP = "CLIFF_OR_DROP"
    UNKNOWN = "UNKNOWN"


class TraversabilityLevel(StrEnum):
    PASSABLE = "PASSABLE"
    CAUTION = "CAUTION"
    REPLAN_REQUIRED = "REPLAN_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class TerrainAnalysisResult:
    terrain_class: TerrainClass
    slope_degree: float
    step_height_cm: float
    roughness_score: float
    obstacle_density: float
    traversability_score: float
    traversability_level: TraversabilityLevel
    traversable: bool
```

---

## LocomotionMode

```python
from enum import StrEnum


class LocomotionMode(StrEnum):
    WHEEL = "WHEEL"
    OBSTACLE_CLIMB = "OBSTACLE_CLIMB"
    SLOW_SAFE = "SLOW_SAFE"
    EDGE_FOLLOW = "EDGE_FOLLOW"
    STOP_AND_REPLAN = "STOP_AND_REPLAN"
    STOP = "STOP"
```

---

## LocomotionDecision

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class LocomotionDecision:
    target_mode: LocomotionMode
    recommended_speed: float
    reason: str
```

---

## SearchDriveProfile

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchDriveProfile:
    search_method: SearchMethod
    locomotion_mode: LocomotionMode
    speed_scale: float
    min_clearance_cm: float
    replan_required: bool
    scan_density: str
    reason: str
```

---

# 12. 핵심 Interface

## Detector

```python
from typing import Protocol


class IDetector(Protocol):
    def infer(self, frame: "Frame") -> "DetectionResult":
        ...
```

---

## SLAM

```python
from typing import Protocol


class ISlamEngine(Protocol):
    def update(self, cloud: "PointCloud") -> Pose3D:
        ...
```

---

## Navigation

```python
from typing import Protocol


class INavigationEngine(Protocol):
    def plan_path(self, pose: Pose3D, goal: "Goal") -> "NavigationPath":
        ...

    def plan_search_path(
        self,
        pose: Pose3D,
        area: SearchArea,
        profile: SearchDriveProfile,
    ) -> "NavigationPath":
        ...

    def decide_locomotion(self, terrain: TerrainAnalysisResult) -> LocomotionDecision:
        ...
```

---

## Terrain Analyzer / Search Drive Policy

```python
from typing import Protocol


class ITerrainAnalyzer(Protocol):
    def analyze(self, cloud: "PointCloud") -> TerrainAnalysisResult:
        ...


class ISearchDrivePolicy(Protocol):
    def select_profile(
        self,
        terrain: TerrainAnalysisResult,
        method: SearchMethod,
    ) -> SearchDriveProfile:
        ...
```

---

## WebRTC

```python
from typing import Protocol


class IWebRTCTrackSender(Protocol):
    def send_video_packet(self, packet: "Packet") -> bool:
        ...

    def send_audio_packet(self, packet: "Packet") -> bool:
        ...
```

---

## DataChannel

```python
from typing import Protocol


class IDataChannelSender(Protocol):
    def send(self, channel: str, message: "DataChannelMessage") -> bool:
        ...


class IDataChannelReceiver(Protocol):
    def receive(self, channel: str) -> "DataChannelMessage":
        ...
```

---

## Media Packet Receiver

```python
from typing import Protocol


class IMediaPacketReceiver(Protocol):
    def receive_packet(self) -> "MediaPacket":
        ...
```

---

## ROS Topic Gateway

```python
from typing import Protocol


class IRosTopicGateway(Protocol):
    def publish(self, topic: str, message: object) -> bool:
        ...

    def subscribe(self, topic: str, handler: "TopicHandler") -> None:
        ...
```

---

## Event Publisher / Subscriber

```python
from typing import Protocol


class IEventPublisher(Protocol):
    def publish_event(self, event: BaseEvent) -> bool:
        ...


class IEventSubscriber(Protocol):
    def subscribe_event(self, event_type: str, handler: "EventHandler") -> None:
        ...


class IPerceptionEventPublisher(Protocol):
    def publish_decision(self, decision: VictimDecision) -> bool:
        ...

    def publish_event(self, event: BaseEvent) -> bool:
        ...
```

---

## Storage

```python
from typing import Protocol


class IEventRepository(Protocol):
    def save(self, event: BaseEvent) -> bool:
        ...
```

---

## Media / Mission Storage

```python
from typing import Protocol


class IMediaRepository(Protocol):
    def save_media(self, media: "MediaChunk") -> bool:
        ...


class IMissionLogRepository(Protocol):
    def append(self, log: "MissionLog") -> bool:
        ...


class IMissionRepository(Protocol):
    def save_draft(self, draft: MissionDraft) -> bool:
        ...

    def save_plan(self, plan: SearchMissionPlan) -> bool:
        ...

    def load_draft(self, mission_id: str) -> MissionDraft:
        ...


class IStorageWriter(Protocol):
    def save_event(self, event: BaseEvent) -> bool:
        ...

    def save_media(self, media: "MediaChunk") -> bool:
        ...
```

---

## Sync Queue

```python
from typing import Protocol


class ISyncQueue(Protocol):
    def enqueue(self, item: "SyncItem") -> bool:
        ...

    def flush(self) -> "SyncResult":
        ...
```

---

## Robot Control

```python
from typing import Protocol


class IRobotController(Protocol):
    def move(self, command: "MotionCommand") -> bool:
        ...

    def stop(self) -> bool:
        ...
```

---

## Control Command

```python
from typing import Protocol


class IControlCommandSender(Protocol):
    def send_command(self, command: "ControlCommand") -> bool:
        ...


class IControlCommandReceiver(Protocol):
    def receive_command(self) -> "ControlCommand":
        ...
```

---

## Mission Core / UI

```python
from typing import Protocol


class IMissionCore(Protocol):
    def handle_event(self, event: BaseEvent) -> "MissionState":
        ...


class IMissionCreationService(Protocol):
    def create_search_mission(self, request: SearchMissionRequest) -> MissionDraft:
        ...

    def validate_search_area(self, area: SearchArea) -> "ValidationResult":
        ...

    def select_search_method(
        self,
        mission_id: str,
        method: SearchMethod,
    ) -> MissionDraft:
        ...

    def submit_for_approval(self, mission_id: str) -> "MissionApprovalRequest":
        ...


class IMissionSetupSender(Protocol):
    def submit_mission_request(self, request: SearchMissionRequest) -> MissionDraft:
        ...


class IUiNotifier(Protocol):
    def notify_alert(self, alert: "OperatorAlert") -> bool:
        ...

    def update_status(self, status: "SystemStatus") -> bool:
        ...


class IStatusView(Protocol):
    def render_status(self, status: "SystemStatus") -> None:
        ...
```

---

## SOP Agent

```python
from typing import Protocol


class ISopAgent(Protocol):
    def generate(self, context: "Context") -> "Recommendation":
        ...


class ISopMissionConfigurator(Protocol):
    def apply_profile(
        self,
        request: SearchMissionRequest,
        sop_profile_id: str,
    ) -> MissionSetupRecommendation:
        ...
```

---

## SOP Recommendation Publisher

```python
from typing import Protocol


class IRecommendationPublisher(Protocol):
    def publish(self, recommendation: "Recommendation") -> bool:
        ...
```

---

# 13. ROS2 ↔ WebRTC Bridge

## 역할

```text
ROS2 Subscriber
    ↓
Data Serialization
    ↓
WebRTC DataChannel
```

---

## 전달 대상

```text
/robot/pose
/gas/data
/system/events
/system/status
/perception/victim_decision
```

---

## Thread 구조

```text
Thread-1 Thermal Track
Thread-2 RGB Track
Thread-3 Audio1 Track
Thread-4 Audio2 Track
Thread-5 Sensor DataChannel
Thread-6 Event DataChannel
Thread-7 PointCloud Channel
Thread-8 Control Receiver
Thread-9 Connection Monitor
```

---

# 14. 네트워크 정책

## 우선순위

```text
1. Emergency Stop
2. Control
3. Critical Event
4. Thermal Video
5. RGB Video
6. Audio
7. PointCloud
```

---

## Network Degraded

```text
PointCloud Downsampling
RGB Bitrate 감소
Audio2 Disable
Thermal 유지
```

---

## Network Disconnected

```text
Local Autonomous Mode
Local Storage
Reconnect Retry
```

---

# 15. Storage Interface

## 저장 대상

```text
Event
Thermal Video
RGB Video
PointCloud
Mission Log
```

---

## 저장 정책

```text
Critical Event 우선 저장
Local Save 우선
Recovery 후 Sync
```

---

# 16. Multi Robot 정책

## Namespace

```text
/robot_001/*
/robot_002/*
```

---

## 공유 대상

```text
Map
Victim Event
Hazard Event
Mission Status
```

---

# 17. Test Harness Interface

## Mock 대상

```text
MockDetector
MockSLAM
MockWebRTC
MockStorage
MockRobotController
MockSOPAgent
```

---

## 검증 대상

```text
Event Ordering
Failover
Reconnect
Emergency Stop
Local Autonomous
```

---

# 18. Replaceable Architecture

| 영역 | 교체 가능 대상 |
|---|---|
| Detector | YOLO → 다른 모델 |
| SLAM | GoSLAM → 다른 SLAM |
| WebRTC | aiortc → 다른 Stack |
| DB | PostgreSQL → SQLite |
| AI Agent | OpenAI → Local LLM |

---

# 19. 최종 핵심

```text
1. 모든 영역은 Interface 기반으로 연결한다.
2. Domain Logic은 Middleware에 의존하지 않는다.
3. Video/Audio는 ROS2를 통과하지 않는다.
4. WebRTC 전송과 AI 추론은 분리한다.
5. Event는 시스템 중심 Contract이다.
6. Failure Isolation을 유지한다.
7. 통신 단절 시 Local Autonomous를 유지한다.
8. 모든 Layer는 Mock/Test Harness 가능해야 한다.
9. ROS Message는 ROS Adapter 밖으로 노출하지 않는다.
```
