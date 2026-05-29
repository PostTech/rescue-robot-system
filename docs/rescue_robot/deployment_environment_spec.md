# 배포 환경 명세서

## 1. 목적

본 문서는 Windows 기본 개발 환경과 향후 Linux/ROS 실행 환경의 실행 조건, 컨테이너, 네트워크, 로그 기준을 정의한다.

---

## 2. 환경 프로파일

| Profile | OS | 목적 | ROS Runtime |
|---|---|---|---|
| `dev-windows-local` | Windows | 기본 개발, Lint, Type Check, Unit/Contract/Layer/Module Test | 실행하지 않음 |
| `target-linux-ros` | Linux/Ubuntu | ROS2, 센서, 로봇 제어, Simulation, Field Test | 실행함 |

기본 프로파일은 `dev-windows-local`이다.

---

## 3. Windows 개발 환경 구성

| 구성 | 권장 기준 |
|---|---|
| OS | Windows |
| Shell | PowerShell |
| Runtime | Python 3.11 이상 |
| Middleware | ROS2 Runtime 미실행 |
| Test Scope | Unit, Contract, Layer, Module Boundary, Mission Creation, Terrain Driven Navigation |
| Adapter | Mock/Fake Adapter |
| Storage | Local test storage 또는 Mock repository |

Windows 기본 환경에서는 `rclpy`, ROS Node, 실제 ROS Topic Publish/Subscribe를 실행하지 않는다.

---

## 4. Robot Side Linux/ROS 구성

| 구성 | 권장 기준 |
|---|---|
| OS | Ubuntu LTS 기반 |
| Runtime | Python 3.11 이상 |
| Middleware | ROS2 |
| GPU | TensorRT/AI Inference 가능 GPU |
| Network | 5G 또는 Mesh + WebRTC |
| Storage | Local Event/Media Buffer |
| Sensor | Thermal, RGB, LiDAR, IMU, Gas, Microphone |

---

## 5. Control Center 구성

| 구성 | 권장 기준 |
|---|---|
| Runtime | Python 3.11 이상 |
| UI | Mission UI |
| WebRTC | Receiver / Signaling |
| Storage | DB + Object Storage |
| AI/SOP | Recommendation Service |
| Monitoring | Metrics + Alert |

---

## 6. Container 구성

| Container | 역할 | Health Check |
|---|---|---|
| `detector_container` | Thermal/RGB/Audio Detection | inference latency, GPU memory |
| `slam_container` | SLAM/Localization | pose update rate |
| `navigation_container` | Path Planning/Locomotion | path publish status |
| `webrtc_container` | Track/DataChannel | ICE state, bitrate |
| `storage_container` | Event/Media Save/Sync | disk usage, sync queue |
| `mission_core_container` | State Machine/Event | event queue lag |

---

## 7. 네트워크 포트 기준

| 구분 | 용도 |
|---|---|
| Signaling | WebRTC session negotiation |
| Media | WebRTC RTP/SRTP |
| DataChannel | Control/Event/Status |
| Monitoring | Metrics scrape/export |
| Storage | DB/Object Storage 접근 |

실제 포트 번호는 보안 정책과 운영 환경 확정 후 별도 배포 설정에 기록한다.

---

## 8. 로그 경로 기준

| 로그 | 내용 |
|---|---|
| Mission Log | mission state, operator decision, mission creation/approval |
| Terrain Log | terrain_class, traversability_score, search_drive_profile |
| Event Log | BaseEvent stream |
| Error Log | exception, failure, restart |
| Recovery Log | reconnect, local autonomous, sync |
| Performance Log | FPS, latency, GPU, CPU |
| Security Log | auth, access, control command audit |

---

## 9. 배포 완료 기준

1. Windows `dev-windows-local` 테스트가 ROS Runtime 없이 통과한다.
2. Linux/ROS 전환은 `target-linux-ros` 프로파일에서만 수행한다.
3. 모든 컨테이너 Health Check가 통과한다.
4. Lint/Type/Test Gate가 통과한 빌드만 배포한다.
5. Rollback 가능한 이전 Stable Version을 보존한다.
6. Field Test 전 Security와 Safety Check를 완료한다.
