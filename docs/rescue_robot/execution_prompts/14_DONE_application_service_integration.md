# 14 TODO — Application Service Integration

## Phase Reference
- Phase-3 Business Logic

## Prompt

개별 Service를 Application Service로 통합해 주세요.

### Dependency Rule
```text
Service -> Config -> Types
```

### Reference Docs
- `implementation_roadmap.md` Phase-3
- `mission_creation_plan.md`
- `operation_plan.md`
- `interface_baseline_freeze.md`

### Create
```text
src/service/application_service.py    — Top-level orchestrator
tests/unit/service/test_application_service.py
tests/integration/test_full_mission_flow.py
```

### Features
- Full mission lifecycle: Create -> Validate -> Approve -> Execute -> Complete
- Event bus connects all services
- Terrain analysis feeds into drive profile during execution
- Safety manager can abort any mission
- SOP recommendation applied at creation time
- Deterministic end-to-end test with FakeClock + DeterministicIdGenerator

### Required TC
- TC-INTEG-001: Full mission creation to approval flow
- TC-INTEG-002: Terrain analysis during mission execution
- TC-INTEG-003: Emergency stop aborts active mission
- TC-INTEG-004: SOP recommendation applied correctly
- TC-INTEG-005: Deterministic full-flow replay

### Completion Criteria
1. Application service wires all components via dependency injection
2. Full flow works with all mock implementations
3. Same input sequence produces same final state
4. No real HW, network, or ROS dependency
