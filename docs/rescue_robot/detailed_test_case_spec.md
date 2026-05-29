# 상세 테스트 케이스 명세서

## 1. 목적

본 문서는 주요 P0/P1 요구사항의 입력, 절차, 기대 결과, Pass/Fail 기준을 정의한다.

계층별 TDD 대상, Mock/Fake, Harness 구성은 `layer_tdd_harness_matrix.md`를 기준으로 한다.

현재 기본 테스트 환경은 Windows `dev-windows-local`이며, 기본 테스트는 ROS Runtime까지 진행하지 않는다.

---

## 2. Code Quality Gate

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-LINT-001 | Ruff Lint 검증 | `ruff check .` 실행 | Lint 오류 없음 | Exit code 0 |
| TC-LINT-002 | Formatting 검증 | `ruff format --check .` 실행 | Format 변경 필요 없음 | Exit code 0 |
| TC-LINT-003 | Type Check 검증 | `mypy src tests` 실행 | 타입 오류 없음 | Exit code 0 |
| TC-LINT-004 | Unit Test 실행 | `pytest tests/unit tests/contract tests/layer tests/dependency tests/module_boundary tests/mission_creation tests/terrain` 실행 | 테스트 통과 | ROS Runtime 없이 P0 테스트 통과 |

---

## 3. Layer Boundary Test

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-LAYER-001 | Domain ROS 독립성 | `domain/` import scan | `rclpy`, ROS Message import 없음 | 위반 0건 |
| TC-LAYER-002 | Application ROS 독립성 | Application Service 입력 타입 확인 | ROS Message 직접 입력 없음 | DTO/Protocol만 사용 |
| TC-LAYER-003 | ROS Adapter Contract 변환 | Fake ROS Envelope 입력 | Domain DTO 변환 | ROS Runtime 없이 Mapper 테스트 통과 |
| TC-LAYER-004 | ROS Runtime 없는 Unit Test | ROS 미실행 상태에서 `pytest tests/unit` | Business Logic 통과 | Exit code 0 |
| TC-LAYER-005 | Mock Topic 장애 Event 변환 | Mock timeout 주입 | System Event 생성 | Domain exception 직접 전파 없음 |

---

## 4. Dependency Direction Test

고정 순서:

```text
Types -> Config -> Service -> UI
```

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-DEP-001 | Types 독립성 | `types/` import scan | Config/Service/UI import 없음 | 위반 0건 |
| TC-DEP-002 | Config 독립성 | `config/` import scan | Service/UI import 없음 | 위반 0건 |
| TC-DEP-003 | Service 독립성 | `service/` import scan | UI import 없음, `import ... from "../ui/..."` 없음 | 발견 즉시 수정 요청 |
| TC-DEP-004 | UI Runtime 직접 접근 차단 | `ui/` import scan | DB Driver/ROS Runtime/Robot SDK 직접 import 없음 | 위반 0건 |
| TC-DEP-005 | 순환 의존성 차단 | dependency graph 분석 | Types/Config/Service/UI cycle 없음 | cycle 0건 |
| TC-DEP-006 | 신규 기능 Types First | 변경 파일 순서와 traceability 확인 | 신규 Types 정의가 Config/Service/UI보다 선행 | Types 없이 Service/UI 구현 시 실패 |

---

## 5. Deterministic Validation Test

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-DETVAL-001 | Fixed Clock 검증 | FakeClock으로 Event 생성 | timestamp 고정 | 실행 시각과 무관 |
| TC-DETVAL-002 | Fixed Seed 검증 | 동일 seed로 Fusion 실행 | 동일 confidence/decision | 결과 일치 |
| TC-DETVAL-003 | Event Ordering 검증 | 동일 Event 목록 입력 | 동일 처리 순서 | priority/timestamp 기준 일치 |
| TC-DETVAL-004 | State Snapshot 검증 | 동일 시나리오 실행 | 동일 Mission State | snapshot 일치 |
| TC-DETVAL-005 | Adapter Mapper 검증 | 동일 Fake ROS Envelope 입력 | 동일 Domain DTO | DTO 일치 |
| TC-DETVAL-006 | Storage Key 검증 | 동일 Event 저장 | 동일 storage key | key 일치 |
| TC-DETVAL-007 | Retry/Sync 검증 | 동일 장애 시나리오 실행 | 동일 retry/sync 순서 | 순서 일치 |
| TC-DETVAL-008 | Mission Draft Snapshot 검증 | 동일 SearchMissionRequest와 SOP Profile 입력 | 동일 draft snapshot | `draft_snapshot_id` 일치 |
| TC-DETVAL-009 | SearchDriveProfile 검증 | 동일 TerrainAnalysisResult와 SearchMethod 입력 | 동일 drive profile | mode/speed/replan 일치 |

---

## 6. Safety Test

| Test ID | 입력 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-SAFE-001 | `EMERGENCY_STOP` Event | 모든 상태에서 이벤트 주입 | All Motion Stop | 제어 명령보다 우선 처리 |
| TC-SAFE-002 | Gas `DANGER` | Gas Sensor 값 Threshold 초과 | Stop 또는 Retreat 권고 | Operator Alert 생성 |
| TC-SAFE-003 | Localization Failure | SLAM pose update 중단 | Safe Mode 진입 | Mission 상태 DEGRADED |

---

## 7. Detection Test

| Test ID | 입력 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-DET-001 | Thermal temp 36.5°C | Fake Thermal Frame 입력 | VictimCandidate 생성 | confidence 기준 만족 |
| TC-DET-002 | RGB confidence 0.8 | Fake RGB Detection 입력 | RGB 후보 생성 | Thermal보다 낮은 우선순위 |
| TC-DET-003 | Audio help keyword | Fake Audio Event 입력 | SuspiciousEvent 생성 | Operator UI Event 표시 |
| TC-DET-004 | Thermal + RGB | Fusion 실행 | High Confidence 후보 | Fusion score 상승 |

---

## 8. Function Unit Test

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-FUNC-DEC-001 | Thermal 판단 함수 | fixed thermal input | victim flag 결정 | 동일 입력 동일 결과 |
| TC-FUNC-DEC-004 | Fusion 함수 | fixed evidence 입력 | fusion score 결정 | 동일 score |
| TC-FUNC-DEC-005 | Gas Hazard 함수 | fixed gas value 입력 | SAFE/WARNING/DANGER | threshold 기준 일치 |
| TC-FUNC-DEC-007 | Emergency 우선순위 함수 | state + emergency trigger | stop decision | 모든 state에서 stop |
| TC-FUNC-DEC-008 | Local Autonomous 함수 | disconnected status 입력 | local autonomous true | 조건 일치 |
| TC-FUNC-DEC-010 | 탐색 방법 판단 함수 | area_type + sop_profile 입력 | SearchMethod 결정 | 동일 입력 동일 방법 |
| TC-FUNC-DEC-012 | 지형 기반 주행 정책 함수 | terrain_class + search_method | SearchDriveProfile 결정 | 동일 입력 동일 profile |
| TC-FUNC-BND-001 | Event 정렬 함수 | fixed event list | deterministic order | 순서 일치 |
| TC-FUNC-BND-003 | Control Authority 함수 | role + command | allow/deny | 권한 기준 일치 |
| TC-FUNC-BND-004 | Storage Key 함수 | fixed ids | deterministic key | key 일치 |
| TC-FUNC-BND-006 | Sync Queue 순서 함수 | fixed queue | priority + FIFO | 순서 일치 |
| TC-FUNC-BND-008 | Fake ROS Envelope Mapper | fixed fake envelope | Domain DTO | DTO 일치 |
| TC-FUNC-BND-010 | SearchArea 검증 함수 | fixed area input | valid/invalid | Area Type별 조건 일치 |
| TC-FUNC-BND-011 | Mission Approval Guard | draft state + role | approve/deny | Commander 승인 전 활성화 차단 |
| TC-FUNC-BND-014 | TerrainAnalysisResult 검증 함수 | fixed terrain payload | valid/invalid | score/range 조건 일치 |

---

## 9. Mission Creation Test

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-MISSION-001 | 관제자 탐색 임무 생성 | `SearchMissionRequest` 입력 | `MissionDraft` 생성 | Mission Core가 요청 접수 |
| TC-MISSION-002 | 탐색 구역 검증 | Polygon/Waypoint/Grid/Geofence fixture 입력 | valid/invalid 판정 | 잘못된 구역은 Draft 저장 차단 |
| TC-MISSION-003 | 탐색 방법 선택 검증 | Area Type + SearchMethod 조합 입력 | 허용/차단 판정 | 정의된 enum과 조합 규칙 준수 |
| TC-MISSION-004 | SOP Profile 적용 | fixed SOP Profile 입력 | `MissionSetupRecommendation` 생성 | 동일 입력 동일 recommendation |
| TC-MISSION-005 | 승인 전 활성화 차단 | Draft 상태에서 start 시도 | Mission Plan 비활성 | Commander 승인 전 시작 불가 |
| TC-MISSION-006 | UI 저장소 직접 접근 금지 | Server-2 dependency scan | Repository/DB 직접 import 없음 | `IMissionSetupSender`만 사용 |
| TC-MISSION-007 | SOP 직접 시작/제어 금지 | Server-4 output scan | ControlCommand/Mission Start 없음 | Recommendation only |
| TC-MISSION-008 | Mission Draft 결정성 | FakeClock + deterministic id 입력 | 동일 snapshot | `draft_snapshot_id` 일치 |

---

## 10. Terrain Driven Navigation Test

| Test ID | 목적 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-TERRAIN-001 | 3D LiDAR 지형 분석 존재 검증 | `ITerrainAnalyzer` Contract 확인 | `TerrainAnalysisResult` 반환 | ROS Runtime 없이 Mock PointCloud 처리 |
| TC-TERRAIN-002 | slope/roughness/step 산출 | fixed elevation grid 입력 | feature 값 산출 | fixture expected와 일치 |
| TC-TERRAIN-003 | TerrainClass 분류 | fixed feature 입력 | `FLAT_OPEN`, `STEEP_SLOPE` 등 분류 | threshold 기준 일치 |
| TC-TERRAIN-004 | 탐색 방법 호환성 검증 | TerrainClass + SearchMethod 입력 | 허용/차단 | 위험 조합 차단 |
| TC-TERRAIN-005 | SearchDriveProfile 결정 | TerrainClass + SearchMethod 입력 | speed/mode/replan 결정 | 동일 입력 동일 profile |
| TC-TERRAIN-006 | CLIFF/DROP 안전 차단 | drop fixture 입력 | `STOP_AND_REPLAN` | 경로 생성 차단 |
| TC-TERRAIN-007 | FLAT_OPEN 평행 탐색 | flat fixture + `PARALLEL_SWEEP` | 정상 속도 sweep profile | `replan_required=false` |
| TC-TERRAIN-008 | ROUGH_RUBBLE 탐색 | rubble fixture + `FRONTIER_EXPLORATION` | 저속 obstacle profile | `OBSTACLE_CLIMB` 또는 replan |

---

## 11. Communication / Failover Test

| Test ID | 입력 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-COMM-001 | ICE Disconnect | WebRTC 연결 중단 | DISCONNECTED 전이 | Reconnect Attempt 시작 |
| TC-COMM-002 | WebRTC=false, 5G=false | 단절 지속 | Local Autonomous Mode | Local SLAM/Save 유지 |
| TC-COMM-003 | Reconnect 성공 | 통신 복구 이벤트 입력 | Local Data Sync | Mission Resume |
| TC-COMM-004 | Bandwidth 저하 | Packet loss 증가 | PointCloud Downsample | Thermal 유지 |

---

## 12. Interface / Adapter Test

| Test ID | 대상 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-IF-001 | `IDetector` | MockDetector 교체 | Business Logic 변경 없음 | 동일 테스트 통과 |
| TC-IF-002 | `IWebRTCTrackSender` | Fake Packet 송신 | Track Sender 호출 | ROS2 Topic 미사용 |
| TC-IF-003 | `IEventRepository` | DB Failure 주입 | Local Save 유지 | Critical Event 보존 |
| TC-IF-004 | `ISopAgent` | Hazard Context 입력 | Recommendation 생성 | ControlCommand 미생성 |
| TC-IF-050 | `IMissionCreationService` | `SearchMissionRequest` 입력 | `MissionDraft` 반환 | UI/DB 직접 의존 없음 |
| TC-IF-051 | `IMissionRepository` | Draft/Plan 저장 fixture | 저장/조회 성공 | Mission 판단 없음 |
| TC-IF-052 | `ISopMissionConfigurator` | SOP Profile 적용 | `MissionSetupRecommendation` 반환 | Mission Start 없음 |
| TC-IF-060 | `ITerrainAnalyzer` | Mock PointCloud 입력 | `TerrainAnalysisResult` 반환 | ROS Message 직접 노출 없음 |
| TC-IF-061 | `ISearchDrivePolicy` | Terrain + SearchMethod 입력 | `SearchDriveProfile` 반환 | deterministic profile |

---

## 13. Module Boundary Test

| Test ID | 대상 | 절차 | 기대 결과 | Pass 기준 |
|---|---|---|---|---|
| TC-MOD-001 | Client-1 | Mock ROS2 Topic과 Mock DataChannel 연결 | Bridge만 수행 | Detector/SLAM 직접 호출 없음 |
| TC-MOD-002 | Client-2 | Detection 결과 생성 | ROS2/Event Contract로 발행 | WebRTC Track 직접 송신 없음 |
| TC-MOD-003 | Client-3 | Navigation Path와 Control 실행 | Pose/Path/Event 발행 | UI/SOP 직접 호출 없음 |
| TC-MOD-004 | Server-1 | Event 수신 후 Mission 처리 | UI/Storage/SOP Interface 호출 | DB Driver 직접 접근 없음 |
| TC-MOD-005 | Server-2 | Operator 명령 생성 | `ControlCommand` 송신 | DB 직접 저장 없음 |
| TC-MOD-006 | Server-3 | Event/Media 저장 요청 처리 | Save Result/Sync Status 반환 | Mission 판단 없음 |
| TC-MOD-007 | Server-4 | SOP Context 입력 | Recommendation만 생성 | ControlCommand 미생성 |
| TC-MOD-008 | Server-2 Mission Setup | 탐색 임무 생성 입력 | `SearchMissionRequest` 송신 | Mission Repository 직접 접근 없음 |
| TC-MOD-009 | Server-1 Mission Creation | 요청 접수 후 Draft 생성 | Repository/SOP Interface 호출 | DB Driver 직접 접근 없음 |
| TC-MOD-010 | Server-4 SOP Mission Config | SOP Profile 입력 | 설정 추천만 반환 | Mission Start/ControlCommand 없음 |
| TC-MOD-011 | Client-3 Terrain Driven Navigation | Mock PointCloud + SearchMethod 입력 | TerrainAnalysisResult와 SearchDriveProfile 기반 Path 생성 | UI/SOP 직접 호출 없음 |

---

## 14. Acceptance Test

| Test ID | 영역 | 기준 |
|---|---|---|
| TC-ACC-001 | Detection | Victim Detection Accuracy ≥ 90% |
| TC-ACC-002 | Streaming | Thermal Stream ≥ 15 FPS |
| TC-ACC-003 | SLAM | Localization Update ≥ 10Hz |
| TC-ACC-004 | Recovery | Reconnect < 10 sec |
| TC-ACC-005 | Safety | Emergency Stop 즉시 정지 |
| TC-ACC-006 | Storage | Critical Event Loss = 0 |
| TC-ACC-007 | Mission | Mission Success Rate ≥ 95% |
| TC-ACC-008 | Mission Creation | 구역/방법/SOP 기반 탐색 임무 생성 및 승인 가능 |
| TC-ACC-009 | Terrain Driven Navigation | 3D LiDAR 지형 분석 기반 탐색 주행 가능 |

---

## 15. 완료 기준

1. `TC-LINT-*`는 모든 Sprint에서 통과해야 한다.
2. `TC-LAYER-*`는 ROS Runtime 없이 통과해야 한다.
3. `TC-DEP-*`는 `Types -> Config -> Service -> UI` 의존성 방향을 강제한다.
4. `TC-DETVAL-*`는 Windows 기본 테스트 Gate에 포함한다.
5. `TC-FUNC-DEC-*`, `TC-FUNC-BND-*`는 Windows 기본 테스트 Gate에 포함한다.
6. `TC-MISSION-*`는 Windows 기본 테스트 Gate에 포함한다.
7. `TC-TERRAIN-*`는 Windows 기본 테스트 Gate에 포함한다.
8. Windows 기본 테스트에서는 `rclpy`, ROS Node, 실제 ROS Topic을 실행하지 않는다.
9. `TC-SAFE-*`, `TC-COMM-*`는 Field Test 전 반드시 통과해야 한다.
10. `TC-MOD-*`는 Client/Server 분리 기준으로 모두 통과해야 한다.
11. Acceptance Test 실패 시 운영 배포하지 않는다.
12. Hotfix 예외는 별도 승인 기록과 재검증 일정을 남긴다.
