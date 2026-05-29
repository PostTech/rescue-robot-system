# 탐색 임무 생성 기능 계획

## 1. 확인 결과

기존 문서에는 Mission Start, Mission Management, SOP Recommendation은 정의되어 있었지만 다음 기능은 명시적으로 고정되어 있지 않았다.

- 관제자가 탐색 임무를 생성
- 탐색 구역 지정
- 탐색 방법 선택
- SOP Profile을 통한 임무 설정

따라서 본 문서를 신규 기준 문서로 추가하고, 관련 요구사항, Interface, Test Gate, Traceability에 반영한다.

---

## 2. 기능 범위

탐색 임무 생성 기능은 관제자가 임무 시작 전에 Search Mission Draft를 만들고, Mission Commander 승인 후 실행 가능한 Search Mission Plan으로 확정하는 기능이다.

포함 범위:

- Operator UI에서 탐색 임무 생성
- 탐색 구역 지정
- 탐색 방법 선택
- SOP Profile 적용
- Mission Core의 검증, 승인 요청, 확정
- Mission Repository 저장
- Windows `dev-windows-local` 환경의 Mock/Fake 기반 테스트

제외 범위:

- SOP Agent의 직접 Mission Start
- SOP Agent의 직접 ControlCommand 생성
- UI의 DB 직접 저장
- Windows 기본 테스트에서 실제 ROS Runtime 실행

---

## 3. 역할 분리

| 모듈 | 책임 | 금지 |
|---|---|---|
| Server-1 Mission Core | 임무 Draft 생성, 검증, 승인 요청, Plan 확정 | DB Driver 직접 접근 |
| Server-2 UI | 관제자 입력 수집, 임무 생성 요청 송신 | DB 직접 저장, 로봇 SDK 직접 호출 |
| Server-3 Storage / DB | Mission Draft/Plan 저장 및 조회 | Mission 판단 |
| Server-4 AI Agent / SOP | SOP 기반 설정값 추천 | Mission Start, ControlCommand 생성 |
| Client-3 Navigation / Control | 승인된 Mission Plan을 실행 가능한 경로/제어로 반영 | UI/SOP 직접 호출 |

---

## 4. 탐색 구역 지정

지원 방식:

| Area Type | 설명 | 검증 기준 |
|---|---|---|
| `POLYGON` | 지도 위 다각형 탐색 영역 | 점 3개 이상, self-intersection 없음 |
| `WAYPOINT_ROUTE` | 순차 경유점 기반 탐색 | waypoint 2개 이상 |
| `GRID` | 격자 기반 구역 탐색 | cell size, boundary 필수 |
| `GEOFENCE` | 진입/이탈 제한 구역 | mission area와 충돌 없음 |

탐색 구역은 Domain DTO로 표현하며, ROS 좌표계나 지도 메시지는 Adapter 내부에서만 변환한다.

---

## 5. 탐색 방법 선택

검색 기준으로 IAMSAR/SAR 표준 탐색 패턴과 로봇 자율 탐색 패턴을 함께 반영한다.

참조 근거:

- IAMSAR 계열 SAR 패턴: Expanding Square, Sector, Parallel Track, Creeping Line  
  Reference: https://www.amnautical.com/blogs/the-mariners-blog/what-is-iamsar-manual-and-its-purpose
- Land SAR 패턴: Single File, Track Sweep, Parallel Sweep, Contour Search  
  Reference: https://www.scribd.com/document/792632407/NATSAR-Manual-Sept-2018
- Robot exploration 패턴: Frontier-based exploration  
  Reference: https://www.robotfrontier.com/papers/cira97.pdf
- 3D LiDAR traversability 기준: elevation grid map, height difference, slope, roughness  
  Reference: https://journals.sagepub.com/doi/pdf/10.1177/1729881417751530

| Search Method | 사용 상황 |
|---|---|
| `AREA_SWEEP` | 지정 영역을 체계적으로 훑는 기본 탐색 |
| `PARALLEL_SWEEP` | 사각형/완만한 지형에서 평행 주행선으로 균일 탐색 |
| `CREEPING_LINE` | 특정 방향으로 가능성이 치우친 넓은 구역을 점진적으로 탐색 |
| `EXPANDING_SQUARE` | 마지막 위치 또는 추정 위치가 비교적 정확할 때 중심에서 확장 |
| `SECTOR_SEARCH` | 기준점이 명확하고 반경 내 집중 탐색이 필요할 때 |
| `TRACKLINE_SEARCH` | 예상 이동 경로, 도로, 계곡, 통로를 따라 탐색 |
| `CONTOUR_SEARCH` | 산악/사면에서 등고선 또는 고도대를 따라 탐색 |
| `TRACK_SWEEP` | 길/통로 중심선 주변을 좌우로 훑는 탐색 |
| `SINGLE_FILE` | 좁은 통로, 협소 공간, 잔해 사이를 한 줄로 통과 |
| `GRID_COVERAGE` | 격자 기반 정밀 탐색 |
| `FRONTIER_EXPLORATION` | 미지 영역 경계로 이동하며 지도 확장 탐색 |
| `WAYPOINT_ROUTE` | 관제자가 지정한 순서대로 이동 |
| `SPIRAL_SEARCH` | 마지막 감지 위치 주변 확장 탐색 |
| `PERIMETER_SEARCH` | 경계선 우선 탐색 |
| `MANUAL_ASSISTED` | 관제자 보조 기반 반자동 탐색 |

Mission Core는 탐색 방법을 Mission State와 SearchArea에 맞게 검증하고, 불가능한 조합은 승인 요청 전 차단한다.

---

## 5.1 3D LiDAR 지형 분석 기반 탐색 방법 선택

3D LiDAR 지형 분석 결과는 탐색 방법 선택과 주행 정책에 직접 반영한다.

```text
3D LiDAR PointCloud
    ↓
Elevation Grid Map
    ↓
Slope / Roughness / Step Height / Obstacle Density
    ↓
Terrain Class
    ↓
Search Method Compatibility Check
    ↓
Search Drive Profile
    ↓
Navigation / Locomotion
```

| Terrain Class | 권장 탐색 방법 | 주행 정책 |
|---|---|---|
| `FLAT_OPEN` | `PARALLEL_SWEEP`, `GRID_COVERAGE`, `AREA_SWEEP` | 직선 구간 유지, 정상 속도 |
| `MILD_SLOPE` | `CONTOUR_SEARCH`, `PARALLEL_SWEEP` | 등고선 우선, 횡경사 제한 |
| `STEEP_SLOPE` | `CONTOUR_SEARCH`, `WAYPOINT_ROUTE` | 저속, 경사 한계 초과 시 우회 |
| `ROUGH_RUBBLE` | `FRONTIER_EXPLORATION`, `MANUAL_ASSISTED` | 저속, 장애물 등반/우회, 짧은 재계획 |
| `NARROW_PASSAGE` | `SINGLE_FILE`, `TRACKLINE_SEARCH`, `WAYPOINT_ROUTE` | 중앙선 추종, 저속, 최소 회전 반경 제한 |
| `OBSTACLE_DENSE` | `PERIMETER_SEARCH`, `FRONTIER_EXPLORATION` | 외곽 우선, 통과 불가 구간 replan |
| `CLIFF_OR_DROP` | `PERIMETER_SEARCH` | 진입 금지, 즉시 정지 또는 우회 |
| `UNKNOWN` | `MANUAL_ASSISTED`, `FRONTIER_EXPLORATION` | 센서 재관측, 속도 제한 |

결정 규칙:

```text
if terrain.traversability_score < stop_threshold:
    drive_mode = STOP_AND_REPLAN
elif terrain.terrain_class == STEEP_SLOPE:
    search_method = CONTOUR_SEARCH or WAYPOINT_ROUTE
    drive_mode = SLOW_SAFE
elif terrain.terrain_class == FLAT_OPEN and area_type in {POLYGON, GRID}:
    search_method = PARALLEL_SWEEP or GRID_COVERAGE
    drive_mode = NORMAL_WHEEL
elif terrain.terrain_class == ROUGH_RUBBLE:
    search_method = FRONTIER_EXPLORATION or MANUAL_ASSISTED
    drive_mode = OBSTACLE_CLIMB
else:
    drive_mode = SLOW_SAFE
```

## 6. SOP 기반 설정

SOP Profile은 임무 생성 단계에서 기본값과 제한 조건을 제공한다.

| SOP 설정 항목 | 적용 예 |
|---|---|
| `sop_profile_id` | mountain_missing_person, collapsed_structure, tunnel_gas_risk |
| 위험 정책 | gas danger 시 stop/retreat, slope limit, no-go zone |
| 탐색 방법 추천 | 현장 유형에 맞는 Search Method 추천 |
| 센서 우선순위 | thermal first, gas first, audio assist |
| 통신 정책 | low bandwidth 시 pointcloud downsample |
| 승인 정책 | 고위험 SOP는 Mission Commander 승인 필수 |

SOP Agent는 `MissionSetupRecommendation`만 반환하며, Mission 생성/시작/제어는 수행하지 않는다.

---

## 7. 표준 Workflow

```text
Operator selects SOP Profile
    ↓
Operator creates SearchMissionRequest
    ↓
Operator defines SearchArea
    ↓
Operator selects SearchMethod
    ↓
Mission Core validates request
    ↓
SOP Mission Configurator recommends constraints/defaults
    ↓
Mission Draft saved through Mission Repository
    ↓
Mission Commander approves
    ↓
Mission Core freezes SearchMissionPlan
    ↓
Approved plan is delivered through existing command/event path
```

---

## 8. 고정 Interface

신규 Interface는 `interface_baseline_freeze.md`의 Mission Creation Extension 기준으로 고정한다.

| Interface | 소유 모듈 | 목적 |
|---|---|---|
| `IMissionSetupSender` | Server-2 | UI에서 Mission Core로 임무 생성 요청 송신 |
| `IMissionCreationService` | Server-1 | Draft 생성, 구역/방법 검증, 승인 요청 |
| `IMissionRepository` | Server-3 | Draft/Plan 저장 및 조회 |
| `ISopMissionConfigurator` | Server-4 | SOP 기반 설정 추천 |

---

## 9. Test Gate

| Test ID | 검증 |
|---|---|
| TC-MISSION-001 | Operator가 `SearchMissionRequest`를 생성할 수 있다 |
| TC-MISSION-002 | SearchArea 필수값과 경계 조건을 검증한다 |
| TC-MISSION-003 | SearchMethod 선택값을 Mission State와 Area Type 기준으로 검증한다 |
| TC-MISSION-004 | SOP Profile 적용 시 동일 입력에서 동일 `MissionSetupRecommendation`이 생성된다 |
| TC-MISSION-005 | Mission Commander 승인 전에는 Mission Plan이 활성화되지 않는다 |
| TC-MISSION-006 | Server-2 UI는 Mission Repository/DB에 직접 접근하지 않는다 |
| TC-MISSION-007 | Server-4 SOP는 Mission Start 또는 ControlCommand를 생성하지 않는다 |
| TC-MISSION-008 | FakeClock과 deterministic id를 사용하면 동일 Mission Draft Snapshot이 생성된다 |

Windows 기본 테스트는 ROS Runtime 없이 `tests/unit`, `tests/contract`, `tests/module_boundary`, `tests/layer` 범위에서 수행한다.

---

## 10. 완료 기준

1. FR-016부터 FR-020까지 요구사항이 Traceability Matrix에 연결된다.
2. `IMissionSetupSender`, `IMissionCreationService`, `IMissionRepository`, `ISopMissionConfigurator`가 Interface Baseline에 포함된다.
3. `TC-MISSION-*`, 관련 `TC-IF-*`, `TC-MOD-*`, `TC-FUNC-*`가 정의된다.
4. SOP 기반 설정은 Recommendation으로 제한되고 직접 제어를 수행하지 않는다.
5. Windows 기본 테스트에서 ROS Runtime 없이 검증 가능해야 한다.
