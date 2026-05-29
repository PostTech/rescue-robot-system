# 코드 작성 전 점검 체크리스트

## 1. 목적

본 문서는 실제 코드를 작성하기 전에 계획 문서 기준으로 반드시 확인해야 할 항목과, 반복적인 취사 삭제로 구조가 흔들렸는지 점검하는 기준을 정의한다.

---

## 2. 현재 구조 점검 결과

현재 문서 구조는 무너지지 않았다.

다만 다음 혼동 위험이 있다.

| 항목 | 상태 | 조치 |
|---|---|---|
| `Types -> Config -> Service -> UI` 의존성 방향 | 반영됨 | `TC-DEP-*`로 강제 |
| Service에서 UI import 금지 | 반영됨 | `../ui/` import 발견 시 즉시 수정 요청 |
| 신규 기능 Types First | 반영됨 | `TC-DEP-006`으로 강제 |
| Mission Creation | 반영됨 | `TC-MISSION-*`로 검증 |
| 3D LiDAR Terrain Driven Navigation | 반영됨 | `TC-TERRAIN-*`로 검증 |
| Windows 기본 테스트에서 ROS Runtime 제외 | 반영됨 | `dev-windows-local` 기준 유지 |
| 기존 `Domain/Application/Interface` 용어 혼재 | 혼동 위험 있음 | Types/Config/Service/UI 매핑 기준으로만 구현 |

결론:

```text
구조 붕괴 없음
    단,
기존 용어 혼재로 인한 구현 혼선 위험 있음
```

따라서 구현 기준은 항상 `dependency_direction_plan.md`를 최우선으로 한다.

---

## 3. 코드 작성 전 필수 점검

### 3.1 요구사항 점검

- 구현할 기능의 FR/NFR ID가 있는가?
- `traceability_matrix.md`에 Design, Implementation, Test, Operation 연결이 있는가?
- P0/P1/P2 우선순위가 명확한가?

### 3.2 Interface Baseline 점검

- `interface.md`와 `interface_baseline_freeze.md`에 필요한 Protocol/DTO가 정의되어 있는가?
- Interface 변경이 필요하면 Change Request가 필요한가?
- 기존 Client 3개, Server 4개 경계가 깨지지 않는가?

### 3.3 Dependency Direction 점검

고정 방향:

```text
Types -> Config -> Service -> UI
```

확인:

- Types가 Config/Service/UI를 import하지 않는가?
- Config가 Service/UI를 import하지 않는가?
- Service가 UI를 import하지 않는가?
- Service 파일에 `import ... from "../ui/..."`가 없는가?
- UI가 DB Driver, ROS Runtime, Robot SDK를 직접 import하지 않는가?

### 3.4 Types First 점검

새 기능은 반드시 Types 정의부터 시작한다.

순서:

```text
1. Types
2. Config
3. Service
4. UI
```

Types 없이 Service/UI부터 작성하면 구현 시작 조건을 만족하지 못한다.

### 3.5 Windows 기본 테스트 범위 점검

Windows `dev-windows-local`에서는 다음을 실행하지 않는다.

```text
ROS Runtime
rclpy
실제 ROS Topic Publish/Subscribe
실제 Sensor/HW
실제 DB Driver
```

Mock/Fake/Fixture 기반으로 먼저 검증한다.

### 3.6 Deterministic Validation 점검

- FakeClock 또는 고정 timestamp를 사용하는가?
- fixed seed를 사용하는가?
- fixed fixture를 사용하는가?
- 동일 입력에서 동일 DTO/Event/State/Profile이 생성되는가?

### 3.7 Test Gate 점검

구현 전 테스트 계획에 다음이 포함되어야 한다.

```text
TC-DEP-*
TC-LAYER-*
TC-IF-*
TC-MOD-*
TC-DETVAL-*
TC-FUNC-DEC-*
TC-FUNC-BND-*
TC-MISSION-*   # 임무 생성 기능 관련
TC-TERRAIN-*   # 3D LiDAR 지형 분석/탐색 주행 관련
TC-LINT-*
```

---

## 4. 취사 삭제 방지 기준

다음 항목은 임의 삭제하면 구조가 무너진다.

| 삭제 금지 대상 | 이유 |
|---|---|
| `dependency_direction_plan.md` | 코드 의존성 방향 기준 |
| `interface_baseline_freeze.md` | Interface 변경 통제 기준 |
| `traceability_matrix.md` | 요구사항-테스트 연결 기준 |
| `detailed_test_case_spec.md` | Gate 상세 기준 |
| `environment_profile_plan.md` | Windows/Linux 전환 기준 |
| `mission_creation_plan.md` | 탐색 임무 생성 기능 기준 |
| `deterministic_validation_plan.md` | 동일 입력/동일 결과 기준 |

삭제 또는 축약이 필요하면 다음 순서를 따른다.

```text
Change Request
    ↓
영향 분석
    ↓
Traceability 수정
    ↓
Test Gate 수정
    ↓
Baseline 승인
```

---

## 5. 구현 시작 승인 기준

다음 항목이 모두 Yes여야 구현을 시작한다.

| 점검 항목 | 기준 |
|---|---|
| 요구사항 ID 존재 | FR/NFR가 명확함 |
| Types 정의 존재 | DTO/Enum/Value Object 선행 |
| Config 정의 존재 | Threshold/Profile/Flag 분리 |
| Service 책임 명확 | UI/Runtime 직접 의존 없음 |
| UI 책임 명확 | Service Interface만 사용 |
| Test ID 존재 | `TC-*`가 Traceability에 연결 |
| Windows 테스트 가능 | ROS Runtime 없이 검증 가능 |
| Interface 변경 승인 | Baseline 변경 필요 시 승인됨 |

---

## 6. 최종 판정

```text
현재 구조:
    유지됨

주요 위험:
    용어 혼재와 임의 삭제

구현 기준:
    dependency_direction_plan.md
    interface_baseline_freeze.md
    detailed_test_case_spec.md
    traceability_matrix.md
```
