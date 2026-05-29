# 안전 및 현장 SOP

## 1. 목적

본 문서는 현장 운용 중 안전 관련 의사결정과 비상 절차를 정의한다.

---

## 2. Safety 우선순위

```text
Human Safety
    >
Robot Safety
    >
Mission Continuity
    >
Performance
```

---

## 3. Mission 시작 전 SOP

1. Battery, Sensor, Storage, Network 상태를 확인한다.
2. Thermal/RGB 영상 출력과 Pose/Map 표시를 확인한다.
3. Operator UI에서 탐색 임무를 생성하고 탐색 구역, 탐색 방법, SOP Profile을 지정한다.
4. SOP Profile이 제안한 제한 조건과 위험 경고를 확인한다.
5. Emergency Stop 경로를 점검한다.
6. Operator, Safety Officer, Mission Commander 역할을 확인한다.
7. Self Check와 Mission Draft 검증 통과 후 Mission Commander가 시작을 승인한다.

---

## 3.1 SOP Profile 기반 임무 설정

SOP Profile은 Mission 생성 시 설정 추천과 제한 조건을 제공한다.

| SOP Profile 예시 | 기본 탐색 방법 | 주요 제한 조건 |
|---|---|---|
| `mountain_missing_person` | `AREA_SWEEP` | Thermal 우선, 경사 제한, 장시간 배터리 정책 |
| `collapsed_structure` | `FRONTIER_EXPLORATION` | 협소 구간 감속, 잔해 위험 Alert |
| `tunnel_gas_risk` | `PERIMETER_SEARCH` | Gas DANGER 시 Stop/Retreat, 통신 단절 경고 강화 |

금지:

```text
SOP Profile → Mission Start
SOP Profile → ControlCommand
SOP Agent → Robot Controller
```

SOP Agent는 `MissionSetupRecommendation`만 생성하고, 최종 적용은 Mission Core 검증과 Mission Commander 승인 후 수행한다.

---

## 4. Emergency Stop SOP

Trigger:

- Operator Stop
- Collision Risk
- Gas Hazard DANGER
- Motor Failure
- Control Authority Violation

절차:

```text
Trigger
    ↓
Emergency Stop
    ↓
All Motion Stop
    ↓
Safety Officer Confirm
    ↓
Mission Commander Recovery Decision
```

---

## 5. 통신 단절 SOP

```text
DISCONNECTED
    ↓
Reconnect Attempt
    ↓
Local Autonomous Mode
    ↓
Critical Event Local Save
    ↓
Reconnect 후 Sync
```

운영 원칙:

- 원격 제어 불가 상태에서 무리한 이동을 금지한다.
- Local Navigation과 Obstacle Avoidance를 유지한다.
- Critical Event는 Local Storage에 우선 저장한다.

---

## 6. Gas Hazard SOP

| Level | 조치 |
|---|---|
| WARNING | Operator Alert, Mission Continue 가능 |
| DANGER | Robot Stop 또는 Retreat, Mission Re-evaluation |

---

## 7. Field Test 중단 조건

- Emergency Stop 실패
- Local Autonomous 전환 실패
- Critical Event Loss 발생
- 제어 권한 검증 실패
- Sensor/SLAM 장애로 Safe Mode 진입 실패
- 3D LiDAR 지형 분석이 `CLIFF_OR_DROP` 또는 `BLOCKED`를 감지했는데 정지/우회하지 못한 경우
- SearchMethod와 TerrainClass가 불일치하는데 주행이 계속되는 경우
- Safety Officer 또는 Mission Commander의 중단 결정

---

## 8. 완료 기준

1. SOP는 Field Test 전 모든 운영자가 숙지한다.
2. Emergency Stop 리허설을 수행한다.
3. 통신 단절과 복구 절차를 Simulation에서 검증한다.
4. 실제 Field Test 결과는 Operation Log에 기록한다.
