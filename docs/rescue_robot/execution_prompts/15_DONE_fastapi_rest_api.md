# 15 DONE — FastAPI REST API Server

## Phase
- Phase MVP-1: Backend API

## Context & Specifications References

> [!IMPORTANT]
> 본 단계를 완벽히 구현하기 위해 다음 설계 명세서의 구체적인 스키마 구조를 반드시 참조하여 100% 일관되게 코딩하십시오.
> - **도메인 DTO 및 JSON 스키마 명세**: [detailed_interface_schema.md:L117-195](file:///c:/Users/cosmo/AI_challange/docs/rescue_robot/detailed_interface_schema.md#L117-L195)
> - **미션 생성 필드 및 데이터 명세**: [detailed_interface_schema.md:L240-270](file:///c:/Users/cosmo/AI_challange/docs/rescue_robot/detailed_interface_schema.md#L240-L270)

---

## Prompt

기존 Service 계층 위에 FastAPI REST API를 올려 주세요.

### Technology
```text
Backend: FastAPI (Python)
Port: 8000
CORS: localhost:5500 허용
```

### Create
```text
src/api/__init__.py
src/api/server.py           — FastAPI app 인스턴스, CORS, lifespan
src/api/routes_mission.py   — /api/missions CRUD
src/api/routes_terrain.py   — /api/terrain 분석 결과
src/api/routes_safety.py    — /api/safety 상태, emergency stop
src/api/routes_detection.py — /api/detection 센서 융합 결과
src/api/deps.py             — DI: ApplicationService singleton
```

### Endpoints & JSON Schema 명세

| Method | Path | Request Body Schema (JSON) | Response Schema (JSON) |
|---|---|---|---|
| POST | `/api/missions` | `{ "operator_id": "str", "mission_name": "str", "search_area": { "area_type": "str", "coordinates": [...] }, "search_method": "str", "sop_profile_id": "str", "priority": "str" }` | `{ "mission_id": "str", "validation_status": "str", "sop_constraints": {}, "draft_snapshot_id": "str" }` |
| GET | `/api/missions` | None (Query parameter) | `[ { "mission_id": "str", "name": "str", "status": "str", "priority": "str", "sop_profile_id": "str", ... } ]` |
| GET | `/api/missions/{id}` | None | `{ "mission_id": "str", "request": {}, "draft": {}, "plan": {} or null, "state": "str", ... }` |
| POST | `/api/missions/{id}/approve` | `{ "approver": "str" }` | `{ "mission_id": "str", "approved_by": "str", "approved_at_ms": int, "plan_snapshot_id": "str" }` |
| POST | `/api/missions/{id}/start` | None | `{ "mission_id": "str", "state": "str" }` |
| POST | `/api/missions/{id}/complete` | None | `{ "mission_id": "str", "state": "str" }` |
| POST | `/api/missions/{id}/emergency-stop` | None | `{ "mission_id": "str", "state": "str" }` |

---

## TDD Driver & Verification

> [!TIP]
> 코드를 작성하기 전, 반드시 다음 테스트 스위트를 검토 및 구동하여 인터페이스 구현 계약이 성립하는지 Red ➡️ Green 상태를 입증하며 점진적으로 코딩하십시오.
> - **TDD 드라이버 테스트 파일**: [tests/unit/api/test_server.py](file:///c:/Users/cosmo/AI_challange/tests/unit/api/test_server.py)

### Completion Criteria
1. `uvicorn src.api.server:app` 으로 서버 시작
2. 모든 엔드포인트가 지정된 JSON 규격으로 정상 응답
3. ApplicationService를 DI로 주입하여 싱글톤 생명주기 관리
4. FakeClock + DeterministicIdGenerator 사용
5. `pytest tests/unit/api/test_server.py` 통과

