# 08 TODO — UI 연결

## 실행 상태

```text
TODO
```

---

## 프롬프트

Service 구현과 테스트가 완료된 후 UI를 연결해 주세요.

의존성 규칙:

```text
UI → Service → Config → Types
```

UI는 다음을 직접 import하지 않습니다:

- DB Driver
- ROS Runtime
- Robot SDK
- Storage 구현체

### 참조 문서

- `dependency_direction_plan.md`
- `mission_creation_plan.md`
- `operation_plan.md`
- `detailed_test_case_spec.md`

### 생성 대상

```text
src/ui/mission_setup_view_model.py
src/ui/terrain_status_view_model.py
tests/unit/ui/test_mission_setup_view_model.py
tests/unit/ui/test_terrain_status_view_model.py
```

### 구현 기능

- Operator 입력을 `SearchMissionRequest`로 변환
- SearchArea, SearchMethod 선택 상태 표시
- SOP Profile 추천 결과 표시
- TerrainClass, SearchDriveProfile 상태 표시
- Mission Commander 승인 요청 상태 표시

### 필수 테스트

- `TC-DEP-004`: UI가 Service Interface만 사용
- `TC-MISSION-006`: UI가 DB/Repository에 직접 접근하지 않음
- `TC-MOD-005`: Server-2 UI 모듈 경계
- `TC-MOD-008`: UI→Service 경계 검증

### 완료 기준

1. UI는 Service Interface/ViewModel만 사용한다
2. UI는 DB/ROS/Robot SDK에 직접 접근하지 않는다
3. UI는 Mission Draft/Plan을 직접 생성하지 않는다
