# 15 TODO — WebRTC Mock Integration

## Phase Reference
- Phase-7 WebRTC Integration (Mock stage)

## Prompt

Mock WebRTC DataChannel 기반으로 원격 관제 흐름을 구현해 주세요.

### Dependency Rule
```text
Service -> Config -> Types
Adapters -> Service -> Config -> Types
```

### Reference Docs
- `implementation_roadmap.md` Phase-7
- `interface.md` (IWebRTCTrackSender)
- `detailed_interface_schema.md`

### Create
```text
src/adapters/webrtc/mock_track_sender.py  — Mock video/audio track sender
src/service/remote_control_service.py     — Control command routing
tests/unit/service/test_remote_control_service.py
tests/contract/test_webrtc_contracts.py
```

### Features
- MockTrackSender implements IWebRTCTrackSender Protocol
- Track priority: Control > Thermal > RGB > Audio > PointCloud
- Control command routing: remote UI -> service -> robot controller
- Event feedback: robot events -> service -> remote UI
- Disconnection handling: queue events, retry on reconnect

### Required TC
- TC-WEBRTC-001: Mock track sender sends data
- TC-WEBRTC-002: Track priority ordering
- TC-WEBRTC-003: Control command roundtrip
- TC-WEBRTC-004: Disconnection queues events
- TC-WEBRTC-005: Reconnect replays queued events

### Completion Criteria
1. MockTrackSender implements IWebRTCTrackSender Protocol
2. Control commands have highest priority
3. Disconnection does not lose critical events
4. No real WebRTC or network dependency
