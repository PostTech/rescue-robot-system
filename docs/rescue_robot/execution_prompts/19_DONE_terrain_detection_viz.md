# 19 TODO — Terrain & Detection Visualization

## Phase
- Phase MVP-5: Visualization

## Prompt

지형 분석과 센서 탐지 결과를 시각적으로 표현해 주세요.

### Create
```text
src/web/js/terrain_viz.js    — Canvas 기반 지형 시각화
src/web/js/detection_viz.js  — 탐지 결과 시각화
```

### Terrain Visualization
- Canvas에 지형 단면도 표시
- TerrainClass별 색상 매핑:
  - FLAT_OPEN: #4ade80 (초록)
  - MILD_SLOPE: #a3e635 (연초록)
  - STEEP_SLOPE: #facc15 (노란)
  - CLIFF_OR_DROP: #ef4444 (빨강)
  - ROUGH_RUBBLE: #f97316 (주황)
  - OBSTACLE_DENSE: #ec4899 (분홍)
  - NARROW_PASSAGE: #8b5cf6 (보라)
- 주행 프로파일 오버레이 (속도, 이동 모드)
- 통행 가능성 표시 (PASSABLE/CAUTION/BLOCKED)

### Detection Visualization
- 탐지 결과 카드: 센서 타입, 라벨, 신뢰도
- 신뢰도 바 (색상 그라데이션)
- 융합 결과 요약 카드
- 우선순위 표시 (THERMAL > RGB > AUDIO)

### Completion Criteria
1. 지형 분석 시 Canvas가 실시간 업데이트
2. 탐지 시 결과 카드 애니메이션 표시
3. 색상이 지형/위험도를 직관적으로 전달
