# 12 TODO — Mock Detector & Fusion Logic

## Phase Reference
- Phase-2 Mock/TDD → Phase-4 Detector Integration

## Prompt

Mock Detector와 Fusion Logic을 구현해 주세요.

### Dependency Rule
```text
Service -> Config -> Types
```

### Reference Docs
- `implementation_roadmap.md` Phase-2, Phase-4
- `interface.md` (IDetector)
- `detailed_interface_schema.md`

### Create
```text
src/service/mock_detector.py         — Mock thermal/RGB/audio detector
src/service/fusion_logic.py          — Multi-sensor fusion (thermal > RGB > audio)
tests/unit/service/test_mock_detector.py
tests/unit/service/test_fusion_logic.py
```

### Features
- MockDetector returns fixed detection results per IDetector Protocol
- Thermal priority: THERMAL > RGB > AUDIO
- Fusion combines multiple detector outputs into a single VictimDecision
- Confidence score thresholding
- Fixed seed for deterministic test results

### Required TC
- TC-DETECT-001: Mock thermal detector returns fixed result
- TC-DETECT-002: Mock RGB detector returns fixed result
- TC-DETECT-003: Fusion combines thermal + RGB
- TC-DETECT-004: Thermal takes priority over RGB
- TC-DETECT-005: Below-threshold confidence is rejected
- TC-DETVAL-002: Fixed seed produces same detection result

### Completion Criteria
1. MockDetector implements IDetector Protocol
2. Fusion logic respects thermal > RGB > audio priority
3. Same input + same seed = same output
4. No real AI model or CUDA dependency
