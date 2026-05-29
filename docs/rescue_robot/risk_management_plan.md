# 리스크 관리 계획서

## 1. 목적

본 문서는 시스템 개발, 통합, 시험, 현장 운영 중 발생 가능한 리스크와 대응 계획을 정의한다.

---

## 2. 리스크 등급

| 등급 | 기준 |
|---|---|
| High | Safety 또는 Mission 실패 가능 |
| Medium | 성능 저하 또는 일정 지연 가능 |
| Low | 국소 기능 영향 |

---

## 3. 리스크 등록부

| ID | 리스크 | 가능성 | 영향도 | 등급 | 대응 | Trigger | 담당 |
|---|---|---|---|---|---|---|---|
| R-001 | Emergency Stop 지연 | Low | High | High | P0 테스트, 독립 제어 경로 | Stop latency 증가 | Safety Officer |
| R-002 | AI OOM/CUDA Error | Medium | Medium | Medium | FPS 감소, AI 재시작, 영상 유지 | GPU memory 90% 이상 | AI Lead |
| R-003 | WebRTC 단절 | High | High | High | Reconnect, Local Autonomous | ICE disconnect | Communication Lead |
| R-004 | SLAM Drift | Medium | High | High | Drift Detection, Re-localization | drift score 초과 | Navigation Lead |
| R-005 | Storage Full | Medium | Medium | Medium | Low Priority 삭제, Critical 보존 | disk 85% 이상 | Platform Lead |
| R-006 | Sensor Failure | Medium | Medium | Medium | Fallback, Unknown Event | sensor heartbeat loss | Robot Lead |
| R-007 | AI 직접 제어 오동작 | Low | High | High | Protocol 차단, Test Gate | ControlCommand 생성 시도 | Safety Officer |
| R-008 | Lint/Type 미준수 누적 | Medium | Medium | Medium | CI Gate, PR 차단 | lint failure | Tech Lead |
| R-009 | Field 환경 편차 | High | Medium | Medium | Simulation 다양화, 단계적 Field Test | KPI 미달 | Test Lead |
| R-010 | 보안 인증 우회 | Low | High | High | Auth, ACL, Audit Log | unauthorized access | Security Lead |
| R-011 | 잘못된 탐색 구역 지정 | Medium | High | High | SearchArea Validation, Geofence 검증, Mission Commander 승인 | invalid area 또는 no-go 충돌 | Mission Commander |
| R-012 | 부적절한 탐색 방법 선택 | Medium | Medium | Medium | SearchMethod Policy, SOP Profile 추천, TC-MISSION-003 | area/method 조합 불일치 | System Architect |
| R-013 | SOP 설정의 직접 제어 오해 | Low | High | High | Recommendation only 계약, TC-MISSION-007, Audit Log | SOP가 Mission Start/ControlCommand 생성 시도 | Safety Officer |
| R-014 | 3D LiDAR 지형 분석 오분류 | Medium | High | High | fixed terrain fixture, TC-TERRAIN-002/003, conservative replan | traversability score 급변 | Navigation Lead |
| R-015 | 지형과 탐색 방법 불일치 | Medium | High | High | SearchMethod-Terrain Compatibility, TC-TERRAIN-004 | steep/drop terrain에 sweep 할당 | System Architect |

---

## 4. 리스크 대응 원칙

1. High 리스크는 Sprint 완료 전 잔여 위험을 명시한다.
2. Safety 관련 리스크는 기능 개발보다 우선한다.
3. Lint/Type Check 실패는 품질 리스크로 관리한다.
4. Field Test 리스크는 Simulation에서 먼저 재현한다.
5. 탐색 임무 생성 리스크는 `TC-MISSION-*`와 권한 검증으로 먼저 차단한다.
6. 지형 기반 주행 리스크는 `TC-TERRAIN-*`와 conservative replan 정책으로 먼저 차단한다.
7. 잔여 리스크는 Acceptance Report에 기록한다.
