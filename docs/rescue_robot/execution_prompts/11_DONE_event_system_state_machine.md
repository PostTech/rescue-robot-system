# 11 TODO — Event System & State Machine

## Phase Reference
- Phase-2 Mock/TDD → Phase-3 Business Logic

## Prompt

Event System과 State Machine을 구현해 주세요.

### Dependency Rule
```text
Service -> Config -> Types
```

### Reference Docs
- `implementation_roadmap.md` Phase-2, Phase-3
- `interface.md`
- `detailed_interface_schema.md`
- `detailed_test_case_spec.md`

### Create
```text
src/service/event_bus.py            — In-process event bus (publish/subscribe)
src/service/mission_state_machine.py — Mission lifecycle state machine
src/service/safety_manager.py       — Emergency stop, safe mode logic
tests/unit/service/test_event_bus.py
tests/unit/service/test_mission_state_machine.py
tests/unit/service/test_safety_manager.py
```

### Features
- Event publish/subscribe (sync, in-process)
- Mission lifecycle: DRAFT -> PENDING -> APPROVED -> ACTIVE -> COMPLETED / ABORTED
- Emergency stop overrides all states -> EMERGENCY_STOPPED
- State transition validation (forbidden transitions rejected)
- Safety priority: EMERGENCY_STOP > SAFE_MODE > MISSION

### Required TC
- TC-STATE-001: Valid state transitions
- TC-STATE-002: Forbidden transition rejected
- TC-STATE-003: Emergency stop overrides any state
- TC-SAFETY-001: Emergency stop triggers STOP_AND_REPLAN
- TC-SAFETY-002: Gas alert triggers retreat
- TC-EVENT-001: Event publish/subscribe roundtrip
- TC-EVENT-002: Event ordering by timestamp

### Completion Criteria
1. Event bus delivers events to all subscribers
2. State machine rejects invalid transitions
3. Emergency stop overrides any mission state
4. No ROS/rclpy/real network dependency
