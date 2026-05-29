# Goal: React UI - Go Core Backend E2E Integration

> [!IMPORTANT]
> Before implementing, align with the root [Universal AI Guidelines](../../AGENT_GUIDELINES.md) and track progress in [task.md](./task.md).
현재 재난 구조용 사족로봇 관제 대시보드(React + TS)의 실시간 텔레메트리, 요구조자 탐지 데이터 및 임무 계획 생성 로직은 프론트엔드(`App.tsx`, `MissionSetupPanel.tsx`) 내부에서 로컬 `setTimeout` 및 임의의 Ticker Loop을 통해 모킹(Mock) 시뮬레이션되고 있습니다.

본 계획서는 **React UI 대시보드**를 **Go Core Backend(Port 8080)**의 실제 REST API 및 실시간 WebSocket 채널(`ws://localhost:8080/ws/telemetry`)과 물리적으로 결합하여, 실시간 데이터 영속성(PostgreSQL) 및 스트리밍 전송 채널을 작동시키는 최종 E2E 통합 마이그레이션을 목표로 합니다.

---

## User Review Required

> [!IMPORTANT]
> - **백엔드 포트 연결**: React UI는 브라우저 단에서 `localhost:8080`에 기동되는 Go Core Server와 REST/WS로 연동됩니다. 로컬 또는 다중 디바이스 기동 시 IP 및 포트 주소가 일치해야 합니다.
> - **시뮬레이션 가동의 지속**: UI 자체의 모의 Ticker Loop을 제거하고, 대신 백엔드로 실시간 텔레메트리를 송출할 수 있는 Python 시뮬레이터 클라이언트 스크립트를 연결하여 무결성을 증명합니다.

---

## Open Questions

> [!NOTE]
> - **인프라 연결**: 로컬 PostgreSQL과 MinIO 컨테이너가 `docker-compose.yml`을 통해 5432, 9000 포트에서 백엔드와 연동되어 작동하고 있는지 점검이 필요합니다.

---

## Proposed Changes

### [React UI Component & State Store]

React UI가 로컬에서 데이터를 모킹하는 대신, 실제 Go 백엔드 API와 통신하고 실시간 WebSocket 스트림을 청취하도록 개편합니다.

#### [MODIFY] [useStore.ts](file:///C:/Users/NB-BQ-346/.gemini/antigravity/scratch/AI_challenge/rescue-robot-system-main/react_ui/src/store/useStore.ts)
- Go Core 서버의 기본 주소(`http://localhost:8080` 및 `ws://localhost:8080`) 연결 설정을 추가합니다.
- `fetch` API를 사용하여 백엔드의 임무 생성(`/api/missions/draft`) 및 승인(`/api/missions/plan`) API를 호출하는 비동기 함수 `createDraftFromServer` 및 `approvePlanOnServer`를 구현합니다.
- WebSocket 연결 객체 및 연결 함수 `connectWebSocket`을 정의하여, 실시간 텔레메트리 및 사건 이벤트를 수신받았을 때 Zustand 스토어 상태를 실시간으로 업데이트하는 리스너 파이프라인을 구축합니다.

#### [MODIFY] [App.tsx](file:///C:/Users/NB-BQ-346/.gemini/antigravity/scratch/AI_challenge/rescue-robot-system-main/react_ui/src/App.tsx)
- 컴포넌트 마운트 시 `useStore`의 `connectWebSocket`을 호출하여 Go Core 서버와 실시간 커넥션을 수립합니다.
- 프론트엔드 자체의 로컬 mock Ticker Loop을 제거(또는 백엔드 미연결 시의 fallback으로 전환)하여 실제 백엔드 스트림으로부터 텔레메트리 데이터(로봇 자세, 배터리, Gas Accumulation)가 반응형으로 화면에 표시되도록 설정합니다.

#### [MODIFY] [MissionSetupPanel.tsx](file:///C:/Users/NB-BQ-346/.gemini/antigravity/scratch/AI_challenge/rescue-robot-system-main/react_ui/src/components/MissionSetupPanel.tsx)
- 기존의 `setTimeout` 로컬 mock 코드를 걷어내고, `useStore`에 추가된 실제 백엔드 연동 액션을 바인딩합니다.
- 임무 계획 요청 및 승인 시 Loading 스피너 애니메이션과 비동기 처리 트랜지션을 깔끔하게 연출합니다.

---

## Verification Plan

### Automated & Manual Tests

1. **인프라 및 서버 가동**:
   - `docker compose up -d`를 수행하여 PostgreSQL 및 MinIO 기동을 확인합니다.
   - `cd go_core; go run cmd/server/main.go`를 통해 Go 백엔드 서버를 포트 8080에서 가동합니다.
   - `cd react_ui; npm run dev`를 실행하여 프론트엔드 대시보드를 구동합니다.

2. **임무 수립 E2E 검증**:
   - React UI에서 임무 구역 좌표 및 방식을 기입하고 "GENERATE MISSION DRAFT" 버튼을 클릭합니다.
   - 백엔드에 드래프트가 POST 요청되고 PostgreSQL DB `drafts` 테이블에 영속 저장된 후, 검증된 SOP 규격과 함께 화면에 표시되는지 확인합니다.
   - "COMMIT PLAN TO DATABASE" 버튼을 클릭하여 Commander Lee 명의로 승인된 최종 계획이 백엔드 PostgreSQL `plans` 테이블에 무사히 Commit되는지 트랜잭션을 검증합니다.

3. **실시간 WebSocket 텔레메트리 연동 테스트**:
   - 별도의 데이터 송출 시뮬레이터(예: 백엔드로 임의 텔레메트리/이벤트를 쏘아 올릴 파이썬 클라이언트 또는 백엔드 API 테스트)를 구동하여, 로봇의 x, y 좌표 이동 및 가스 hazard 수치가 React UI의 Isometric topographic radar 및 텔레메트리 대시보드 게이지에 Neon Glow 실시간 애니메이션으로 박동하는지 점검합니다.
