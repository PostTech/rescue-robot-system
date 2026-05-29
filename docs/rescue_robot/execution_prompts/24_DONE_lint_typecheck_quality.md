# 18 TODO — Lint, Type Check & Quality Gate

## Phase Reference
- Phase-1 Foundation (quality gate)

## Prompt

ruff, mypy를 설치하고 전체 품질 게이트를 통과시켜 주세요.

### Commands
```bash
pip install ruff mypy
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/ tests/ --ignore-missing-imports
```

### Create
```text
docs/rescue_robot/final_verification_report.md
```

### Fix Targets
- All ruff lint warnings
- All ruff format violations
- All mypy type errors (strict mode optional)

### Required TC
- TC-LINT-001: ruff check passes
- TC-LINT-002: ruff format passes
- TC-LINT-003: mypy passes

### Completion Criteria
1. `ruff check .` returns 0 violations
2. `ruff format --check .` returns 0 violations
3. `mypy src tests` returns 0 errors
4. Final verification report documents all results
