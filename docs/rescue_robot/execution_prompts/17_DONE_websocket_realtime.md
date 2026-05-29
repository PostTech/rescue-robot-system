# 17 TODO — WebSocket Real-time Updates

## Phase
- Phase MVP-3: Real-time

## Prompt

WebSocket을 추가해서 대시보드에 실시간 업데이트를 보내 주세요.

### Create
```text
src/api/websocket_manager.py  — WebSocket connection manager
src/api/routes_ws.py          — /ws endpoint
src/web/js/websocket.js       — WebSocket 클라이언트
```

### WebSocket Events
| Event | Direction | Data |
|---|---|---|
| mission.created | Server → Client | mission draft |
| mission.approved | Server → Client | mission plan |
| mission.state_changed | Server → Client | new state |
| terrain.analyzed | Server → Client | terrain result |
| detection.result | Server → Client | victim decision |
| safety.changed | Server → Client | safety state |
| event.published | Server → Client | base event |

### Features
- 미션 상태 변경 시 대시보드 자동 업데이트
- 지형 분석 결과 실시간 반영
- 탐지 결과 실시간 카드 추가
- 이벤트 타임라인 자동 스크롤
- 안전 상태 변경 시 경고 애니메이션

### Completion Criteria
1. WebSocket 연결 시 실시간 이벤트 수신
2. API 호출 결과가 WebSocket으로도 전파
3. 연결 끊김 시 자동 재연결
