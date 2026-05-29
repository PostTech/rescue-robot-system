# 🤖 UNIVERSAL AI CODING AGENT GUIDELINES (ROOT POINTER)

> **CRITICAL INSTRUCTION FOR ALL INCOMING AI AGENTS (Claude, Codex, Gemini/Antigravity, GPT, Cursor)**
>
> You are an autonomous AI coding agent collaborating on this project. Before writing any code, running commands, or modifying files, you **MUST** read and strictly align with this root guidelines file. 
> 
> Follow the hierarchical pointers below to absorb the current workspace state and architectural constraints.

---

## 🗺️ 1. Project-wide Hierarchical Navigation Map

Use these relative links to lazily load and explore the current state of the workspace. Only read what is necessary for your current task to conserve your context window:

```text
Root Guidelines (AGENT_GUIDELINES.md)
  │
  ├── 🧭 Dev State (Current checklist, plans, and achievements)
  │     ├── [task.md](./docs/dev-state/task.md) — Active checklist of todo tasks (Read first!)
  │     ├── [implementation_plan.md](./docs/dev-state/implementation_plan.md) — Active design plan under development
  │     └── [walkthrough.md](./docs/dev-state/walkthrough.md) — Recent development results and modifications
  │
  └── 🏛️ Architectural Baselines (Core system rules)
        ├── [project_master_plan.md](./docs/rescue_robot/project_master_plan.md) — System master architecture plan
        └── [implementation_roadmap.md](./docs/rescue_robot/implementation_roadmap.md) — 12-Phase system roadmaps
```

---

## 🔄 2. Universal State Sync Loop

When a developer pulls from Git, you must synchronize with the active tasks by following this exact process:
1. **Read Active Tasks**: Open and parse [task.md](./docs/dev-state/task.md).
   - Identify the step marked as in-progress (`[/]`) or the next uncompleted step (`[ ]`).
2. **Review Design Details**: Open [implementation_plan.md](./docs/dev-state/implementation_plan.md) to comprehend the technical proposed changes and verification commands for the current task.
3. **Execute & Verify (Feedback Loop)**:
   - Make code edits according to the plan.
   - Run the exact verification shell commands specified under `## Verification Plan` in [implementation_plan.md](./docs/dev-state/implementation_plan.md).
   - Parse the raw terminal feedback (Stdout/Stderr) to fix any syntax or test failures.
4. **Update Status**: 
   - Mark the completed task as `[x]` in [task.md](./docs/dev-state/task.md).
   - Document your changes and validation results in [walkthrough.md](./docs/dev-state/walkthrough.md).

---

## 🏛️ 3. Absolute Architectural Boundary Guards

You must never violate these four core system boundaries. If you modify any code, ensure these rules are preserved:

### Guard 3.1: Ports & Adapters (Hexagonal Decoupling)
- Keep high-level application services completely decoupled from infrastructure databases (PostgreSQL/GORM) and object storages (MinIO).
- Go Core services interact with the DB only through strict interfaces defined under `internal/ports/`.

### Guard 3.2: ROS2 Adapter Decoupling (Robot Side)
- ROS2 Node and topic operations must be completely encapsulated inside the **ROS Adapter** boundary.
- Do not import `rclpy` or use raw ROS messages in the core service/domain layers. Map them to domain-pure DTOs (`Pose3D`, `TerrainAnalysisResult`).

### Guard 3.3: WebRTC / Direct Media Streaming
- High-bandwidth video frames (FLIR Thermal, RGB) must **NEVER** be pushed to ROS2 topics.
- Stream them directly over WebRTC tracks, or upload them to MinIO and distribute secure Presigned URLs to the frontend.

### Guard 3.4: Real-time WebSockets & Standby fallback
- The React UI dashboard Zustand store ([useStore.ts](./react_ui/src/store/useStore.ts)) must support a dual-mode:
  - **Online**: Bind directly to Go server WebSockets (`ws://localhost:8080/ws/telemetry`).
  - **Offline**: Run a local mock simulation loop in [App.tsx](./react_ui/src/App.tsx) when WebSocket is disconnected, ensuring interactive visual radar continuity. Mute the simulation instantly when the Go server goes online.
