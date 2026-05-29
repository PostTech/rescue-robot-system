# ROS 기반 경량 계층화 계획

## 1. 목적

본 문서는 ROS2 기반 구현에서 과도한 계층화를 피하면서도 Business Logic 독립성, 테스트 가능성, 장애 격리를 유지하기 위한 경량 계층화 기준을 정의한다.

---

## 2. 핵심 결론

ROS2는 시스템 중심 아키텍처가 아니라 내부 통신 Adapter로 사용한다.

```text
Types
    ↓
Config
    ↓
Service
    ↓
UI
```

ROS는 Service 바깥의 Runtime Adapter이며, 위 코드 의존성 순서를 변경할 수 없다.

```text
Service
    ↓ Protocol
ROS Adapter
    ↓
ROS Topic / Node
```

즉, ROS Node와 Topic은 외부 경계이며, 핵심 판단 로직은 ROS Message 타입과 ROS Runtime에 직접 의존하지 않는다.

현재 Windows 기본 테스트에서는 ROS Topic / Node 계층을 실행하지 않는다.

---

## 3. 계층 정의

| 계층 | 책임 | 허용 의존성 | 금지 의존성 |
|---|---|---|---|
| Types | DTO, Enum, Value Object, Protocol 입출력 타입 | Python dataclass, Enum, typing | Config, Service, UI, ROS2, WebRTC, DB, Robot SDK |
| Config | Runtime Profile, SOP Profile, Threshold, Policy 설정 | Types | Service, UI, Adapter Runtime, ROS Node |
| Service | Event 처리, 상태 전이, Use Case, Mission/Navigation 판단 | Types, Config, Protocol | UI, ROS2 Message 직접 처리, DB Driver 직접 접근 |
| UI | Operator 입력, ViewModel 표시, 승인 요청 | Types, Config, Service Interface | DB Driver, ROS Runtime, Robot SDK 직접 접근 |
| ROS Adapter | ROS Topic 송수신, Message 변환 | Types, Config, Service Protocol, ROS2 | Service 규칙 구현, UI 호출 |
| ROS Topic / Node | Runtime 통신 | ROS2 Runtime | Business Logic |

---

## 4. 의존성 규칙

허용:

```text
Types → Config → Service → UI  # 계층 순서
UI → Service/Config/Types       # import 허용
Service → Config/Types          # import 허용
Config → Types                  # import 허용
ROS Node → ROS Adapter → Service Protocol → Types
```

금지:

```text
Types → Config/Service/UI
Config → Service/UI
Service → UI
Types/Config/Service → ROS Message 직접 사용
Service → rclpy
Service → DB Driver
UI → ROS Runtime
UI → DB Driver
UI → Robot SDK
```

---

## 5. ROS Adapter 책임

ROS Adapter는 다음만 수행한다.

- ROS Topic Subscribe/Publish
- ROS Message ↔ Domain DTO 변환
- QoS 설정
- Namespace 적용
- Topic 오류와 Timeout을 Event로 변환
- Application Service 호출

ROS Adapter는 다음을 수행하지 않는다.

- 요구조자 판단
- Gas Hazard 판단
- Mission State 결정
- SOP Recommendation 생성
- Storage 정책 결정
- WebRTC 우선순위 결정

---

## 6. Client 모듈별 적용

| Client | ROS 계층화 적용 |
|---|---|
| Client-1 ROS2/WebRTC Bridge | ROS Topic을 DataChannel/Track 계약으로 변환한다. Mission 판단은 하지 않는다. |
| Client-2 Detection | Detection 결과를 Domain DTO로 만든 뒤 ROS Adapter가 `/perception/*` Topic으로 발행한다. |
| Client-3 SLAM/Navigation/Control | SLAM/Navigation 결과를 Domain DTO로 만든 뒤 ROS Adapter가 Pose/Path/Control Topic과 연결한다. |

---

## 7. Server 모듈별 적용

| Server | ROS 계층화 적용 |
|---|---|
| Server-1 Mission Core | ROS에 직접 의존하지 않고 WebRTC/Event Contract로 수신한 Domain Event만 처리한다. |
| Server-2 UI | ROS Topic을 직접 구독하지 않고 Mission Core/ViewModel Interface를 통해 상태를 받는다. |
| Server-3 Storage / DB | ROS Message를 저장하지 않고 Event/Media/Mission DTO만 저장한다. |
| Server-4 AI Agent / SOP | ROS Message를 입력으로 받지 않고 Mission Context DTO만 사용한다. |

---

## 8. Python 패키지 구조 권장

```text
src/
    types/
        dto.py
        events.py
        enums.py
        protocols.py
    config/
        profiles.py
        thresholds.py
        sop_profiles.py
    service/
        mission_service.py
        state_machine.py
        failover_service.py
        terrain_service.py
        search_drive_policy.py
    ui/
        mission_setup_view.py
        status_view_model.py
    adapters/
        ros/
            topic_gateway.py
            message_mapper.py
            qos.py
        webrtc/
            track_sender.py
            data_channel.py
        storage/
            event_repository.py
    tests/
        unit/
        contract/
        integration/
```

---

## 9. 테스트 기준

기본 테스트 프로파일은 Windows `dev-windows-local`이며, ROS Runtime까지 진행하지 않는다.

| Test ID | 목적 | 기준 |
|---|---|---|
| TC-LAYER-001 | Domain 독립성 | `domain/`에서 `rclpy`, ROS Message import 없음 |
| TC-LAYER-002 | Application 독립성 | Application Service가 ROS Message를 직접 받지 않음 |
| TC-LAYER-003 | Adapter Contract 변환 | Fake ROS Envelope ↔ Domain DTO 변환 테스트 통과 |
| TC-LAYER-004 | Mock 가능성 | ROS Runtime 없이 Business Logic Unit Test 실행 |
| TC-LAYER-005 | 장애 격리 | Mock Topic 장애가 Domain Failure로 직접 전파되지 않고 Event로 변환 |
| TC-DEP-001 | Types 독립성 | `types/`에서 Config/Service/UI import 없음 |
| TC-DEP-002 | Config 독립성 | `config/`에서 Service/UI import 없음 |
| TC-DEP-003 | Service 독립성 | `service/`에서 UI import 없음 |
| TC-DEP-004 | UI Runtime 차단 | `ui/`에서 DB Driver/ROS Runtime/Robot SDK 직접 import 없음 |
| TC-DEP-005 | 순환 의존성 차단 | Types/Config/Service/UI cycle 없음 |

계층별 TDD와 Test Harness 매핑은 `layer_tdd_harness_matrix.md`를 기준으로 한다.

---

## 10. 완료 기준

1. Types, Config, Service는 ROS Runtime 없이 테스트 가능하다.
2. Windows 기본 테스트는 ROS Topic / Node / rclpy 실행 없이 완료된다.
3. ROS Message 타입은 `adapters/ros` 밖으로 새지 않는다.
4. 모든 ROS Topic 송수신은 Linux/ROS 프로파일에서 `IRosTopicGateway` 또는 ROS Adapter를 통해 수행한다.
5. Client/Server 모듈은 Interface Matrix의 직접 의존 금지 규칙을 만족한다.
6. `Types -> Config -> Service -> UI` 의존성 방향을 만족한다.
7. `TC-LAYER-*`, `TC-DEP-*`, `TC-MOD-*`, `TC-LINT-*` 테스트를 통과한다.
