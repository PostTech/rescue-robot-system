# SDD.md
# 재난 구조용 바퀴형 사족로봇 시스템
## Compact Software Design Description

---

# 1. 시스템 목적

본 시스템은 재난 환경에서 요구조자 탐색 및 구조 지원을 수행하는 AI 기반 바퀴형 사족로봇 시스템이다.

대상 환경:

- 산악 실종자 수색
- 붕괴 건물 탐색
- 지하 공동구 탐색
- 화재/연기 환경

핵심 기능:

- 험지 이동
- 요구조자 탐색
- 위험 탐지
- 자율주행
- 3D LiDAR 기반 지형 분석
- 지형과 탐색 방법 기반 주행 정책 결정
- 원격 관제
- 관제자 기반 탐색 임무 생성
- 탐색 구역 지정 및 탐색 방법 선택
- SOP Profile 기반 임무 설정
- 통신 단절 대응

---

# 2. 시스템 구성

## Sensor Layer

```text
Thermal Camera
RGB Camera
3D LiDAR
Gas Sensor
IMU
Microphone
```

---

## AI Layer

```text
Thermal Detection
RGB Detection
Audio Detection
Terrain Analysis
Fusion Logic
```

---

## Navigation Layer

```text
SLAM
3D LiDAR Terrain Analysis
Localization
Path Planning
Obstacle Avoidance
Locomotion Decision
```

---

## Communication Layer

```text
ROS2
WebRTC
5G / Mesh Network
```

---

## Storage Layer

```text
Event DB
Media Storage
PointCloud Storage
Mission Log
Mission Draft / Plan
```

---

# 3. 아키텍처 원칙

## 핵심 원칙

```text
Business Logic
    !=
Middleware
```

즉:

```text
ROS2 = Middleware
WebRTC = Transport
Business Logic = Core
```

---

## Dependency Rule

```text
Types -> Config -> Service -> UI
```

허용:

```text
UI → Service/Config/Types
Service → Config/Types
Config → Types
Adapter → Service Protocol / Types
```

금지:

```text
Types → Config/Service/UI
Config → Service/UI
Service → UI
Service → ROS2/WebRTC/DB Driver 직접 접근
UI → ROS Runtime/DB Driver/Robot SDK 직접 접근
```

---

# 4. Runtime 구조

## Robot Side

```text
Sensor
    ↓
Perception
    ↓
Decision Engine
    ↓
Navigation
    ↓
Robot Controller
    ↓
WebRTC
```

---

## Control Center

```text
WebRTC Receiver
    ↓
Track Dispatcher
    ↓
Mission Core
    ├── Mission Setup UI
    ├── SOP Agent
    └── Storage
```

---

# 5. 핵심 비즈니스 규칙

## 요구조자 탐색 우선순위

```text
Thermal
    >
RGB
    >
Audio
```

---

## Thermal Detection

조건:

```text
34°C ≤ temp ≤ 38°C
```

결과:

```text
VictimDetected = TRUE
```

---

## RGB Detection

조건:

```text
confidence ≥ 0.7
```

결과:

```text
VictimDetected = TRUE
```

---

## Search Mission Creation

관제자는 Mission Setup UI에서 탐색 임무를 생성하고, Mission Core는 구역과 방법을 검증한다.

필수 조건:

```text
SearchMissionRequest
    =
Operator ID
    +
Search Area
    +
Search Method
    +
SOP Profile
```

활성화 조건:

```text
Mission Draft Valid
    +
Mission Commander Approval
    =
Search Mission Plan Active
```

금지:

```text
SOP Agent → Mission Start
SOP Agent → ControlCommand
UI → Mission DB Direct Write
```

---

## 3D LiDAR Terrain Driven Navigation

3D LiDAR PointCloud는 지형의 경사, 거칠기, 단차, 장애물 밀도를 계산하는 입력으로 사용한다.

```text
PointCloud
    ↓
Elevation Grid Map
    ↓
TerrainAnalysisResult
    ↓
TerrainClass
    ↓
SearchDriveProfile
    ↓
NavigationPath
```

주행 결정은 탐색 방법과 지형을 함께 사용한다.

| Terrain | Search Method | Drive Policy |
|---|---|---|
| Flat/Open | Parallel Sweep, Grid Coverage | 정상 속도 직선 주행 |
| Slope | Contour Search | 등고선 우선 저속 주행 |
| Rubble | Frontier Exploration | 장애물 등반 또는 짧은 재계획 |
| Narrow Passage | Single File, Trackline | 중앙선 추종 저속 주행 |
| Cliff/Drop | Perimeter Search | 진입 금지, 정지/우회 |

---

## Gas Hazard

조건:

```text
CO2 > Threshold
```

결과:

```text
HazardDetected = TRUE
```

---

## Locomotion Decision

조건:

```text
Slope ≤ 20°
→ WHEEL

Slope > 20°
→ OBSTACLE_CLIMB
```

---

## Communication Failure

조건:

```text
WebRTC disconnected
AND
5G disconnected
```

동작:

```text
Local Autonomous Mode
Local SLAM 유지
Local Save 유지
```

---

# 6. 핵심 자료구조

## Input

```python
from dataclasses import dataclass
from enum import StrEnum


class LocomotionMode(StrEnum):
    WHEEL = "WHEEL"
    OBSTACLE_CLIMB = "OBSTACLE_CLIMB"


@dataclass(frozen=True)
class PerceptionFrame:
    thermal_temp: float
    rgb_human_detected: bool
    rgb_confidence: float
    audio_help_detected: bool
    gas_co2: float
    slope: float
    obstacle_height: float
    webrtc_connected: bool
    fiveg_connected: bool
```

---

## Output

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RescueDecision:
    victim_detected: bool
    reason: str
    confidence: float
    mode: LocomotionMode
    local_autonomous_mode: bool
    gas_hazard: bool
```

---

# 7. ROS2 구조

## 주요 Topic

```text
/camera/thermal
/camera/rgb
/lidar/points
/gas/data
/imu/data
```

---

## Decision Topic

```text
/rescue/decision
/robot/gait_mode
/system/failover
```

---

# 8. WebRTC 구조

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

## 정책

```text
Thermal Priority
PointCloud Drop 가능
Encoded Stream Direct Transfer
```

---

# 9. Event 구조

## 주요 Event

```text
VictimDetected
GasHazardDetected
SLAMFailure
BatteryLow
EmergencyStop
```

---

# 10. 장애 대응

## Thermal Failure

```text
RGB Fallback
```

---

## SLAM Failure

```text
Safe Mode
Re-localization
```

---

## GPU OOM

```text
FPS Reduction
Compression
```

---

## Network Failure

```text
Reconnect
Local Autonomous
```

---

# 11. TDD 핵심 테스트

## Thermal Detection

입력:

```text
thermal_temp = 36.5
```

결과:

```text
victim_detected = true
```

---

## Gas Hazard

입력:

```text
co2 > threshold
```

결과:

```text
gas_hazard = true
```

---

## Communication Failure

입력:

```text
webrtc = false
5g = false
```

결과:

```text
local_autonomous_mode = true
```

---

# 12. Test Harness 구조

```text
Mock Sensor
    ↓
Decision Engine
    ↓
Event Generator
    ↓
Result Checker
```

---

# 13. Deployment 구조

## Robot Side

```text
ROS2
SLAM
Navigation
Detector
WebRTC
Storage
```

---

## Control Center

```text
WebRTC Receiver
Mission UI
SOP Agent
Central Storage
```

---

# 14. 구현 단계

> 아래는 개략 요약이다. 상세 12-Phase 로드맵은 `implementation_roadmap.md`를 참조한다.

```text
Data Structure
Event Schema
Interface
```

---

## Phase-2

```text
Business Logic
TDD
Mock Test
```

---

## Phase-3

```text
ROS2 Adapter
WebRTC Adapter
SLAM Integration
```

---

## Phase-4

```text
Simulation Test
Field Test
Acceptance Test
```

---

# 15. 최종 핵심

```text
1. Business Logic 독립성
2. Event 기반 구조
3. WebRTC 멀티트랙 구조
4. Local Autonomous 유지
5. Failure Isolation 유지
6. 탐색 임무 생성은 Mission Core 중심으로 검증 및 승인
7. SOP는 임무 설정 추천만 수행하고 직접 제어하지 않음
8. 3D LiDAR 지형 분석과 탐색 방법을 결합해 주행 정책을 결정
```
