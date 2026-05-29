# Deterministic Validation 계획

## 1. 목적

본 문서는 Windows 기본 테스트 환경에서 테스트 결과가 실행 시점, OS 상태, 네트워크, ROS Runtime, 실제 센서, 임의값에 흔들리지 않도록 결정론적 검증 기준을 정의한다.

---

## 2. 핵심 원칙

```text
Same Input
    =
Same Event
    =
Same State Transition
    =
Same Output
```

테스트는 재실행해도 동일한 결과를 내야 한다.

---

## 3. 금지 사항

Windows 기본 테스트에서 다음을 직접 사용하지 않는다.

```text
실제 시간
실제 난수
실제 네트워크
ROS Runtime
rclpy
실제 ROS Topic
실제 센서/HW
외부 DB
외부 AI API
```

---

## 4. Deterministic Test Fixture

| 대상 | 결정론적 대체 |
|---|---|
| Time | `FakeClock` |
| Random | Fixed seed 또는 `FakeRandom` |
| Sensor Input | Fixed fixture frame |
| Event ID | Deterministic ID Generator |
| Network | Mock DataChannel / Fake Packet |
| ROS Topic | Fake ROS Envelope |
| Storage | InMemoryRepository |
| AI Result | MockDetector fixed output |
| SOP Agent | MockSopAgent fixed recommendation |
| Mission Setup | Fixed SearchArea, fixed SearchMethod, fixed SOP Profile |
| Terrain Analysis | Fixed PointCloud, fixed ElevationGrid, fixed TerrainAnalysisResult |

---

## 5. 검증 대상

| 계층 | Deterministic Validation 기준 |
|---|---|
| Domain | 동일 입력에서 동일 Decision 생성 |
| Application | 동일 Event 순서에서 동일 State Transition |
| Interface | 동일 DTO에서 동일 Contract 결과 |
| ROS Adapter Contract | 동일 Fake ROS Envelope에서 동일 Domain DTO |
| WebRTC Adapter Contract | 동일 Fake Packet에서 동일 송신 결과 |
| Storage Adapter | 동일 Event에서 동일 저장 Key와 Sync 순서 |
| Mission Creation | 동일 `SearchMissionRequest`와 SOP Profile에서 동일 Mission Draft Snapshot |
| Terrain Driven Navigation | 동일 TerrainAnalysisResult와 SearchMethod에서 동일 SearchDriveProfile |
| Module Boundary | 동일 Mock 입력에서 동일 금지 의존성 결과 |

---

## 6. 테스트 케이스

| Test ID | 목적 | 기준 |
|---|---|---|
| TC-DETVAL-001 | Fixed Clock 검증 | Event timestamp가 실행 시각에 의존하지 않음 |
| TC-DETVAL-002 | Fixed Seed 검증 | 동일 seed에서 동일 Detection/Fusion 결과 |
| TC-DETVAL-003 | Event Ordering 검증 | 동일 입력 Event에서 동일 처리 순서 |
| TC-DETVAL-004 | State Snapshot 검증 | 동일 시나리오에서 동일 Mission State Snapshot |
| TC-DETVAL-005 | Adapter Mapper 검증 | 동일 Fake Envelope에서 동일 DTO |
| TC-DETVAL-006 | Storage Key 검증 | 동일 Event에서 동일 저장 Key |
| TC-DETVAL-007 | Retry/Sync 검증 | 동일 장애 시나리오에서 동일 Retry 순서 |
| TC-DETVAL-008 | Mission Draft Snapshot 검증 | 동일 임무 생성 입력에서 동일 `draft_snapshot_id` |
| TC-DETVAL-009 | SearchDriveProfile 검증 | 동일 지형/탐색 방법 입력에서 동일 주행 profile |

---

## 7. 완료 기준

1. Domain/Application 테스트는 `FakeClock` 또는 고정 timestamp를 사용한다.
2. 난수가 필요한 테스트는 fixed seed를 명시한다.
3. Event ordering은 stable sort 또는 명시 priority로 결정한다.
4. Snapshot 테스트는 동일 입력에서 동일 결과를 보장한다.
5. Windows 기본 테스트는 실제 시간, 네트워크, ROS Runtime, 외부 DB/API에 의존하지 않는다.
6. `TC-DETVAL-*`는 `TC-LAYER-*`, `TC-DEP-*`, `TC-MOD-*`, `TC-LINT-*`, `TC-MISSION-*`와 함께 기본 Gate에 포함한다.
