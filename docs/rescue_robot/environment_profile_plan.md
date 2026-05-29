# 환경 프로파일 및 OS 전환 계획

## 1. 목적

본 문서는 현재 Windows 기반 작업 환경을 기본 개발 환경으로 정의하고, 향후 Linux 기반 ROS2 실행 환경으로 전환할 수 있도록 환경 프로파일과 테스트 범위를 정의한다.

---

## 2. 기본 원칙

```text
현재 기본값 = dev-windows-local
향후 전환값 = target-linux-ros
```

Windows 환경에서는 Domain, Application, Interface, Mock Adapter, Test Harness까지만 검증한다.

Linux 환경에서는 ROS2 Runtime, ROS Node, 실제 Topic, 센서/로봇 Runtime 통합을 검증한다.

---

## 3. 환경 프로파일

| Profile | OS | 목적 | 포함 | 제외 |
|---|---|---|---|---|
| `dev-windows-local` | Windows | 기본 개발, 문서, 순수 Python 테스트 | Domain, Application, Interface, Mock/Fake, Layer Test, Module Boundary Test, Mission Creation Test, Terrain Driven Navigation Test | ROS Runtime, `rclpy`, 실제 ROS Topic/Node, 센서 HW |
| `target-linux-ros` | Linux/Ubuntu | ROS2 및 실제 Runtime 통합 | ROS2, `rclpy`, ROS Node/Topic, Container, Sensor/HW, Field/Simulation | Windows-only path, Mock-only 제한 |

---

## 4. 테스트 범위

### 4.1 Windows 기본 테스트 범위

Windows에서는 ROS단까지 진행하지 않는다.

허용 테스트:

```text
TC-LINT-*
TC-LAYER-001
TC-LAYER-002
TC-LAYER-003  # Fake Envelope 기반
TC-LAYER-004
TC-LAYER-005  # Mock Timeout 기반
TC-DEP-*
TC-UNIT-*
TC-IF-*
TC-MOD-*
TC-MISSION-*
TC-TERRAIN-*
TC-SAFE-*  # Mock 기반
TC-COMM-*  # Mock 기반
```

제외 테스트:

```text
ROS Runtime Test
rclpy Import Test
Real ROS Topic Publish/Subscribe
Real ROS Node Launch
Sensor/HW Integration
Field Test
```

### 4.2 Linux/ROS 전환 후 테스트 범위

Linux/ROS 환경에서만 다음을 수행한다.

```text
ROS Node Launch
ROS Topic Publish/Subscribe
QoS Runtime Test
Sensor Driver Integration
Robot Controller Runtime Test
Simulation / Field Test
```

---

## 5. 프로파일 스위칭 기준

구현 시 환경 선택은 명시적 프로파일로 수행한다.

```text
RUNTIME_PROFILE=dev-windows-local
RUNTIME_PROFILE=target-linux-ros
```

권장 구조:

```text
config/
    profiles/
        dev-windows-local.yaml
        target-linux-ros.yaml
```

Adapter 선택 기준:

| Profile | Adapter |
|---|---|
| `dev-windows-local` | MockRosTopicGateway, FakeRosEnvelope, MockSensor, MockRobotController |
| `target-linux-ros` | RosTopicGateway, rclpy Node, Real Sensor Adapter, Real RobotControllerAdapter |

---

## 6. Windows 명령 기준

Windows 기본 검증 명령은 PowerShell 기준으로 정의한다.

```text
$env:RUNTIME_PROFILE = "dev-windows-local"
ruff check .
ruff format --check .
mypy src tests
pytest tests/unit tests/contract tests/layer tests/dependency tests/module_boundary tests/mission_creation tests/terrain
```

주의:

```text
Windows 기본 테스트에서 rclpy, ROS Node, ROS Topic Runtime을 실행하지 않는다.
```

---

## 7. Linux 전환 조건

Linux/ROS 환경으로 전환하기 전 다음을 만족해야 한다.

1. Windows 기본 테스트가 통과한다.
2. Domain/Application 계층에 ROS 의존성이 없다.
3. Interface Contract Test가 통과한다.
4. Module Boundary Test가 통과한다.
5. Dependency Direction Test가 통과한다.
6. Mission Creation Test가 통과한다.
7. Terrain Driven Navigation Test가 통과한다.
8. Mock 기반 Safety/Fallback 테스트가 통과한다.

---

## 8. 완료 기준

1. Windows에서는 ROS Runtime 없이 개발과 검증을 수행할 수 있다.
2. Linux 전환은 명시 프로파일 변경으로 수행한다.
3. ROS 관련 실제 Runtime 검증은 `target-linux-ros`에서만 수행한다.
4. 기본 CI/Test Gate는 ROS단까지 진행하지 않는다.
