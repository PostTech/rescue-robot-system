# 상세 Interface 및 데이터 스키마

## 1. 목적

본 문서는 Python 구현 기준의 Event, ROS2 Topic, WebRTC DataChannel, Storage Payload 스키마를 정의한다.

---

## 2. Python Domain Schema

```python
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


@dataclass(frozen=True)
class BaseEvent:
    event_id: str
    mission_id: str
    robot_id: str
    event_type: str
    priority: EventPriority
    timestamp_ms: int
    source_module: str
    payload: dict[str, Any] = field(default_factory=dict)
```

---

## 3. Event Payload

| Event Type | Priority | Payload |
|---|---|---|
| `THERMAL_DETECTED` | HIGH | `temperature`, `bbox`, `confidence`, `frame_id` |
| `RGB_BODY_PART_DETECTED` | NORMAL | `label`, `bbox`, `confidence`, `frame_id` |
| `AUDIO_HELP_DETECTED` | NORMAL | `keyword`, `confidence`, `audio_ts_ms` |
| `VICTIM_CANDIDATE_DETECTED` | CRITICAL | `fusion_score`, `evidence`, `pose` |
| `GAS_HAZARD_DETECTED` | CRITICAL | `gas_type`, `value`, `threshold`, `level` |
| `SLAM_DRIFT_DETECTED` | HIGH | `drift_score`, `pose`, `map_id` |
| `NETWORK_DISCONNECTED` | HIGH | `webrtc`, `fiveg`, `packet_loss_rate` |
| `EMERGENCY_STOP` | CRITICAL | `trigger`, `operator_id`, `reason` |
| `SEARCH_MISSION_CREATED` | HIGH | `mission_id`, `operator_id`, `sop_profile_id` |
| `SEARCH_AREA_UPDATED` | HIGH | `mission_id`, `area_type`, `coordinates_hash` |
| `SEARCH_METHOD_SELECTED` | HIGH | `mission_id`, `search_method`, `selected_by` |
| `MISSION_SETUP_APPLIED` | HIGH | `mission_id`, `sop_profile_id`, `constraints_hash` |
| `MISSION_APPROVAL_REQUESTED` | HIGH | `mission_id`, `requested_by`, `draft_snapshot_id` |
| `TERRAIN_ANALYZED` | NORMAL | `terrain_class`, `traversability_score`, `map_id` |
| `SEARCH_DRIVE_PROFILE_SELECTED` | NORMAL | `search_method`, `locomotion_mode`, `speed_scale`, `replan_required` |

---

## 4. ROS2 Topic Schema

| Topic | Direction | Payload 기준 | QoS |
|---|---|---|---|
| `/imu/data` | Sensor → SLAM | orientation, acceleration, angular_velocity | SensorDataQoS |
| `/gas/data` | Sensor → Business | gas_type, value, threshold | Reliable |
| `/lidar/points_raw` | LiDAR → SLAM | pointcloud frame | BestEffort |
| `/robot/pose` | SLAM → Bridge | x, y, z, roll, pitch, yaw | Reliable |
| `/navigation/path` | Navigation → Controller | waypoint list | Reliable |
| `/terrain/analysis` | SLAM → Navigation | slope, roughness, traversable | Reliable |
| `/perception/victim_decision` | Detector → Business | victim_detected, confidence, reason | Reliable |
| `/system/events` | Business → Bridge | BaseEvent | Reliable |
| `/control/command` | Bridge → Controller | command_type, speed, direction | Reliable |
| `/control/emergency_stop` | Any → Controller | trigger, reason | Reliable |

---

## 5. WebRTC DataChannel Schema

| Channel | Direction | Message Type | Priority |
|---|---|---|---|
| `data_control` | Control Center → Robot | `ControlCommand` | P0 |
| `data_event` | Robot → Control Center | `BaseEvent` | P0 |
| `data_status` | Robot → Control Center | `SystemStatus` | P1 |
| `data_sensor` | Robot → Control Center | `SensorSummary` | P1 |
| `data_pointcloud` | Robot → Control Center | compressed pointcloud chunk | P2 |
| `data_ack` | Bidirectional | ack/nack/retry | P1 |

---

## 6. Control Command Schema

```python
from dataclasses import dataclass
from enum import StrEnum


class ControlCommandType(StrEnum):
    MOVE = "MOVE"
    STOP = "STOP"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    SET_MODE = "SET_MODE"


@dataclass(frozen=True)
class ControlCommand:
    command_id: str
    mission_id: str
    robot_id: str
    command_type: ControlCommandType
    issued_by: str
    timestamp_ms: int
    payload: dict[str, object]
```

---

## 7. Search Mission Creation Schema

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
class SearchPoint:
    x: float
    y: float
    z: float
    frame_id: str


@dataclass(frozen=True)
class SearchArea:
    area_type: SearchAreaType
    coordinates: tuple[SearchPoint, ...]
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

필수 검증:

| 항목 | 기준 |
|---|---|
| `operator_id` | 인증된 관제자 ID |
| `search_area` | Area Type별 필수 좌표 조건 충족 |
| `search_method` | 정의된 `SearchMethod` enum만 허용 |
| `sop_profile_id` | 등록된 SOP Profile ID |
| `created_at_ms` | FakeClock 또는 시스템 Clock Adapter에서 생성 |
| `draft_snapshot_id` | 동일 입력에서 동일 snapshot 생성 |

---

## 8. 3D LiDAR Terrain Analysis Schema

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


class LocomotionMode(StrEnum):
    WHEEL = "WHEEL"
    OBSTACLE_CLIMB = "OBSTACLE_CLIMB"
    SLOW_SAFE = "SLOW_SAFE"
    EDGE_FOLLOW = "EDGE_FOLLOW"
    STOP_AND_REPLAN = "STOP_AND_REPLAN"
    STOP = "STOP"


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

분석 입력과 산출:

| 입력 | 처리 | 산출 |
|---|---|---|
| 3D LiDAR PointCloud | Ground segmentation, elevation grid map 생성 | `TerrainAnalysisResult` |
| Elevation Grid | slope, roughness, step height, obstacle density 계산 | traversability score |
| Terrain + SearchMethod | compatibility check, speed/clearance/replan 결정 | `SearchDriveProfile` |

---

## 9. Storage Schema

| 저장 대상 | Key | 필수 Metadata |
|---|---|---|
| Event | `mission_id/event_id` | priority, timestamp, robot_id |
| Thermal Video | `mission_id/robot_id/thermal/time_range` | codec, fps, resolution |
| RGB Video | `mission_id/robot_id/rgb/time_range` | codec, fps, resolution |
| PointCloud | `mission_id/robot_id/pointcloud/chunk_id` | compression, map_id |
| Mission Log | `mission_id/log/time_range` | log_level, module |
| Mission Draft | `mission_id/draft/draft_snapshot_id` | operator_id, sop_profile_id, validation_status |
| Search Mission Plan | `mission_id/plan/plan_snapshot_id` | approved_by, approved_at_ms, search_method |
| Terrain Analysis | `mission_id/robot_id/terrain/timestamp_ms` | terrain_class, traversability_score, map_id |

---

## 10. Client / Server Module Contract

| Module | Input Contract | Output Contract |
|---|---|---|
| Client-1 ROS2/WebRTC Bridge | ROS2 Topic, `ControlCommand` | WebRTC Track, DataChannel Message |
| Client-2 Detection | Encoded Media Packet, Detector Frame | `VictimDecision`, `BaseEvent` |
| Client-3 SLAM/Navigation/Control | PointCloud, IMU, `ControlCommand`, `SearchDriveProfile` | `Pose3D`, `TerrainAnalysisResult`, `NavigationPath`, `LocomotionDecision` |
| Server-1 Mission Core | `BaseEvent`, `SystemStatus`, `Recommendation`, `SearchMissionRequest` | `OperatorAlert`, Storage Write, SOP Context, `MissionDraft`, `SearchMissionPlan` |
| Server-2 UI | `OperatorAlert`, `SystemStatus`, Video Track | `SearchMissionRequest`, `ControlCommand` |
| Server-3 Storage / DB | Event, Media, Mission Log, Mission Draft/Plan | Save Result, Sync Status |
| Server-4 AI Agent / SOP | Mission Context, Hazard Context, `SearchMissionRequest` | `Recommendation`, `MissionSetupRecommendation` only |

금지 계약:

```text
Client-2 → WebRTC 직접 송신 금지
Client-3 → UI/SOP 직접 호출 금지
Server-2 → DB 직접 저장 금지
Server-4 → ControlCommand 생성 금지
Server-4 → Mission Start 직접 수행 금지
```

---

## 11. Interface 완료 기준

1. 모든 P0 Event의 Payload 필드가 정의된다.
2. ROS2 Topic과 WebRTC DataChannel 간 변환 규칙이 정의된다.
3. Python dataclass/Protocol은 `mypy` 기준 타입 오류가 없어야 한다.
4. Client 3개 모듈과 Server 4개 모듈의 Inbound/Outbound Contract가 정의된다.
5. Client 3개 모듈과 Server 4개 모듈의 Inbound/Outbound Contract는 Baseline으로 고정한다.
6. Schema 변경 시 `interface_baseline_freeze.md`의 Change Request 절차를 따른다.
7. Schema 변경 시 관련 테스트 케이스와 추적성 매트릭스를 업데이트한다.
8. 탐색 임무 생성 Schema 변경 시 `TC-MISSION-*`, `TC-IF-*`, `TC-MOD-*`를 함께 업데이트한다.
9. 지형 분석 및 주행 정책 Schema 변경 시 `TC-TERRAIN-*`, `TC-FUNC-DEC-*`, `TC-FUNC-BND-*`를 함께 업데이트한다.
