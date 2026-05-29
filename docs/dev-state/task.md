# Task Checklist — Rescue Robot Stack Migration

> [!IMPORTANT]
> Before modifying any files, make sure to align with the root [Universal AI Guidelines](../../AGENT_GUIDELINES.md).
> Refer to the current design in [implementation_plan.md](./implementation_plan.md) and results in [walkthrough.md](./walkthrough.md).
- [x] Step 1: Go Setup & Domain Types
  - [x] Initialize Go module `go_core` in `go_core/`
  - [x] Implement pure domain types in `go_core/internal/domain/` (Terrain, Mission, SOP, Fusion, Events)
- [x] Step 2: Go Core Services & Unit Tests
  - [x] Port `decide_drive_profile()` and `search_drive_policy` to Go
  - [x] Port `FusionLogic` and victim detection logic to Go
  - [x] Port `SafetyManager` and SOP recommending profiles to Go
  - [x] Write and run Go unit tests with 100% success rate
- [x] Step 3: Storage Adapters (Postgres + MinIO)
  - [x] Implement GORM PostgreSQL repositories for missions and events
  - [x] Implement MinIO adapter with Presigned URL generation for video/audio streams
- [x] Step 4: React UI Setup
  - [x] Scaffold React + TS frontend using Vite in `react_ui/`
  - [x] Implement Zustand state stores and WebRTC/WebSocket telemetry client
  - [x] Create UI components (Mission Setup, SOP panel, WebGL 3D map, Alerts dashboard)
- [x] Step 5: Integration & Verification
  - [x] Connect Go Core, Postgres, MinIO, and React UI in a full E2E flow
  - [x] Conduct E2E scenario testing and fault recovery validation
- [x] Step 6: Direct Go-React E2E Integration
  - [x] Implement Go Backend connection (REST API) inside Zustand store (`useStore.ts`)
  - [x] Replace React local mock simulation loop with real WebSocket listener (`ws://localhost:8080/ws/telemetry`)
  - [x] Adapt `MissionSetupPanel.tsx` to communicate directly with Go REST endpoints for draft creation and confirmation
  - [x] Run E2E telemetry validation using backend database transactions
