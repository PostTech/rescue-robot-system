# 보안 계획서

## 1. 목적

본 문서는 원격 관제, 로봇 제어, 데이터 저장 과정의 인증, 권한, 암호화, 감사 기준을 정의한다.

---

## 2. 보안 원칙

- 인증되지 않은 사용자는 관제와 제어를 수행할 수 없다.
- Operator 권한과 Observer 권한을 분리한다.
- Mission 생성 권한과 Mission 시작 승인 권한을 분리한다.
- 모든 Control Command는 감사 로그에 기록한다.
- 모든 Mission 생성, 구역 변경, 방법 선택, 승인 요청은 감사 로그에 기록한다.
- AI/SOP Agent는 제어 권한을 갖지 않는다.
- 비상 상황에서도 최소한의 접근 통제는 유지한다.

---

## 3. 권한 모델

| Role | 권한 |
|---|---|
| Observer | 영상/상태 조회 |
| Operator | 승인된 원격 제어, 탐색 임무 생성 요청 |
| Safety Officer | Emergency Stop, Mission Pause |
| Mission Commander | Mission Start/Stop/Resume 승인 |
| Admin | 사용자/권한/시스템 설정 |
| SOP Agent | Recommendation 생성만 가능 |

---

## 4. 보호 대상

| 대상 | 보호 방식 |
|---|---|
| WebRTC Media | SRTP |
| Signaling | TLS |
| DataChannel Control | 인증된 세션 + command audit |
| Mission Draft/Plan | role-based access + mission audit |
| Storage | 접근 권한, 암호화, 백업 |
| Credentials | Rotation, 만료 정책 |
| Logs | 변조 방지, 접근 통제 |

---

## 5. 보안 테스트

| Test ID | 목적 | 기준 |
|---|---|---|
| SEC-001 | 미인증 접속 차단 | Control/UI 접근 실패 |
| SEC-002 | 권한 없는 제어 차단 | Observer command 거부 |
| SEC-003 | AI 직접 제어 차단 | SOP Agent ControlCommand 생성 불가 |
| SEC-004 | 감사 로그 기록 | 모든 ControlCommand 기록 |
| SEC-005 | Credential 만료 | 만료 토큰 거부 |
| SEC-006 | Dependency 취약점 | High 취약점 배포 차단 |
| SEC-007 | Mission 생성 권한 검증 | Operator 이상만 `SearchMissionRequest` 생성 가능 |
| SEC-008 | Mission 승인 권한 검증 | Mission Commander만 Mission Plan 활성화 가능 |

---

## 6. 완료 기준

1. Control 권한은 Role 기반으로 제한된다.
2. 모든 제어 명령은 operator_id, timestamp, command_id와 함께 기록된다.
3. Mission 생성, 구역 변경, 방법 선택, 승인 요청은 operator_id, timestamp, mission_id와 함께 기록된다.
4. 보안 High 취약점은 Release Candidate에 포함하지 않는다.
5. Field Test 전 접근 계정과 Credential Rotation 계획을 확정한다.
