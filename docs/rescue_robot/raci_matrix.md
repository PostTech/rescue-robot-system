# RACI 역할 책임 매트릭스

## 1. 목적

본 문서는 개발, 시험, 운영 과정의 역할과 책임을 명확히 한다.

---

## 2. RACI 정의

| 약어 | 의미 |
|---|---|
| R | Responsible, 실행 책임 |
| A | Accountable, 최종 승인 |
| C | Consulted, 검토/자문 |
| I | Informed, 공유 대상 |

---

## 3. 역할

| 역할 | 설명 |
|---|---|
| Product Owner | 요구사항 및 범위 승인 |
| System Architect | 아키텍처 및 Interface 승인 |
| Tech Lead | 구현 품질 및 Lint Gate 책임 |
| AI Lead | Detector/Fusion/SOP Agent 책임 |
| Navigation Lead | SLAM/Navigation/Locomotion 책임 |
| Platform Lead | ROS2/WebRTC/Storage/Deployment 책임 |
| Test Lead | Test Harness, Simulation, Field Test 책임 |
| Safety Officer | Safety Gate 및 Emergency 절차 승인 |
| Security Lead | 인증, 권한, 감사, 보안 점검 책임 |
| Mission Commander | 현장 임무 최종 결정 |

---

## 4. RACI Matrix

| 작업 | PO | Architect | Tech | AI | Nav | Platform | Test | Safety | Security | Mission |
|---|---|---|---|---|---|---|---|---|---|---|
| 요구사항 승인 | A | C | C | C | C | C | C | C | C | I |
| Interface Baseline | C | A | R | C | C | C | C | C | I | I |
| Lint/CI Gate | I | C | A/R | C | C | C | C | I | C | I |
| Detector 구현 | I | C | C | A/R | I | I | C | C | I | I |
| SLAM/Navigation 구현 | I | C | C | I | A/R | C | C | C | I | I |
| WebRTC/Storage 구현 | I | C | C | I | I | A/R | C | C | C | I |
| 탐색 임무 생성 기능 | C | A | R | C | C | R | C | C | C | C |
| SOP 기반 임무 설정 | C | C | R | A/R | C | C | C | C | C | C |
| Mission 생성 승인 | I | C | I | C | C | I | C | C | I | A/R |
| Test Harness | I | C | C | C | C | C | A/R | C | I | I |
| Safety 검증 | I | C | C | C | C | C | R | A | C | C |
| Security 검증 | I | C | C | I | I | R | C | C | A | I |
| Field Test | I | C | I | C | C | C | R | A | C | A |
| Acceptance | A | C | C | C | C | C | R | A | C | A |

---

## 5. 운영 원칙

- Safety Officer와 Mission Commander는 현장 중단 권한을 가진다.
- Lint/Type Gate 예외는 Tech Lead 승인 없이는 허용하지 않는다.
- AI/SOP 권고는 Mission Commander 또는 Operator 승인 후에만 임무 결정으로 반영한다.
- 탐색 임무는 Operator가 생성할 수 있으나 Mission Commander 승인 전에는 활성화하지 않는다.
- SOP 기반 임무 설정은 권고와 제한 조건만 제공하며 직접 Mission Start를 수행하지 않는다.
