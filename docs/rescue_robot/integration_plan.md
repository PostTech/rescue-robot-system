# integration_plan.md
# 재난 구조용 바퀴형 사족로봇 시스템
## System Integration Plan

---

# 1. 목적

본 문서는 재난 구조용 바퀴형 사족로봇 시스템의 전체 통합(Integration) 전략과 Adapter 기반 연결 구조를 정의한다.

핵심 목적:

```text
1. Business Logic 중심 통합 구조 정의
2. ROS2/WebRTC/SLAM/YOLO/HW 분리
3. Adapter 기반 Replaceable Architecture 확보
4. Failure Isolation 구조 유지
5. Mock/Test 가능한 Integration 구조 확보
6. Local Autonomous 기반 재난 대응 구조 확립
```

---

# 2. 전체 시스템 구조

```text
Sensor Layer
    ↓
Adapter Layer
    ↓
Business Logic Layer
    ↓
Event / State Machine
    ↓
Navigation / Storage / WebRTC
    ↓
Operator / Control Center
```

---

# 3. 핵심 통합 원칙

## 3.1 Business Logic 중심 구조

```text
Middleware
    !=
Business Logic
```

즉:

```text
ROS2 교체 가능
WebRTC 교체 가능
SLAM 교체 가능
YOLO 교체 가능
Robot SDK 교체 가능
```

---

## 3.2 Adapter 기반 구조

```text
Business Logic
    ↓
Interface
    ↓
Adapter
    ↓
Middleware / Hardware
```

---

## 3.3 ROS 경량 계층화 구조

ROS2는 내부 통신 수단으로 사용하되, Business Logic은 ROS2에 직접 의존하지 않는다.

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

통합 원칙:

```text
ROS Topic 수신
    ↓
ROS Adapter 변환
    ↓
Domain DTO
    ↓
Business Logic 처리
```

---

## 3.4 Event-Driven 구조

```text
Input
    ↓
Business Event
    ↓
State Transition
    ↓
Action
```

---

## 3.5 Failure Isolation

```text
Single Failure
    !=
Whole System Failure
```

예시:

```text
YOLO Failure
    → Detection만 영향

WebRTC Failure
    → Remote Control만 영향

SLAM Failure
    → Navigation 제한

DB Failure
    → Local Save 유지
```

---

## 3.6 Local Autonomous 유지

```text
Remote Disconnect
    ↓
LOCAL_AUTONOMOUS_MODE
    ↓
Local Navigation
    ↓
Local Detection
    ↓
Local Save
```

---

# 4. 전체 Integration Architecture

```text
Thermal Camera
RGB Camera
LiDAR
IMU
Gas Sensor
        ↓
Sensor Adapter
        ↓
Detector Adapter
SLAM Adapter
        ↓
Business Logic
        ↓
Event Queue
        ↓
State Machine
        ↓
Navigation
Robot Controller
Storage
WebRTC
        ↓
Operator UI / SOP Agent
```

---

# 5. Adapter Integration 구조

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
| MissionCreationAdapter | 탐색 임무 생성 요청 처리 | UI ↔ Mission Core |
| MissionRepositoryAdapter | Mission Draft/Plan 저장 | Mission Core ↔ Storage |
| SopMissionConfiguratorAdapter | SOP 기반 임무 설정 추천 | Mission Core ↔ SOP Agent |

---

# 6. Sensor Integration Plan

## 6.1 Thermal Camera

```text
Thermal Camera
    ↓
GStreamer Parsing
    ↓
Sensor Adapter
    ↓
WebRTC Direct Track
    +
Detector Decode Pipeline
```

핵심 원칙:

```text
WebRTC
    !=
AI Decode
```

---

## 6.2 RGB Camera

```text
RGB Camera
    ↓
GStreamer Parsing
    ↓
Encoded Packet
    ├── WebRTC 송신
    └── AI Decode
```

---

## 6.3 LiDAR

```text
LiDAR
    ↓
PointCloud Adapter
    ↓
SLAM Adapter
    ↓
Localization / Terrain Analysis
```

---

## 6.4 IMU

```text
IMU
    ↓
ROS2 Topic
    ↓
SLAM Adapter
```

---

## 6.5 Gas Sensor

```text
Gas Sensor
    ↓
ROS2 Topic
    ↓
Business Logic
    ↓
Hazard Decision
```

---

# 7. ROS2 Integration Plan

## 7.1 역할

```text
Internal Module Communication
```

ROS2는 Adapter 계층에서만 직접 다룬다.

```text
ROS Node / Topic
    ↓
ROS2Adapter
    ↓
Interface
    ↓
Application Service
    ↓
Domain Logic
```

---

## 7.2 핵심 원칙

```text
Video/Audio
    !=
ROS2 Topic
```

즉:

```text
Thermal/RGB/Audio
    ↓
WebRTC Direct Track
```

ROS2 미사용.

---

## 7.3 ROS2 Topic 구조

### Sensor Topic

```text
/imu/data
/gas/data
/lidar/points_raw
```

---

### Navigation Topic

```text
/slam/map
/robot/pose
/navigation/path
/terrain/analysis
/locomotion/mode
```

---

### Perception Topic

```text
/perception/thermal_detection
/perception/rgb_detection
/perception/audio_detection
/perception/victim_decision
```

---

### System Topic

```text
/system/events
/system/status
/control/command
```

---

## 7.4 QoS 정책

| Topic | QoS |
|---|---|
| /system/events | Reliable |
| /control/command | Reliable |
| /lidar/points_raw | BestEffort |
| /imu/data | SensorDataQoS |

---

# 8. WebRTC Integration Plan

## 8.1 역할

```text
External Remote Communication
```

---

## 8.2 Track 구조

### Video Track

```text
video1 = Thermal
video2 = RGB
```

---

### Audio Track

```text
audio1 = Operator
audio2 = Environment
```

---

### DataChannel

```text
data_sensor
data_pointcloud
data_event
data_status
data_control
```

---

## 8.3 Priority 정책

```text
Control
    >
Event
    >
Thermal
    >
RGB
    >
Audio
    >
PointCloud
```

---

## 8.4 PointCloud 전송

```text
PointCloud
    ↓
Compression
    ↓
DataChannel
```

---

## 8.5 Connection State

```text
CONNECTED
DEGRADED
DISCONNECTED
RECONNECTING
```

---

## 8.6 Reconnect 흐름

```text
ICE Disconnect
    ↓
Reconnect Attempt
    ↓
Recovery
    or
LOCAL_AUTONOMOUS_MODE
```

---

# 9. Detector Integration Plan

## 9.1 Detection 구조

```text
Encoded Packet
    ↓
Decode
    ↓
Thermal / RGB / Audio Detection
    ↓
Fusion
    ↓
Victim Decision
```

---

## 9.2 Fusion 우선순위

```text
Thermal
    >
RGB
    >
Audio
```

---

## 9.3 출력 Topic

```text
/perception/thermal_detection
/perception/rgb_detection
/perception/audio_detection
/perception/victim_decision
```

---

## 9.4 Event 구조

```text
THERMAL_DETECTED
RGB_BODY_PART_DETECTED
AUDIO_HELP_DETECTED
VICTIM_CANDIDATE_DETECTED
```

---

## 9.5 Failure Isolation

```text
YOLO Failure
    !=
Video Failure
```

즉:

```text
AI Failure
    ↓
AI Restart
Video 유지
```

---

# 10. SLAM Integration Plan

## 10.1 입력 구조

```text
/lidar/points_raw
/imu/data
```

---

## 10.2 Localization

```text
PointCloud
    +
IMU
    ↓
SLAM Engine
    ↓
/robot/pose
```

---

## 10.3 Terrain Analysis

```text
PointCloud
    ↓
Elevation Grid Map
    ↓
Slope / Roughness / Step Height / Obstacle Density
    ↓
TerrainAnalysisResult
    ↓
FLAT_OPEN
MILD_SLOPE
STEEP_SLOPE
ROUGH_RUBBLE
NARROW_PASSAGE
OBSTACLE_DENSE
CLIFF_OR_DROP
```

---

## 10.4 지형 + 탐색 방법 기반 Navigation 연동

```text
SLAM
    ↓
Terrain Analysis
    ↓
SearchMethod
    ↓
SearchDriveProfile
    ↓
Path Planning
    ↓
Robot Controller
```

정책:

```text
SearchMethod only
    !=
Drive Decision

TerrainAnalysisResult + SearchMethod
    =
SearchDriveProfile
```

---

## 10.5 Drift Detection

```text
Pose History
    ↓
Drift Detection
    ↓
SLAM_DRIFT_DETECTED
```

---

## 10.6 Local Autonomous 연동

```text
Communication Failure
    ↓
Local SLAM 유지
    ↓
Local Navigation 유지
```

---

# 11. Robot Controller Integration Plan

## 11.1 Motion Flow

```text
Navigation Path
    ↓
Robot Controller Adapter
    ↓
Motor Driver
```

---

## 11.2 Operator Control

```text
Operator
    ↓
WebRTC data_control
    ↓
Robot Controller
```

---

## 11.3 Emergency Stop

```text
ANY_STATE
    ↓
EMERGENCY_STOP
    ↓
All Motion Stop
```

---

## 11.4 Locomotion Mode

```text
Wheel Mode
Obstacle Climb Mode
Safe Mode
Emergency Stop
```

---

## 11.5 Safety 우선순위

```text
Emergency Stop
    >
Safe Mode
    >
Operator Command
    >
Autonomous Navigation
```

---

## 11.6 AI 직접 제어 금지

```text
AI Recommendation
    !=
Direct Motion Control
```

---

# 12. Storage Integration Plan

## 12.1 Event 저장

```text
Business Event
    ↓
Storage Adapter
    ↓
DB
```

---

## 12.2 Media 저장

```text
Encoded Media
    ↓
Compression
    ↓
Object Storage
```

---

## 12.3 Local Save 구조

```text
Network Failure
    ↓
Local Save
    ↓
Recovery
    ↓
Sync
```

---

## 12.4 Critical Event 우선 보존

```text
Critical Event
    >
Mission Event
    >
Raw Media
```

---

## 12.5 Sync 정책

```text
FIFO
Priority 기반
Retry 지원
```

---

# 13. SOP / AI Agent Integration Plan

## 13.1 구조

```text
Business Event
    ↓
SOP Agent
    ↓
Recommendation
    ↓
Operator
```

---

## 13.2 핵심 원칙

```text
AI Agent
    =
Recommendation Only
```

직접 제어 금지.

---

## 13.3 SOP 기반 Mission 설정 통합

```text
SearchMissionRequest
    ↓
Mission Core
    ↓
SopMissionConfiguratorAdapter
    ↓
MissionSetupRecommendation
    ↓
Mission Core Validation
    ↓
Mission Repository
```

금지:

```text
SOP Agent → Mission Start
SOP Agent → ControlCommand
UI → Storage Direct Write
```

---

# 14. Event / State Machine Integration

## 14.1 Event Flow

```text
Sensor Input
    ↓
Business Event
    ↓
Event Queue
    ↓
State Machine
    ↓
Action
```

---

## 14.2 주요 Event

```text
THERMAL_DETECTED
RGB_BODY_PART_DETECTED
GAS_HAZARD_DETECTED
SLAM_DRIFT_DETECTED
NETWORK_DISCONNECTED
EMERGENCY_STOP
```

---

## 14.3 State Flow

```text
IDLE
    ↓
MISSION_START
    ↓
AUTONOMOUS_OPERATION
    ↓
DEGRADED
    ↓
SAFE_MODE
    ↓
RECOVERY
```

---

## 14.4 Emergency Flow

```text
ANY_STATE
    ↓
EMERGENCY_STOP
```

---

# 15. Local Autonomous Integration

## 15.1 진입 조건

```text
Network Disconnected
```

---

## 15.2 유지 기능

```text
Local SLAM
Obstacle Avoidance
Victim Detection
Critical Event Save
Terrain Following
```

---

## 15.3 복구 흐름

```text
Reconnect
    ↓
Sync
    ↓
Mission Resume
```

---

# 16. Multi Robot Integration

## 16.1 Namespace 구조

```text
/robot01/
/robot02/
/robot03/
```

---

## 16.2 공유 데이터

```text
Map
Mission Status
Victim Event
Hazard Event
```

---

## 16.3 Mission Coordination

```text
Task Assignment
Event Sharing
Shared Map
```

---

# 17. Failure Isolation Integration

| 장애 | 영향 범위 | 유지 기능 |
|---|---|---|
| YOLO Failure | Detection만 영향 | Video 유지 |
| WebRTC Failure | Remote만 영향 | Local Autonomous |
| SLAM Failure | Navigation 제한 | Detection 유지 |
| DB Failure | Remote Save 실패 | Local Save 유지 |
| RGB Failure | RGB Detection 영향 | Thermal 유지 |
| Audio Failure | Audio 영향 | Detection 유지 |
| PointCloud Drop | Mapping 영향 | Navigation 유지 |
| Motor Failure | Motion 제한 | Safety 유지 |

---

# 18. Integration Test Plan

## 18.1 Unit Integration

```text
Adapter ↔ Interface
DTO 변환
Event 변환
```

---

## 18.2 Module Integration

```text
Detector ↔ Business Logic
SLAM ↔ Navigation
Storage ↔ Event
WebRTC ↔ Operator UI
Mission Setup UI ↔ Mission Core
Mission Core ↔ Mission Repository
Mission Core ↔ SOP Mission Configurator
```

---

## 18.3 System Integration

```text
Sensor → Detection → Navigation → Robot Control
```

---

## 18.4 Failure Integration

```text
AI Failure
SLAM Failure
ICE Disconnect
DB Failure
Storage Full
```

---

## 18.5 Simulation Integration

환경:

```text
Isaac Sim
Gazebo
Unity
Mujoco
```

---

## 18.6 Field Integration

환경:

```text
Mountain
Tunnel
Debris
Smoke
Low Visibility
```

---

# 19. Integration 우선순위

## Priority-1

```text
Sensor
Detector
SLAM
Navigation
Robot Control
```

---

## Priority-2

```text
WebRTC
Storage
Event System
```

---

## Priority-3

```text
SOP Agent
Multi Robot
Optimization
```

---

# 20. Deployment Integration

## Robot Side

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

---

## Control Center Side

```text
WebRTC Receiver
Mission Management
UI
SOP Agent
Storage
```

---

# 21. 최종 Integration 구조

```text
Sensor
    ↓
Adapter
    ↓
Business Logic
    ↓
Event / State Machine
    ↓
Navigation / Storage / WebRTC
    ↓
Operator / Control Center
```

---

# 22. 완료 기준

```text
1. Business Logic 독립 유지
2. ROS2/WebRTC/HW 교체 가능
3. AI Failure 시 Video 유지
4. 통신 단절 시 Local Autonomous 유지
5. Emergency Stop 최우선 동작
6. Critical Event Local Save 유지
7. Adapter Mock 기반 Test 가능
8. Multi Robot Namespace 지원
9. Domain/Application 계층의 ROS 독립성 검증 완료
10. Failure Isolation 검증 완료
11. Field Integration 완료
```

---

# 23. 최종 핵심

```text
integration_plan.md는
Adapter 기반으로
ROS2/WebRTC/SLAM/YOLO/HW를
Business Logic 중심으로 통합하기 위한
전체 Integration 실행 계획이다.
```
