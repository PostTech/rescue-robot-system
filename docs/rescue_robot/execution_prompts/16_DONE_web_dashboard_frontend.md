# 16 TODO — Web Dashboard Frontend (Mission Control)

## Phase
- Phase MVP-2: Frontend UI

## Prompt

미션 관제 대시보드를 HTML/CSS/JS로 만들어 주세요.

### Technology
```text
Frontend: HTML + CSS + JavaScript (Vanilla)
Design: Dark theme, glassmorphism, micro-animations
Font: Inter (Google Fonts)
Icons: Lucide Icons CDN
API: fetch() -> localhost:8000/api/*
```

### Create
```text
src/web/index.html          — 메인 대시보드 페이지
src/web/css/dashboard.css   — 전체 스타일
src/web/js/app.js           — 메인 앱 로직
src/web/js/api.js           — API 클라이언트
src/web/js/components.js    — UI 컴포넌트 렌더링
```

### Dashboard Layout
```text
┌──────────────────────────────────────────────────┐
│  🔴 Rescue Robot Mission Control    [SAFE MODE]  │
├──────────┬───────────────┬───────────────────────┤
│          │               │                       │
│ Mission  │  Terrain Map  │  Detection Feed       │
│ Panel    │  Visualization│  (Thermal/RGB/Audio)  │
│          │               │                       │
├──────────┼───────────────┴───────────────────────┤
│          │                                       │
│ SOP      │  Event Timeline                       │
│ Profile  │  (real-time event stream)              │
│          │                                       │
├──────────┴───────────────────────────────────────┤
│  Robot Status  │  Safety Controls  │  Quick Stats │
└──────────────────────────────────────────────────┘
```

### Features
- 미션 생성/승인/시작/완료/긴급정지 버튼
- 지형 분석 결과 시각화 (TerrainClass 색상 매핑)
- 센서 융합 탐지 결과 카드
- 이벤트 타임라인 (최신순)
- 안전 상태 표시 (NORMAL/CAUTION/SAFE_MODE/EMERGENCY)
- SOP 프로파일 선택 (산악/붕괴/터널)
- 반응형 레이아웃

### Completion Criteria
1. index.html을 브라우저에서 열면 대시보드 표시
2. API 호출로 미션 전체 흐름 시연 가능
3. Dark theme + glassmorphism + 애니메이션 적용
4. 모바일 반응형
