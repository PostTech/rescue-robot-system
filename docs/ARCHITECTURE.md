# 아키텍처 디렉토리 계층 및 매핑 (ARCHITECTURE.md)

## 1. 목적

본 문서는 재난 구조용 바퀴형 사족로봇 시스템 관제 센터의 현대화된 분산 기술 아키텍처와 물리적 디렉토리 구조 간의 매핑을 규정한다.

구조적으로 기존의 Python 모노리스에서 **Go (Server Core), React + TS (Control Dashboard), PostgreSQL (Database), MinIO (Object Storage)** 분산 구조로 전환하면서, 핵심 도메인이 물리 외부 기술(DB 드라이버, S3 SDK, 네트워크 프레임워크)에 오염되는 것을 차단하기 위해 수립된 **도메인 주도 아키텍처 규격**과 **의존성 고정 규칙**을 정의한다.

---

## 2. 현대화된 디렉토리 구조 및 계층 매핑

```text
c:\Users\cosmo\AI_challange\
│
├── go_core/                         # [Go Server Core 및 백엔드]
│   ├── cmd/
│   │   └── server/main.go           # [API 진입점] Gin API 라우팅, CORS, WebSockets 오케스트레이션
│   ├── internal/
│   │   ├── domain/                  # [계층 1] Domain (외부 의존성 0% 순수 Go 도메인 타입 및 구조체)
│   │   │   ├── types.go             # TerrainClass, SearchDriveProfile, SearchMissionPlan
│   │   │   ├── perception.go        # SensorType, LocomotionMode
│   │   │   ├── detector.go          # Victim 정보
│   │   │   └── events.go            # BaseEvent, EventPriority, EventType
│   │   │
│   │   ├── config/                  # [계층 2] Config (임계치 및 정적 안전 기준값 정의)
│   │   │   └── thresholds.go        # 경사도/지형별 주행 안전 임계치
│   │   │
│   │   ├── service/                 # [계층 3] Service (핵심 비즈니스 로직 및 TDD 단위 테스트)
│   │   │   ├── search_drive_policy.go# 지형별 바퀴 제어 속도 및 험지 극복 제어 로직
│   │   │   ├── fusion_logic.go      # Thermal > RGB > Audio 요구조자 판정 우선순위 엔진
│   │   │   ├── safety_manager.go    # 위험 가스 및 긴급 비상 제어 오케스트레이터
│   │   │   └── core_logic_test.go   # 도메인 논리 무결성을 검증하는 100% 그린 패스 TDD 테스트
│   │   │
│   │   ├── ports/                   # [계층 4] Ports (리포지토리 및 스토리지 추상 인터페이스 정의)
│   │   │   ├── repositories.go      # IMissionRepository, IEventRepository 포트
│   │   │   └── storage.go           # IStorageAdapter 포트 (오브젝트 스토리지 추상화)
│   │   │
│   │   └── adapters/                # [계층 5] Adapters (구체 데이터베이스 및 파일 드라이버)
│   │       ├── postgres/            # GORM PostgreSQL 기반 Draft, Plan, Event 리포지토리 구현
│   │       └── storage/             # minio-go/v7 SDK 기반 S3 버킷 및 Presigned URL 어댑터 구현
│   │
│   ├── go.mod                       # Go 모듈 관리
│   └── go.sum
│
├── react_ui/                        # [React + TypeScript 모던 관제 대시보드]
│   ├── src/
│   │   ├── store/
│   │   │   └── useStore.ts          # [Zustand 전역 상태] 실시간 WebSocket 텔레메트리 반응형 동기화 스토어
│   │   ├── components/              # [UI 컴포넌트]
│   │   │   ├── TelemetryDashboard.tsx# 배터리, 통신, 가스 누출 텔레메트리 게이지 위젯
│   │   │   ├── MissionSetupPanel.tsx# 안전 조건 가드가 탑재된 임무 드래프트 및 최종 승인 제어 패널
│   │   │   ├── SOPPanel.tsx         # 발견 요구조자 대장 및 사건 실시간 로그 타임라인
│   │   │   └── Terrain3DViewer.tsx  # HTML5 Canvas 기반 Isometric Topographic 3D/2.5D 레이더 뷰어
│   │   ├── index.css                # 다크 모드 글래스모피즘 및 네온 경보 애니메이션 CSS
│   │   └── main.tsx                 # React 엔트리 마운트 포인트
│   ├── tsconfig.json                # TypeScript 엄격 검증 설정
│   └── vite.config.ts               # Vite 포트 3000번 개발 서버 빌더
│
├── docker-compose.yml               # PostgreSQL + MinIO 자동 기동 인프라 정의서
└── .env.example                     # 다중 기기 개발 연속성 보장 환경 설정 변수
```

---

## 3. 백엔드 의존성 역전 원칙 (Dependency Inversion Principle)

Go Server Core는 클린 아키텍처 및 헥사고날 아키텍처(Hexagonal Architecture) 사상을 엄격히 고수한다.

```text
  [ Domain ]  <---  [ Service ]  <---  [ Ports (Interfaces) ]  <=== (Dependency Inversion) ===  [ Adapters ]
  (순수 타입)        (비즈니스 논리)        (추상 리포지토리/스토리지)                                (GORM / MinIO SDK)
```

1. **내부 코어 (`domain`, `service`)의 독립성**:
   - `internal/domain`과 `internal/service`는 데이터베이스 패키지(`gorm`), 파일 스토리지 패키지(`minio`) 등 구체 외부 프레임워크 기술을 절대 직접 임포트하거나 참조하지 않는다.
   - 오직 `internal/ports`에서 정의된 인터페이스 규격(Port)만을 바라보며 동작하므로, 추후 스토리지나 데이터베이스 인프라가 변동되어도 핵심 비즈니스 논리 코드는 100% 무결하게 보호된다.
2. **구체 기술의 어댑터화 (`adapters`)**:
   - PostgreSQL 연결 라이브러리 및 MinIO S3 SDK 라이브러리는 전적으로 외부 경계 계층인 `adapters/` 하위에 완전히 은닉되어 포트를 통해 동적으로 주입(Dependency Injection)된다.

---

## 4. [엔지니어링 고찰] 레거시 설계의 한계 극복 (Resolving Limitations)

이전 Python 모노리스 및 초창기 MVP 아키텍처가 안고 있던 현실적인 소프트웨어 공학적 취약점을 기술적으로 완벽하게 극복하였습니다.

### 1) 로컬 SQLite 영속성 ➔ 엔터프라이즈 PostgreSQL + PostGIS 전환
- **이전의 한계**: SQLite 로컬 파일 저장은 여러 기기에서 동시 테스트하거나 컨테이너화하여 연속적으로 배포할 때, 다중 프로세스의 쓰기 경합(DB Lock)과 원격 스토리지 유실 등의 치명적인 안정성 결함을 보였다.
- **극복 조치**: `docker-compose`를 통해 공간 연산 능력을 갖춘 `postgis/postgis` 이미지를 표준 DB로 채택하였으며, GORM PostgreSQL 어댑터를 통해 원격에서도 정합성을 잃지 않는 분산 안정성을 완비하였다.

### 2) 비결정론적 타입 예외 ➔ 컴파일 타임 정적 가드로의 진화
- **이전의 한계**: Python 환경에서 아무리 유닛 테스트 하네스와 Pydantic, Beartype 등의 데코레이터로 가드를 세우더라도, 동적 타이핑 특유의 런타임 타입 누수와 Mypy strict 설정 누락 시의 불안정성이 상존했다.
- **극복 조치**: 관제 코어의 핵심 데이터와 트래픽 관문을 **Go 컴파일러의 정적 강결합 타입 체크** 영역으로 밀어 넣었다. 진입 경계에서 API 페이로드 규격을 구조체로 고정하고, 서비스 흐름 상에서 런타임 타입 어설션(Assertion) 에러가 발생할 가능성을 물리적으로 100% 영구 소멸시켰다.

### 3) 대용량 미디어 I/O 병목 ➔ MinIO Presigned URL 분산 처리
- **이전의 한계**: 로봇이 촬영한 고용량 영상/음성 프레임 바이너리를 백엔드 서버가 받아서 다시 프론트엔드로 대리 전달(Proxying)하는 구조는 서버 메모리와 네트워크 대역폭에 극심한 I/O 병목을 발생시켰다.
- **극복 조치**: 백엔드 Go 서버는 파일 업로드 및 다운로드를 위한 서명된 임시 안전 링크인 **Presigned URL**만 계산하여 브라우저에 던져준다. React UI는 해당 URL을 받아 MinIO 스토리지 노드로 직접 우회(Direct Streaming) 접근하여 미디어를 스트리밍 재생하므로, 관제 백엔드의 동시 처리량과 메모리 가용성이 극대화되었다.

### 4) 스파게티 DOM manipulation ➔ Zustand Reactive State Engine 전환
- **이전의 한계**: Vanilla JS의 직접적인 DOM 엘리먼트 제어 방식은 텔레메트리 데이터가 실시간으로 수백 개씩 요동치기 시작하면 렌더링 상태 싱크가 깨지고 코드 가독성이 스파게티처럼 파괴되는 한계를 가졌다.
- **극복 조치**: React의 가상 돔(Virtual DOM) 렌더링 최적화와 Zustand 전역 상태 저장소의 reactive selector 방식을 결합했다. 웹소켓 프레임 수신 시 지정된 selector 필드만 리액티브하게 타겟 렌더링되어 웅장하고 세련된 대시보드를 프레임 드랍 없이 극도로 부드럽게 유지한다.

---

## 5. 결론

본 아키텍처 개편을 통해 재난 구조 관제 센터 소프트웨어는 책상 위 설계 명세에만 안주하는 Mock 중심의 껍데기 설계를 넘어서, **필드 환경의 동시성 트래픽과 내결함성(Fault Tolerance), 엔터프라이즈 영속성을 지니게 된 분산형 아키텍처**로 완벽하게 도약하였다.
