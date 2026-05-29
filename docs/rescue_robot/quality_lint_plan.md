# Python 품질 및 Lint 계획서

## 1. 목적

본 문서는 Python 기반 구현물의 코드 품질, 정적 분석, 타입 검증, 테스트 실행 기준을 정의한다.

---

## 2. 품질 원칙

- Lint는 기능 테스트 이전에 실행한다.
- Lint 실패는 테스트 실패와 동일하게 처리한다.
- Safety 관련 코드는 타입 힌트와 테스트를 필수로 작성한다.
- Hotfix 예외는 승인자, 사유, 재검증 일정을 기록한다.

---

## 3. 권장 도구

| 도구 | 목적 | Gate |
|---|---|---|
| Ruff | Lint 및 기본 정적 분석 | 필수 |
| Ruff Format | Formatting 검증 | 필수 |
| mypy | Type Check | 필수 |
| pytest | Windows 기본 Unit/Contract/Layer/Module Boundary/Mission Creation/Terrain Test | 필수 |
| bandit | Python 보안 정적 분석 | 권장 |
| pip-audit | Dependency 취약점 점검 | 권장 |

---

## 4. 기본 명령

Windows 기본 프로파일에서는 ROS Runtime까지 진행하지 않는다.

```text
$env:RUNTIME_PROFILE = "dev-windows-local"
ruff check .
ruff format --check .
mypy src tests
pytest tests/unit tests/contract tests/layer tests/dependency tests/module_boundary tests/mission_creation tests/terrain
bandit -r src
pip-audit
```

---

## 5. CI Gate

| 단계 | 명령 | 실패 시 조치 |
|---|---|---|
| Format | `ruff format --check .` | Merge 차단 |
| Lint | `ruff check .` | Merge 차단 |
| Type | `mypy src tests` | Merge 차단 |
| Test | `pytest tests/unit tests/contract tests/layer tests/dependency tests/module_boundary tests/mission_creation tests/terrain` | Merge 차단 |
| Security | `bandit -r src` | High 이상 Merge 차단 |

---

## 6. Python 작성 기준

- Domain Data는 `dataclass(frozen=True)`를 기본으로 한다.
- Interface는 `typing.Protocol`을 사용한다.
- Event Payload는 명시적 schema를 둔다.
- 직접 문자열 비교가 많은 상태값은 `StrEnum`을 사용한다.
- Adapter는 Domain Layer가 아닌 외부 계층에 둔다.
- SOP Agent는 `ControlCommand`를 반환하지 않는다.
- Mission 생성 로직은 `SearchMissionRequest`, `MissionDraft`, `SearchMissionPlan` DTO를 사용한다.
- 지형 기반 주행 로직은 `TerrainAnalysisResult`, `SearchDriveProfile` DTO를 사용한다.
- 코드 의존성 방향은 `Types -> Config -> Service -> UI`를 반드시 지킨다.
- Service 파일에서 `import ... from "../ui/..."`가 발견되면 즉시 수정 요청한다.
- 새 기능은 Types 정의부터 시작한다.

---

## 7. 완료 기준

1. 모든 P0 모듈은 Ruff, Format, mypy, Windows 기본 pytest 범위를 통과한다.
2. Safety, Control, Storage, Failover 코드는 테스트 커버리지 대상에 포함한다.
3. Lint 예외는 코드 주석이 아니라 별도 승인 기록으로 관리한다.
4. Windows 기본 테스트는 ROS Runtime, rclpy, 실제 ROS Topic을 실행하지 않는다.
5. Release Candidate는 품질 Gate 실패 상태로 만들지 않는다.
