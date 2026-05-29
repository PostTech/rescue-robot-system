# 의존성 방향 고정 계획

## 1. 목적

본 문서는 구현 단계에서 모든 코드가 반드시 지켜야 하는 의존성 방향을 고정한다.

---

## 2. 고정 의존성 순서

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
```

해석:

- 계층 순서는 `Types -> Config -> Service -> UI`로 고정한다.
- 상위 계층은 하위 계층을 사용할 수 있다.
- 하위 계층은 상위 계층을 import하거나 호출할 수 없다.
- 즉 실제 import 허용 범위는 다음과 같다.

| 계층 | import 허용 | import 금지 |
|---|---|---|
| Types | Python 표준 라이브러리, typing, dataclass, enum | Config, Service, UI, Adapter, ROS, DB, WebRTC |
| Config | Types | Service, UI, Adapter Runtime, ROS Node |
| Service | Types, Config, Interface Protocol | UI, concrete DB Driver, concrete ROS Runtime |
| UI | Types, Config, Service Interface/ViewModel | DB Driver, ROS Runtime, Robot SDK 직접 접근 |

---

## 3. 역할 정의

| 계층 | 책임 |
|---|---|
| Types | DTO, Value Object, Enum, Protocol 입력/출력 타입, Validation Result |
| Config | Runtime Profile, Threshold, SOP Profile, Feature Flag, Environment Profile |
| Service | Mission Creation, Terrain Analysis Policy, Search Drive Policy, State Machine, Use Case |
| UI | Operator 입력, Mission Setup 화면, Status/ViewModel 표시, 승인 요청 |

---

## 4. 금지 규칙

```text
Types → Config import 금지
Types → Service import 금지
Types → UI import 금지
Config → Service import 금지
Config → UI import 금지
Service → UI import 금지
UI → DB Driver 직접 접근 금지
UI → ROS Runtime 직접 접근 금지
UI → Robot SDK 직접 접근 금지
```

Service 파일에서 다음 패턴이 발견되면 즉시 수정 요청 대상으로 분류한다.

```text
import ... from "../ui/..."
from ..ui import ...
from ui import ...
```

즉, Service는 UI를 참조하지 않는다. 필요한 출력은 Types에 정의한 DTO/ViewModel 또는 Protocol을 통해 전달한다.

---

## 5. 신규 기능 구현 순서

새 기능은 반드시 Types 정의부터 시작한다.

```text
1. Types 정의
   - DTO
   - Enum
   - Value Object
   - Validation Result
   - Protocol 입출력 타입

2. Config 정의
   - Threshold
   - SOP Profile
   - Runtime Profile
   - Feature Flag

3. Service 구현
   - Use Case
   - Policy
   - State Transition
   - Validation

4. UI 연결
   - Operator Input
   - ViewModel
   - Alert / Status 표시
```

Types 정의 없이 Service/UI부터 구현한 변경은 완료로 인정하지 않는다.

---

## 6. 탐색 임무 생성 적용

```text
Types
    SearchMissionRequest
    SearchArea
    SearchMethod
    MissionDraft
    SearchMissionPlan

Config
    SOP Profile
    Search Method Policy Threshold
    Environment Profile

Service
    MissionCreationService
    SearchAreaValidator
    MissionApprovalGuard

UI
    Mission Setup UI
    Operator Input
    Approval View
```

---

## 7. 3D LiDAR 지형 분석 적용

```text
Types
    TerrainAnalysisResult
    TerrainClass
    TraversabilityLevel
    SearchDriveProfile

Config
    Terrain Threshold
    Traversability Threshold
    Speed Limit Policy

Service
    TerrainAnalyzer
    SearchDrivePolicy
    Navigation Use Case

UI
    Terrain Overlay
    Drive Profile Status
    Operator Alert
```

---

## 8. Test Gate

| Test ID | 목적 | 기준 |
|---|---|---|
| TC-DEP-001 | Types 독립성 | Types에서 Config/Service/UI import 없음 |
| TC-DEP-002 | Config 독립성 | Config에서 Service/UI import 없음 |
| TC-DEP-003 | Service 독립성 | Service에서 UI import 없음, `import ... from "../ui/..."` 발견 시 실패 |
| TC-DEP-004 | UI 직접 Runtime 차단 | UI에서 DB Driver/ROS Runtime/Robot SDK 직접 import 없음 |
| TC-DEP-005 | 순환 의존성 차단 | Types, Config, Service, UI 간 cycle 없음 |
| TC-DEP-006 | 신규 기능 Types First | 신규 기능 변경분에 Types 정의가 선행됨 |

---

## 9. 완료 기준

1. 모든 신규 구현은 `Types -> Config -> Service -> UI` 순서를 따른다.
2. `TC-DEP-*`는 Windows 기본 테스트 Gate에 포함한다.
3. `TC-LAYER-*`, `TC-MOD-*`, `TC-DEP-*` 중 하나라도 실패하면 구현 완료로 인정하지 않는다.
4. Service 파일에서 `../ui/` import가 발견되면 즉시 수정 요청한다.
5. 새 기능은 Types 정의 없이 Service/UI부터 구현하지 않는다.
