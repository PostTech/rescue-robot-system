# 17 TODO — End-to-End Scenario Tests

## Phase Reference
- Phase-3 Business Logic (completion gate)

## Prompt

SOP 시나리오별 E2E 테스트를 작성해 주세요.

### Reference Docs
- `mission_creation_plan.md` Section 7 (Standard Workflow)
- `safety_sop.md`
- `detailed_test_case_spec.md`

### Create
```text
tests/scenario/test_mountain_missing_person.py
tests/scenario/test_collapsed_structure.py
tests/scenario/test_tunnel_gas_risk.py
```

### Scenarios
1. **Mountain Missing Person**
   - SOP profile: mountain_missing_person
   - Terrain: STEEP_SLOPE -> CONTOUR_SEARCH
   - Detection: thermal priority
   - Full flow: create -> approve -> execute -> terrain update -> drive profile -> detect -> complete

2. **Collapsed Structure**
   - SOP profile: collapsed_structure
   - Terrain: ROUGH_RUBBLE -> FRONTIER_EXPLORATION
   - Detection: thermal + audio
   - Gas detection -> retreat event

3. **Tunnel Gas Risk**
   - SOP profile: tunnel_gas_risk
   - Terrain: NARROW_PASSAGE -> SINGLE_FILE
   - Gas CO2 > threshold -> EMERGENCY_STOP
   - Full gas safety protocol

### Required TC
- TC-SCENARIO-001: Mountain search completes
- TC-SCENARIO-002: Collapsed structure with gas retreat
- TC-SCENARIO-003: Tunnel gas emergency stop
- TC-SCENARIO-004: All scenarios deterministic with FakeClock

### Completion Criteria
1. Each scenario exercises the full Types->Config->Service->UI stack
2. All scenarios use FakeClock and DeterministicIdGenerator
3. Same input = same output for all scenarios
4. Gas/cliff safety triggers correctly
