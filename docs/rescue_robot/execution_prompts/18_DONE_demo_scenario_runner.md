# 18 TODO — Demo Scenario Runner

## Phase
- Phase MVP-4: Demo

## Prompt

버튼 하나로 전체 시나리오를 시연할 수 있는 Demo Runner를 만들어 주세요.

### Create
```text
src/api/routes_demo.py      — /api/demo/* 시나리오 실행
src/web/js/demo.js           — Demo UI 컨트롤
```

### Scenarios
1. **산악 실종자 수색**
   - 미션 생성 (mountain_missing_person)
   - 지형: FLAT → STEEP_SLOPE → FLAT
   - 탐지: thermal 0.92 confidence
   - 완료

2. **붕괴 구조물 탐색**
   - 미션 생성 (collapsed_structure)
   - 지형: ROUGH_RUBBLE → OBSTACLE_DENSE
   - 탐지: thermal + audio
   - 가스 감지 → 안전 후퇴

3. **터널 가스 위험**
   - 미션 생성 (tunnel_gas_risk)
   - 지형: NARROW_PASSAGE
   - 가스 CO2 초과 → EMERGENCY_STOP

### Features
- Demo 버튼 클릭 시 1~2초 간격으로 이벤트 자동 발생
- 각 단계마다 대시보드 실시간 업데이트
- 진행률 표시
- 시나리오 설명 오버레이

### Completion Criteria
1. 3개 시나리오 모두 자동 실행
2. WebSocket으로 실시간 대시보드 반영
3. 각 시나리오별 차이가 시각적으로 구분
