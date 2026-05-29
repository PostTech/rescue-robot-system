# operation_plan.md
# 재난 구조용 바퀴형 사족로봇 시스템
## Operation & Maintenance Plan

---

# 1. 목적

본 문서는 재난 구조용 바퀴형 사족로봇 시스템의 운영(Operation), 현장(Field), 유지보수(Maintenance) 전략을 통합 정의한다.

핵심 목적:

```text
1. 실제 재난 현장 운영 절차 정의
2. Mission Continuity 유지
3. Safety 중심 운영 체계 구축
4. Local Autonomous 기반 장애 대응
5. Predictive Maintenance 기반 예방 정비
6. 장기 운영 안정성 확보
```

---

# 2. 핵심 운영 원칙

## 2.1 Safety First

```text
Human Safety
    >
Robot Safety
    >
Mission
```

---

## 2.2 AI Recommendation Only

```text
AI Recommendation
    !=
Direct Robot Control
```

즉:

```text
AI는 권고만 수행
최종 결정은 Operator 수행
```

---

## 2.3 Local Autonomous 유지

```text
Remote Disconnect
    !=
Mission Stop
```

---

## 2.4 Failure Isolation

```text
Single Failure
    !=
Whole Mission Failure
```

---

## 2.5 Predictive Maintenance 우선

```text
Failure 대응
    <
Failure 예측 및 예방
```

---

# 3. 운영 조직 구조

| 역할 | 책임 |
|---|---|
| Mission Commander | 전체 임무 통제 |
| Robot Operator | 로봇 운용 |
| Safety Officer | 안전 관리 |
| Communication Operator | 통신 관리 |
| AI/SOP Operator | AI 권고 모니터링 |
| Technical Support | 장애 대응 |
| Maintenance Manager | 유지보수 총괄 |

---

# 4. Mission Operation Plan

## 4.1 Mission 시작 전 점검

점검 항목:

```text
Battery
Sensor 상태
Storage 상태
Network 상태
SLAM 상태
WebRTC 상태
Emergency Stop
```

---

## 점검 흐름

```text
Self Check
    ↓
Operator Confirm
    ↓
Mission Approval
```

---

## 출력 확인

```text
Thermal Video
RGB Video
Pose
Map
Event Stream
```

---

## 4.2 탐색 임무 생성 및 SOP 설정

관제자는 Mission 시작 전에 Operator UI에서 탐색 임무를 생성한다.

필수 입력:

```text
Mission Name
Search Area
Search Method
SOP Profile
Mission Priority
Operator ID
```

표준 흐름:

```text
SOP Profile 선택
    ↓
Search Mission 생성
    ↓
탐색 구역 지정
    ↓
탐색 방법 선택
    ↓
Mission Core 검증
    ↓
SOP 설정 추천 반영
    ↓
Mission Commander 승인
    ↓
Mission Plan 확정
```

탐색 구역 지정 방식:

| 방식 | 운영 기준 |
|---|---|
| Polygon | 관제 지도에서 폐곡선 영역 지정 |
| Waypoint Route | 경유점 순서 지정 |
| Grid | 격자 크기와 탐색 범위 지정 |
| Geofence | 진입 금지 또는 이탈 금지 영역 지정 |

탐색 방법:

| 방법 | 운영 기준 |
|---|---|
| `AREA_SWEEP` | 기본 구역 훑기 |
| `PARALLEL_SWEEP` | 넓고 완만한 사각형 구역의 평행 탐색 |
| `CREEPING_LINE` | 가능성이 한쪽으로 치우친 구역의 점진 탐색 |
| `EXPANDING_SQUARE` | 마지막 위치 또는 추정 위치 중심 확장 탐색 |
| `SECTOR_SEARCH` | 기준점 중심 방사형 집중 탐색 |
| `TRACKLINE_SEARCH` | 길, 통로, 예상 이동 경로 탐색 |
| `CONTOUR_SEARCH` | 산악/사면 등고선 기반 탐색 |
| `TRACK_SWEEP` | 트랙 주변 좌우 훑기 |
| `SINGLE_FILE` | 협소 통로 단일 경로 탐색 |
| `GRID_COVERAGE` | 격자 기반 정밀 탐색 |
| `FRONTIER_EXPLORATION` | 미탐색 영역 확장 |
| `WAYPOINT_ROUTE` | 지정 경유점 순차 이동 |
| `SPIRAL_SEARCH` | 감지 지점 주변 확장 |
| `PERIMETER_SEARCH` | 경계 우선 확인 |
| `MANUAL_ASSISTED` | 관제자 보조 반자동 탐색 |

SOP 설정 원칙:

```text
SOP Profile = 설정 추천 및 제한 조건
SOP Profile != Mission Start
SOP Profile != ControlCommand
```

SOP Agent는 `MissionSetupRecommendation`만 생성하고, Mission Core가 검증 후 Mission Commander 승인 절차로 넘긴다.

---

## 4.3 3D LiDAR 지형 분석 기반 주행

3D LiDAR 지형 분석은 탐색 임무 실행 중 Client-3에서 수행한다.

```text
3D LiDAR PointCloud
    ↓
Terrain Analysis
    ↓
TerrainClass / Traversability
    ↓
SearchMethod Compatibility
    ↓
SearchDriveProfile
    ↓
Navigation / Locomotion
```

운영 기준:

| 지형 | 우선 탐색 방법 | 주행 방식 |
|---|---|---|
| 평탄 개활지 | `PARALLEL_SWEEP`, `GRID_COVERAGE` | 정상 속도, 직선 주행 |
| 완만한 경사 | `CONTOUR_SEARCH`, `PARALLEL_SWEEP` | 등고선 우선, 속도 제한 |
| 급경사 | `CONTOUR_SEARCH`, `WAYPOINT_ROUTE` | 저속, 경사 한계 초과 시 우회 |
| 잔해/험지 | `FRONTIER_EXPLORATION`, `MANUAL_ASSISTED` | 장애물 등반 또는 짧은 재계획 |
| 협소 통로 | `SINGLE_FILE`, `TRACKLINE_SEARCH` | 중앙선 추종, 저속 |
| 절벽/낙차 | `PERIMETER_SEARCH` | 진입 금지, 정지/우회 |

탐색 방법만으로 주행을 확정하지 않고, 지형 분석 결과와 결합해 Mission Core와 Operator UI에 상태를 보고한다.

---

# 5. Autonomous Operation Plan

## 5.1 기본 구조

```text
Navigation
+
Victim Detection
+
Terrain Analysis
```

---

## 5.2 Operator 역할

```text
Monitoring
Approval
Emergency 대응
Mission Decision
```

---

## 5.3 Detection 절차

```text
Thermal Detection
RGB Detection
Audio Detection
    ↓
Fusion Logic
    ↓
Victim Candidate
    ↓
Operator Review
```

---

## 우선순위

```text
Thermal
    >
RGB
    >
Audio
```

---

# 6. Communication Operation Plan

## 6.1 정상 상태

상태:

```text
CONNECTED
```

---

## 기능

```text
Real-Time Monitoring
Remote Control
Event Streaming
```

---

## 6.2 DEGRADED 상태

상태:

```text
DEGRADED
```

---

## 동작

```text
Thermal Priority 유지
RGB Bitrate 감소 가능
PointCloud Drop 가능
```

---

## 6.3 DISCONNECTED 상태

상태:

```text
DISCONNECTED
```

---

## 흐름

```text
Reconnect Attempt
    ↓
LOCAL_AUTONOMOUS_MODE
```

---

## 유지 기능

```text
Local Navigation
Victim Detection
Critical Event Save
Obstacle Avoidance
```

---

# 7. Emergency Operation Plan

## 7.1 Emergency Stop

Trigger:

```text
Operator Stop
Collision Risk
Gas Hazard
Hardware Failure
```

---

## 흐름

```text
Emergency Stop
    ↓
All Motion Stop
    ↓
Safety Confirm
```

---

## 우선순위

```text
Highest Priority
```

---

## 7.2 Safe Mode

Trigger:

```text
Localization Failure
Motor Failure
Communication Failure
```

---

## 흐름

```text
Safe Navigation
    ↓
Operator Alert
    ↓
Recovery 시도
```

---

# 8. Gas Hazard Operation Plan

## WARNING Level

```text
Operator Alert
Mission Continue 가능
```

---

## DANGER Level

```text
Robot Stop
Retreat 가능
Mission Re-evaluation
```

---

# 9. Navigation Operation Plan

## Terrain Following

검증 환경:

```text
Slope
Rock
Mud
Uneven Terrain
```

---

## 감시 항목

```text
Slip
Tilt
Obstacle
Terrain Risk
```

---

## Obstacle Climb

```text
Terrain Analysis
    ↓
Locomotion Mode 변경
    ↓
Obstacle Traverse
```

---

## Localization Failure

```text
Localization Recovery
    ↓
Replan
    ↓
Safe Mode 가능
```

---

# 10. Field Operation Plan

## 10.1 산악 환경

환경:

```text
Slope
Rock
Mud
Tree Root
Uneven Terrain
```

---

## 검증 항목

```text
Terrain Following
Obstacle Avoidance
Wheel Stability
```

---

## 10.2 터널 환경

환경:

```text
Darkness
GPS Loss
Communication Loss
Gas Hazard
```

---

## 검증 항목

```text
Thermal Detection
SLAM
Local Autonomous
```

---

## 10.3 붕괴 구조물 환경

환경:

```text
Debris
Collapsed Area
Narrow Passage
```

---

## 검증 항목

```text
Obstacle Climb
Safe Navigation
Terrain Analysis
```

---

## 10.4 화재/연기 환경

환경:

```text
Smoke
Heat Source
Low Visibility
```

---

## 검증 항목

```text
Thermal Detection
False Positive
Navigation
```

---

# 11. Storage Operation Plan

## 11.1 Normal Storage

저장 대상:

```text
Event
Mission
Video
PointCloud
```

---

## 11.2 Local Save

조건:

```text
Network Failure
```

---

## 흐름

```text
Local Save
    ↓
Sync Queue
    ↓
Recovery 후 Sync
```

---

## 11.3 Storage Full

```text
Low Priority 삭제
Critical Event 유지
Operator Alert
```

---

# 12. AI / SOP Operation Plan

## AI 역할

```text
Situation Summary
Hazard Analysis
Mission Recommendation
```

---

## 금지 사항

```text
Direct Motion Control 금지
```

---

## 승인 구조

```text
AI Recommendation
    ↓
Operator Review
    ↓
Mission Decision
```

---

# 13. Multi Robot Operation Plan

## 구조

```text
Robot01
Robot02
Robot03
```

---

## 공유 데이터

```text
Map
Victim Detection
Hazard Event
Mission Status
```

---

## 운영 구조

```text
Area 분담
Shared Map
Shared Event
```

---

# 14. Failure Recovery Plan

## 14.1 AI Failure

```text
Video 유지
Detector Restart
Fallback 가능
```

---

## 14.2 SLAM Failure

```text
Localization Recovery
Safe Navigation
Operator Alert
```

---

## 14.3 WebRTC Failure

```text
Reconnect 시도
Local Autonomous 유지
```

---

## 14.4 Storage Failure

```text
Local Save 유지
Retry
Sync Queue 유지
```

---

# 15. Maintenance Strategy

## 15.1 Hardware Maintenance

대상:

```text
Thermal Camera
RGB Camera
LiDAR
IMU
Gas Sensor
Motor
Battery
```

---

## 점검 항목

```text
Calibration
Temperature
Noise
Torque
Vibration
Packet Loss
```

---

## 주기

```text
Pre-Mission
Weekly
Monthly
```

---

# 16. Software Maintenance

## 대상

```text
ROS2
YOLO
Fusion Logic
TensorRT
SLAM
Navigation
WebRTC
```

---

## 점검 항목

```text
Latency
Memory Leak
Inference Time
Localization Drift
Reconnect
GPU Usage
```

---

## Update 절차

```text
Offline Validation
    ↓
Simulation Validation
    ↓
Field Validation
    ↓
Deployment
```

---

# 17. Predictive Maintenance

## 대상

```text
Motor
Battery
Storage
GPU
Temperature
```

---

## 분석 항목

```text
Trend
Repeated Error
Abnormal Pattern
```

---

## 결과

```text
Maintenance Recommendation
Replacement Recommendation
```

---

# 18. Monitoring Plan

## 수집 항목

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

---

## Alert Level

### INFO

```text
정상 범위 경고
```

---

### WARNING

```text
성능 저하 가능성
```

---

### CRITICAL

```text
Mission 영향 가능
```

---

## Alert 흐름

```text
Metrics
    ↓
Threshold Check
    ↓
Alert
    ↓
Operator Notification
```

---

# 19. OTA / Deployment Plan

## 대상

```text
ROS2 Node
AI Model
SLAM
Navigation
Container
```

---

## 절차

```text
Offline Validation
    ↓
Simulation Test
    ↓
Controlled Deployment
    ↓
Field Deployment
```

---

## Rollback

조건:

```text
Critical Failure
Performance Degradation
```

---

## 조치

```text
Previous Stable Version 복원
```

---

# 20. Container Operation Plan

## 구조

```text
detector_container
slam_container
navigation_container
webrtc_container
storage_container
```

---

## 장점

```text
Isolation
Independent Restart
Independent Update
```

---

## Recovery

```text
Container Restart
Health Check
Fallback
```

---

# 21. Long Duration Mission Plan

## 감시 항목

```text
Battery
Temperature
Storage
GPU
Network
```

---

## 조치

```text
Cooling
Mission Pause
Low Priority Cleanup
```

---

# 22. Security Operation Plan

## 점검 항목

```text
Unauthorized Access
Credential Expiration
Container Vulnerability
```

---

## 조치

```text
Credential Rotation
Security Patch
Access Audit
```

---

# 23. Logging Plan

## 저장 대상

```text
Mission Log
Event Log
Error Log
Recovery Log
Performance Log
```

---

## 목적

```text
Failure Analysis
Post Mission Analysis
Predictive Maintenance
```

---

# 24. 종료 절차

## Mission 종료

```text
Mission Complete
    ↓
Robot Stop
    ↓
Data Sync
    ↓
Mission Archive
```

---

## Shutdown

```text
Mission Stop
    ↓
Motor Stop
    ↓
Data Save
    ↓
ROS2 종료
    ↓
Sensor 종료
```

---

# 25. 운영 KPI

| KPI | 목표 |
|---|---|
| Mission Success Rate | ≥ 95% |
| Detection Accuracy | ≥ 90% |
| Reconnect Time | < 10 sec |
| Obstacle Traversal Success | ≥ 90% |
| Mission Availability | ≥ 99% |
| Critical Event Loss | 0 |

---

# 26. 최종 운영 흐름

```text
Mission Start
    ↓
Autonomous Operation
    ↓
Detection/Event
    ↓
Operator Decision
    ↓
Mission Continue
    ↓
Mission Complete
```

---

# 27. 완료 기준

```text
1. Safety 검증 완료
2. Local Autonomous 유지 가능
3. Critical Event Loss = 0
4. Reconnect 및 Recovery 가능
5. Long Duration Mission 가능
6. Predictive Maintenance 적용 완료
7. AI Recommendation 구조 유지
8. Emergency Stop 최우선 동작
9. Multi Robot 운영 가능
10. 실제 재난 환경 운영 가능
```

---

# 28. 최종 핵심

```text
operation_plan.md는
실제 재난 현장에서
Mission Continuity를 유지하기 위한
운영, 장애대응, 유지보수,
Predictive Maintenance 전략을
통합한 운영 계획 문서이다.
```
