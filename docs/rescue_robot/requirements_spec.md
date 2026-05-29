# 재난 구조용 바퀴형 사족로봇 시스템 요구사항 명세서

## 1. 목적

본 문서는 시스템 구현, 테스트, 검수의 기준이 되는 기능 요구사항과 비기능 요구사항을 정의한다.

---

## 2. 범위

### 2.1 포함 범위

- 재난 환경 로봇 자율주행
- Thermal/RGB/Audio 기반 요구조자 탐지
- LiDAR/IMU 기반 SLAM 및 지형 분석
- 3D LiDAR 지형 분석과 탐색 방법 기반 주행 정책
- WebRTC 원격 관제 및 제어
- 통신 단절 시 Local Autonomous Mode
- Event/Media/PointCloud 저장 및 복구 후 Sync
- AI/SOP 기반 권고 생성
- 관제자 기반 탐색 임무 생성, 탐색 구역 지정, 탐색 방법 선택
- SOP Profile 기반 임무 설정 추천 및 검증
- Simulation, Field Test, Acceptance 검증
- Python 기반 구현 품질 관리 및 Lint

### 2.2 제외 범위

- AI/SOP Agent의 직접 로봇 제어
- 영상/오디오의 ROS2 Topic 전송
- Operator 승인 없는 원격 제어
- Acceptance 미통과 상태의 현장 투입
- 보안 인증 없는 원격 접속

---

## 3. 기능 요구사항

| ID | 요구사항 | 우선순위 | Acceptance 기준 |
|---|---|---|---|
| FR-001 | Thermal 영상에서 요구조자 후보를 탐지한다. | P0 | Accuracy ≥ 90%, latency < 200ms |
| FR-002 | RGB 탐지는 Thermal 판단을 보조한다. | P0 | RGB confidence ≥ 0.7 시 후보 생성 |
| FR-003 | Audio help 탐지는 보조 이벤트를 생성한다. | P1 | SuspiciousEvent 생성 |
| FR-004 | Thermal/RGB/Audio 결과를 Fusion한다. | P0 | Thermal > RGB > Audio 우선순위 유지 |
| FR-005 | Gas Hazard를 감지하고 Safe Mode 또는 Stop을 권고한다. | P0 | DANGER 시 Robot Stop 또는 Retreat |
| FR-006 | LiDAR/IMU 기반 Pose와 Map을 생성한다. | P0 | Localization update ≥ 10Hz |
| FR-007 | 지형 분석 결과에 따라 Locomotion Mode를 선택한다. | P0 | Slope > 20° 시 OBSTACLE_CLIMB |
| FR-008 | Emergency Stop은 모든 상태보다 우선한다. | P0 | 즉시 All Motion Stop |
| FR-009 | WebRTC로 Thermal/RGB/Audio Track을 송신한다. | P0 | Thermal stream ≥ 15 FPS |
| FR-010 | Control/Event/Thermal 우선 네트워크 정책을 적용한다. | P0 | Control 지연이 PointCloud보다 낮음 |
| FR-011 | 통신 단절 시 Local Autonomous Mode로 전환한다. | P0 | Mission 중단 없이 Local Save 유지 |
| FR-012 | Critical Event를 Local Storage에 우선 저장한다. | P0 | Critical Event Loss = 0 |
| FR-013 | Reconnect 후 Local Data를 Remote Storage와 Sync한다. | P1 | FIFO + Priority 기반 Sync 완료 |
| FR-014 | AI/SOP Agent는 권고만 생성한다. | P0 | Direct Motion Command 없음 |
| FR-015 | Multi Robot Namespace를 지원한다. | P2 | `/robot_001/*`, `/robot_002/*` 분리 |
| FR-016 | 관제자는 Operator UI에서 탐색 임무를 생성할 수 있다. | P0 | `SearchMissionRequest` 생성 및 Mission Core 접수 |
| FR-017 | 관제자는 탐색 구역을 Polygon, Waypoint, Grid, Geofence 기준으로 지정할 수 있다. | P0 | SearchArea validation 통과 후 Draft 저장 |
| FR-018 | 관제자는 탐색 방법을 선택할 수 있다. | P0 | `SearchMethod` 선택값이 Mission State와 Area Type 기준으로 검증됨 |
| FR-019 | SOP Profile을 통해 임무 설정 기본값과 제한 조건을 적용한다. | P0 | 동일 SOP 입력에서 동일 `MissionSetupRecommendation` 생성 |
| FR-020 | Mission Commander 승인 전에는 탐색 Mission Plan을 활성화하지 않는다. | P0 | 승인 전 Mission Start/ControlCommand 생성 없음 |
| FR-021 | 3D LiDAR PointCloud 기반 지형 분석을 수행한다. | P0 | slope, roughness, step height, obstacle density, traversability 산출 |
| FR-022 | 지형 분석 결과와 탐색 방법에 따라 주행 정책을 결정한다. | P0 | TerrainClass + SearchMethod → SearchDriveProfile 결정 |

---

## 4. 비기능 요구사항

| ID | 요구사항 | 목표 |
|---|---|---|
| NFR-001 | Safety | Emergency Stop 최우선 |
| NFR-002 | Availability | Mission Availability ≥ 99% |
| NFR-003 | Recovery | Reconnect < 10 sec |
| NFR-004 | Performance | Thermal stream ≥ 15 FPS |
| NFR-005 | Reliability | Critical Event Loss = 0 |
| NFR-006 | Maintainability | Interface + Adapter 기반 교체 가능 |
| NFR-007 | Testability | Mock/Test Harness 기반 검증 가능 |
| NFR-008 | Observability | CPU/GPU/Memory/Network/FPS/Latency 수집 |
| NFR-009 | Security | 인증, 권한, 암호화, 감사 로그 적용 |
| NFR-010 | Code Quality | Python Lint, Formatting, Type Check 통과 |
| NFR-011 | ROS Layering | Domain/Application 계층은 ROS Message와 `rclpy`에 직접 의존하지 않음 |
| NFR-012 | Layer Testability | 각 계층은 TDD 대상, Mock/Fake, Test Harness, 완료 기준을 가진다 |
| NFR-013 | Environment Profile | Windows 기본 개발 환경과 Linux/ROS 실행 환경을 명시 프로파일로 전환한다 |
| NFR-014 | Windows Test Scope | Windows 기본 테스트는 ROS Runtime, rclpy, 실제 ROS Topic까지 진행하지 않는다 |
| NFR-015 | Deterministic Validation | Windows 기본 테스트는 동일 입력에서 동일 Event/State/Output을 보장한다 |
| NFR-016 | Interface Baseline Freeze | Client 3개와 Server 4개의 Inbound/Outbound Contract는 승인 없이 변경하지 않는다 |
| NFR-017 | Function Unit Test | 결정 로직과 경계 로직은 함수 단위 테스트를 가진다 |
| NFR-018 | Mission Setup Determinism | 동일 임무 생성 입력, SOP Profile, FakeClock에서 동일 Mission Draft Snapshot을 생성한다 |
| NFR-019 | Terrain Driven Navigation | 탐색 주행은 SearchMethod 단독이 아니라 TerrainAnalysisResult와 결합해 결정한다 |
| NFR-020 | Dependency Direction | 코드 의존성은 반드시 `Types -> Config -> Service -> UI` 순서를 지킨다 |

---

## 5. 완료 기준

1. 모든 P0 요구사항이 구현되고 테스트를 통과한다.
2. P1 요구사항은 운영 배포 전까지 완료한다.
3. P2 요구사항은 Multi Robot 실증 단계 이전까지 완료한다.
4. 요구사항은 설계, 구현, 테스트 케이스와 추적 가능해야 한다.
5. Python Lint/Type Check 실패 항목은 Release Candidate에 포함하지 않는다.
