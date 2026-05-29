# 함수 단위 테스트 계획

## 1. 목적

본 문서는 결정 로직과 경계 로직 중심의 함수 단위 테스트 대상을 정의한다.

함수 단위 테스트는 Windows `dev-windows-local` 환경에서 ROS Runtime 없이 수행한다.

---

## 2. 테스트 원칙

```text
Pure Function First
Deterministic Input
Deterministic Output
No ROS Runtime
No External I/O
```

테스트 대상 함수는 동일 입력에서 동일 출력을 보장해야 한다.

---

## 3. 결정 로직 함수 테스트 대상

| Test ID | 함수 역할 | 입력 | 기대 결과 |
|---|---|---|---|
| TC-FUNC-DEC-001 | Thermal 요구조자 판단 | thermal_temp, threshold | VictimCandidate 여부 |
| TC-FUNC-DEC-002 | RGB 보조 판단 | label, confidence | RGB candidate 여부 |
| TC-FUNC-DEC-003 | Audio help 판단 | keyword, confidence | SuspiciousEvent 여부 |
| TC-FUNC-DEC-004 | Multi Sensor Fusion | thermal/rgb/audio evidence | fusion_score, victim_detected |
| TC-FUNC-DEC-005 | Gas Hazard 판단 | gas_type, value, threshold | WARNING/DANGER/SAFE |
| TC-FUNC-DEC-006 | Locomotion Mode 결정 | slope, obstacle_height, traversable | WHEEL/OBSTACLE_CLIMB/SLOW_SAFE/STOP |
| TC-FUNC-DEC-007 | Emergency Stop 우선순위 | current_state, trigger | All Motion Stop |
| TC-FUNC-DEC-008 | Local Autonomous 진입 | webrtc, fiveg, disconnect_duration | local_autonomous_mode |
| TC-FUNC-DEC-009 | SOP 권고 제한 | context | Recommendation only |
| TC-FUNC-DEC-010 | 탐색 방법 추천/선택 판단 | area_type, risk_level, sop_profile | SearchMethod |
| TC-FUNC-DEC-011 | SOP 임무 설정 제한 판단 | sop_context, requested_action | Recommendation only |
| TC-FUNC-DEC-012 | 지형 기반 주행 정책 판단 | terrain_class, traversability_score, search_method | SearchDriveProfile |
| TC-FUNC-DEC-013 | 지형 기반 속도 제한 판단 | slope, roughness, step_height | speed_scale |

---

## 4. 경계 로직 함수 테스트 대상

| Test ID | 함수 역할 | 입력 | 기대 결과 |
|---|---|---|---|
| TC-FUNC-BND-001 | Event Priority 정렬 | event list | deterministic ordered events |
| TC-FUNC-BND-002 | State Transition Guard | state, event | allowed/blocked transition |
| TC-FUNC-BND-003 | Control Authority 검증 | command, role | allowed/denied |
| TC-FUNC-BND-004 | Storage Key 생성 | mission_id, robot_id, event_id | deterministic storage key |
| TC-FUNC-BND-005 | Retry Backoff 계산 | retry_count, policy | deterministic delay |
| TC-FUNC-BND-006 | Sync Queue 순서 결정 | queued events | priority + FIFO order |
| TC-FUNC-BND-007 | DataChannel Priority 결정 | message type | priority class |
| TC-FUNC-BND-008 | Fake ROS Envelope Mapper | fake envelope | Domain DTO |
| TC-FUNC-BND-009 | DTO Validation | payload | valid/invalid result |
| TC-FUNC-BND-010 | SearchArea Validation | area_type, coordinates | valid/invalid result |
| TC-FUNC-BND-011 | Mission Approval Guard | mission_state, role | activation allowed/blocked |
| TC-FUNC-BND-012 | SearchMissionRequest Validation | request payload | valid/invalid result |
| TC-FUNC-BND-013 | Search Grid 생성 | boundary, cell_size | deterministic grid cells |
| TC-FUNC-BND-014 | TerrainAnalysisResult Validation | terrain payload | valid/invalid result |
| TC-FUNC-BND-015 | SearchMethod-Terrain Compatibility | terrain_class, search_method | allowed/blocked |

---

## 5. 제외 대상

다음은 함수 단위 테스트 필수 대상이 아니다.

```text
단순 getter/setter
단순 pass-through wrapper
로그만 남기는 함수
프레임워크 lifecycle hook
실제 ROS Node 실행 함수
실제 DB 연결 함수
실제 WebRTC 연결 함수
```

이 대상은 Contract Test, Adapter Test, Integration Test에서 검증한다.

---

## 6. Fixture 기준

| Fixture | 기준 |
|---|---|
| Time | FakeClock 또는 고정 timestamp |
| Random | fixed seed |
| Sensor | fixed frame/value |
| Event ID | deterministic id |
| Storage | InMemoryRepository |
| ROS | FakeRosEnvelope |
| Network | FakePacket / MockDataChannel |
| Mission Setup | fixed SearchArea, fixed SOP Profile |
| Terrain | fixed PointCloud, fixed ElevationGrid, fixed TerrainAnalysisResult |

---

## 7. 완료 기준

1. `TC-FUNC-DEC-*`와 `TC-FUNC-BND-*`는 Windows 기본 테스트에 포함한다.
2. 모든 테스트는 ROS Runtime 없이 실행된다.
3. 모든 테스트는 외부 네트워크, 외부 DB, 실제 센서에 의존하지 않는다.
4. 동일 입력에서 동일 결과가 나와야 한다.
5. 실패 시 해당 로직은 Adapter/Integration 단계로 진행하지 않는다.
