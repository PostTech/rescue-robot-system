# Interface Baseline Freeze 정책

## 1. 목적

본 문서는 Client 3개 모듈과 Server 4개 모듈의 Interface Contract를 고정하고, 임의 변경을 방지하기 위한 기준을 정의한다.

---

## 2. Baseline 대상

다음 문서는 Interface Baseline의 기준 문서다.

- `interface.md`
- `detailed_interface_schema.md`
- `traceability_matrix.md`
- `detailed_test_case_spec.md`

---

## 3. 고정 대상 Interface

### 3.1 Client Interface

| 모듈 | 고정 Inbound | 고정 Outbound |
|---|---|---|
| Client-1 | `IDataChannelReceiver`, `IControlCommandReceiver` | `IWebRTCTrackSender`, `IDataChannelSender`, `IRosTopicGateway` |
| Client-2 | `IDetector`, `IMediaPacketReceiver` | `IPerceptionEventPublisher`, `IRosTopicGateway` |
| Client-3 | `ISlamEngine`, `ITerrainAnalyzer`, `ISearchDrivePolicy`, `INavigationEngine`, `IRobotController` | `IRosTopicGateway`, `IEventPublisher` |

### 3.2 Server Interface

| 모듈 | 고정 Inbound | 고정 Outbound |
|---|---|---|
| Server-1 | `IMissionCore`, `IMissionCreationService`, `IEventSubscriber` | `IUiNotifier`, `IStorageWriter`, `IMissionRepository`, `ISopAgent`, `ISopMissionConfigurator` |
| Server-2 | `IUiNotifier`, `IStatusView` | `IMissionSetupSender`, `IControlCommandSender` |
| Server-3 | `IEventRepository`, `IMediaRepository`, `IMissionLogRepository`, `IMissionRepository` | `ISyncQueue` |
| Server-4 | `ISopAgent`, `ISopMissionConfigurator` | `IRecommendationPublisher` |

### 3.3 Baseline Revision B1 - Search Mission Creation Extension

관제자 탐색 임무 생성 기능을 위해 다음 Interface를 Baseline에 포함한다.

| Interface | 고정 목적 |
|---|---|
| `IMissionSetupSender` | UI에서 Mission Core로 `SearchMissionRequest` 송신 |
| `IMissionCreationService` | Search Mission Draft 생성, SearchArea/SearchMethod 검증, 승인 요청 |
| `IMissionRepository` | Mission Draft와 Search Mission Plan 저장/조회 |
| `ISopMissionConfigurator` | SOP Profile 기반 Mission 설정 추천 |

B1은 사용자 요구사항에 따른 승인된 확장이며, 이후 메서드명, 필수 DTO 필드, 책임 경계 변경은 Change Request를 필요로 한다.

### 3.4 Baseline Revision B2 - Terrain Driven Search Extension

3D LiDAR 지형 분석과 탐색 방법 기반 주행 결정을 위해 다음 Interface를 Baseline에 포함한다.

| Interface | 고정 목적 |
|---|---|
| `ITerrainAnalyzer` | 3D LiDAR PointCloud에서 slope, roughness, step height, obstacle density, traversability 계산 |
| `ISearchDrivePolicy` | TerrainAnalysisResult와 SearchMethod를 결합해 SearchDriveProfile 결정 |
| `INavigationEngine.plan_search_path()` | SearchDriveProfile 기반 탐색 경로 생성 |

B2는 사용자 요구사항에 따른 승인된 확장이며, ROS Message나 `rclpy`는 여전히 Domain/Application 계층에 노출하지 않는다.

---

### 3.5 Baseline Revision B3 - Dependency Direction Freeze

코드 의존성 방향은 다음 순서로 고정한다.

```text
Types -> Config -> Service -> UI
```

B3 기준:

| 계층 | 고정 규칙 |
|---|---|
| Types | Config, Service, UI를 import하지 않는다 |
| Config | Types만 import한다 |
| Service | Types, Config, Protocol만 import하고 UI를 import하지 않는다 |
| UI | Service Interface/ViewModel만 사용하고 DB Driver, ROS Runtime, Robot SDK에 직접 접근하지 않는다 |

---

## 4. 금지 변경

승인 없이 다음 변경을 금지한다.

```text
1. Interface 메서드 이름 변경
2. Input/Output DTO 필드 삭제
3. Event Type 이름 변경
4. DataChannel 이름 변경
5. ROS Topic 계약 변경
6. Client/Server 직접 의존 추가
7. SOP Agent의 ControlCommand 생성 추가
8. UI의 DB 직접 접근 추가
9. SOP Agent의 Mission Start 직접 수행 추가
10. UI의 Mission Draft/Plan 직접 저장 추가
11. Domain/Application 계층의 3D LiDAR ROS Message 직접 의존 추가
12. TerrainAnalysisResult 없이 SearchMethod만으로 주행 방식 확정
13. Types → Config/Service/UI 의존 추가
14. Config → Service/UI 의존 추가
15. Service → UI 의존 추가
16. UI → DB Driver/ROS Runtime/Robot SDK 직접 의존 추가
```

---

## 5. 허용 변경

하위 호환이 유지되는 경우에만 허용한다.

```text
1. Optional 필드 추가
2. 신규 Event Type 추가
3. 신규 Mock 구현체 추가
4. 신규 Adapter 추가
5. 신규 테스트 케이스 추가
6. B1 범위 안에서 `SearchMissionRequest`, `MissionDraft`, `SearchMissionPlan`의 Optional 필드 추가
7. B2 범위 안에서 SearchMethod enum 값 추가
8. B2 범위 안에서 TerrainClass/TraversabilityLevel enum 값 추가
9. B3 범위 안에서 의존성 방향을 깨지 않는 내부 파일 분리
```

단, 변경 시 관련 테스트와 추적성 매트릭스를 함께 업데이트해야 한다.

---

## 6. 변경 절차

Interface 변경은 다음 순서를 따른다.

```text
Change Request
    ↓
Impact Analysis
    ↓
Interface Contract Update
    ↓
TC-IF-* Update
    ↓
TC-MOD-* Update
    ↓
Traceability Matrix Update
    ↓
Review / Approval
```

승인 책임:

| 변경 대상 | 승인 |
|---|---|
| Domain DTO | System Architect |
| Client/Server Contract | System Architect + Tech Lead |
| Safety 관련 Interface | Safety Officer |
| Security 관련 Interface | Security Lead |
| Test Gate 변경 | Tech Lead |

---

## 7. 고정 검증 Gate

| Test ID | 목적 |
|---|---|
| TC-IF-* | Interface Contract 유지 |
| TC-MOD-* | Client/Server Boundary 유지 |
| TC-LAYER-* | Dependency Direction 유지 |
| TC-DEP-* | `Types -> Config -> Service -> UI` 의존성 방향 유지 |
| TC-DETVAL-* | 동일 Contract 입력의 동일 결과 유지 |
| TC-MISSION-* | 탐색 임무 생성, 구역 지정, 방법 선택, SOP 설정 유지 |
| TC-TERRAIN-* | 3D LiDAR 지형 분석과 탐색 방법 기반 주행 정책 유지 |

---

## 8. 완료 기준

1. Client 3개와 Server 4개의 Inbound/Outbound Contract가 고정된다.
2. Interface 변경은 Change Request 없이 수행하지 않는다.
3. Interface 변경 시 테스트와 추적성 매트릭스를 함께 수정한다.
4. `TC-IF-*`, `TC-MOD-*`, `TC-LAYER-*`, `TC-DEP-*`가 통과해야 Baseline 유지로 판단한다.
5. 탐색 임무 생성 관련 변경은 `TC-MISSION-*`까지 통과해야 Baseline 유지로 판단한다.
6. 지형 분석/주행 정책 변경은 `TC-TERRAIN-*`까지 통과해야 Baseline 유지로 판단한다.
7. Service 파일에서 `import ... from "../ui/..."` 또는 UI import가 발견되면 즉시 수정 요청한다.
8. 신규 기능은 Types 정의가 선행되어야 하며, Types 없이 Service/UI부터 구현한 변경은 Baseline 위반이다.
