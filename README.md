# 🤖 Rescue Robot Joint Control Center Platform

> **재난 구조용 바퀴형 사족로봇 시스템 미션 제어, 실시간 험지 topography 레이더 관제 및 분산 미디어 전송 플랫폼**

본 프로젝트는 재난 구조(SAR: Search and Rescue) 현장에서 활약하는 사족 로봇의 주행 결정, 센서 융합(Sensor Fusion), 험지 지형 극복 프로파일 결정을 안전하게 오케스트레이션하기 위해 기존 Python 모노리스에서 **Go (Server Core), React + TS (Control Dashboard), PostgreSQL (Database), MinIO (Object Storage)** 기술 스택으로 성공적으로 마이그레이션된 **최첨단 통합 통제 플랫폼**입니다.

---

## 🌟 Key Architecture & Features

### 1. 현대화 마이그레이션 기술 스택 (Modernized Stack)
- **Go Server Core (`go_core/`)**:
  - Gin-Gonic 웹 프레임워크를 기반으로 고성능 REST API와 실시간 텔레메트리 분산 WebSocket 통로(`/ws/telemetry`)를 개설하였습니다.
  - Python `@beartype` 데코레이터를 통한 런타임 타입 가드는 Go의 강력한 정적 타이핑(Static Typing)으로 컴파일 경계 가드를 구현하였으며, 외부 JSON 페이로드는 `go-playground/validator`로 타입 안정성을 극대화했습니다.
- **React Control Dashboard (`react_ui/`)**:
  - Vite와 TypeScript를 기반으로 구축된 최상급 다크 테마 글래스모피즘(Glassmorphism) UI 대시보드입니다.
  - Zustand 상태 스토어를 통해 실시간 로봇 텔레메트리, 사건 사고 스트림, 탐지 요구조자 대장을 반응형(Reactive)으로 동기화합니다.
  - **Live Video Feed Card**: 열화상(Thermal) 및 RGB 카메라로부터 수신되는 실시간 비디오 프레임 데이터를 대시보드 상에 초저지연(Ultra-low latency) 고속 플레이백으로 연출합니다.
- **GORM PostgreSQL & MinIO S3 Object Storage**:
  - PostgreSQL DB에 GORM 어댑터를 탑재하여 탐색 임무 계획(`plans`), 드래프트(`drafts`), 사건 로그(`events`)를 영속 저장합니다.
  - 로봇이 송출하는 비디오 프레임/오디오/3D 맵 등의 대용량 미디어 데이터를 MinIO에 격리 적재하고, UI가 직접 버퍼링할 수 있는 **Secure Presigned URL(서명 임시 링크)**을 발행하여 대역폭 I/O 병목을 완벽히 해결했습니다.

### 2. 가드 장치 및 분산 프로세스 격리 (Fault Isolation & Type Guards)
- **Beartype 런타임 타입 가드**:
  - 레거시 파이썬 컴포넌트의 신뢰도 보증을 위해 `@beartype` 데코레이터를 전면 적용하여 엄격한 타입 무결성(0 Errors)을 증명했습니다.
- **gRPC 기반 프로세스 물리 격리 및 카오스 내결함성**:
  - `grpc_process_gateway.py`를 구현하여, SLAM/인식 모듈 등 특정 연산 프로세스가 비정상 종료되거나 물리 차단되는 극한의 재난 시나리오에서도 전체 시스템이 Autonomous Failover 모드로 즉시 전환되도록 카오스 내결함성 안전장치를 탑재했습니다.

### 3. HTML5 Canvas 2.5D Isometric Topographic Radar
- 대시보드 중앙에 HTML5 Canvas를 이용한 **입체 2.5D 등고선 지형 레이더 화면**을 배치하여, 로봇의 실시간 Pose 궤적 및 험지 극복 드라이브 프로파일(Safe, Climb, Slow, Critical Halt)을 입체 그라디언트 그물망으로 회전 렌더링합니다.

---

## 🚀 Quick Start (동작 및 테스트 구동 가이드)

### 시나리오 A: 원클릭 로컬 통합 시뮬레이터 구동 (Docker/Go 불필요)
로컬 PC에 Docker나 Go 컴파일러가 없더라도, Python 단독 실행을 통해 320x240 실시간 FLIR 열화상 프레임과 Bounding Box 인명 탐지 시나리오를 1분 만에 가동하여 직접 체험할 수 있습니다.

1. **데모 통합 서버 기동**:
   ```powershell
   python run_mvp.py
   ```
   > Uvicorn 서버 기동 즉시 웹 브라우저 **[http://localhost:8000](http://localhost:8000)** 이 자동으로 열립니다.

2. **비디오 프레임 송출 시뮬레이터 기동**:
   *새로운 PowerShell 터미널을 추가로 열고* 아래 명령을 실행합니다:
   ```powershell
   python send_test_frame.py
   ```
   > Pillow 라이브러리 부재 시 백그라운드에서 자가 치유 설치가 진행되며 즉시 영상 피드가 렌더링되기 시작합니다.

---

### 시나리오 B: 현대화 마이그레이션 컨테이너 풀스택 구동 (Go + React + PostgreSQL + MinIO)
실제 운영 및 미디어 전송 환경까지 완전히 가동하는 윈도우 원클릭 프로세스입니다.

1. **Docker Desktop 기동**:
   - 노트북의 Docker Desktop 엔진을 먼저 실행해 주십시오. (Hyper-V/WSL2 활성화 필요)

2. **원클릭 인프라 & 서버 기동 스크립트 실행 (관리자 권한)**:
   프로젝트 루트 디렉토리에서 관리자 권한 터미널을 열고 다음 명령어를 한 줄로 입력합니다:
   ```powershell
   powershell -ExecutionPolicy Bypass -File launch_all.ps1
   ```
   > **스크립트가 자동 수행하는 작업**:
   > - `docker compose up -d`를 통해 PostgreSQL 및 MinIO 컨테이너 실행 및 `video`/`audio`/`maps` 다운로드 가능 버킷 초기 생성
   > - `go_core/server.exe` 백엔드 서버 기동 및 DB/스토리지 연동 (Port 8080)
   > - `npm run dev`를 통한 React Vite 대시보드 웹 서버 기동 (Port 5173)

3. **웹 관제 대시보드 접속**:
   - 브라우저를 열고 **[http://localhost:5173](http://localhost:5173)** 주소로 접속해 관제 시스템을 감상합니다.

4. **실시간 비디오 전송 및 카메라 스트리밍 시작 (하이브리드 지원)**:
   *새로운 터미널 창을 열고* 상황에 맞는 송출 명령을 기동합니다:

   **옵션 A: 최첨단 E2E 압축 WebRTC 실시간 카메라 스트리밍 (강력 추천 - 신규 탑재)**
   ```powershell
   python send_video_webrtc.py
   ```
   > - `send_video_webrtc.py`는 `aiortc`와 `websockets`를 사용하여 웹캠 비디오 프레임을 VP8/H.264 압축 인코딩 후 WebRTC 채널을 통해 초당 30프레임으로 실시간 전송합니다.
   > - 로컬 PC에 실제 웹캠이 없거나 연동에 실패하더라도, **고화질의 동적 그래픽 진단 화면(그라디언트 레이더, 스캐너, 실시간 카운터)**을 자동 합성하여 스트리밍을 정상 가동하는 뛰어난 예외 대응 능력을 갖추고 있습니다.

   **옵션 B: HTTP POST 기반 레거시 JPEG 프레임 폴링 스트리밍**
   ```powershell
   # 실제 소장하고 계신 MP4 비디오 파일 스트리밍 전송
   python send_video_file.py "C:\path\to\your\video.mp4"
   
   # 또는 노트북 내장 웹캠 카메라 피드를 실시간 대시보드로 스트리밍 송출
   python send_video_file.py webcam
   ```
   > - 대시보드 UI(`SOPPanel.tsx`)는 두 방식 모두를 완벽하게 인지하는 **하이브리드 렌더러**로 개편되어, WebRTC 커넥션이 동작할 때는 compressed video player로 작동하다가, 레거시 폴링 프레임이 인입되면 자동으로 JPEG 뷰어로 롤백되어 동시 호환됩니다.

---

## 💻 다중 디바이스 연속 작업 워크플로우 (Multi-Device Workflow)

여러 대의 개발용 랩탑/워크스테이션 환경에서 끊김 없이 상태를 싱크하여 Pair Programming 및 개발을 지속하기 위해 다음 절차를 제공합니다.

1. **진행 상태 동기화**:
   - 에이전트의 개발 진행 궤적 정보는 [task.md](docs/dev-state/task.md) 및 [walkthrough.md](docs/dev-state/walkthrough.md)에 보존되며 원격 Git으로 연동됩니다.
   - 새 디바이스에서 단순히 `git pull`을 실행하면 이전 작업 락을 안전하게 인계받아 이어서 즉시 구현할 수 있습니다.

2. **통합 환경 설정**:
   - [.env.example](.env.example) 파일 내용을 바탕으로 로컬 복사본 `.env` 파일을 생성하여 디바이스별 커스텀 세팅이 가능합니다.

---

## 📁 Directory Structure

```text
rescue-robot-system-main/
├── go_core/                 # Go 기반 고성능 Server Core 및 백엔드
│   ├── cmd/server/main.go   # API 라우터, 웹소켓 및 가드 총괄 메인 진입점
│   ├── server.exe           # 컴파일된 고성능 백엔드 실행 파일 (Windows)
│   └── internal/
│       ├── domain/          # 지형, 임무, 사건 로그 Go Pure 도메인 모델
│       ├── service/         # 주행 정책(decide_drive_profile), 융합 판정 로직 서비스
│       ├── ports/           # 데이터베이스 및 스토리지 포트 인터페이스
│       └── adapters/        # GORM Postgres 리포지토리 & MinIO S3 SDK 어댑터
├── react_ui/                # Vite + TypeScript + React 관제 프론트엔드 UI
│   ├── src/
│   │   ├── components/      # 3D 지형 Radar Canvas 및 실시간 Live Video 피드 카드
│   │   ├── store/useStore.ts# 실시간 WebSocket 바인딩 Zustand 스토어
│   │   └── index.css        # 글래스모피즘 및 네온 이펙트 글로벌 스타일시트
├── src/                     # Python 런타임 타입 가드 & gRPC 결함 격리 컴포넌트
├── tests/                   # Python / Go TDD 무결성 증명 테스트 스위트
├── docker-compose.yml       # PostgreSQL + MinIO 자동화 인프라 정의서
├── launch_all.ps1           # Windows용 원클릭 인프라/백엔드/프론트엔드 전체 가동 스크립트
├── send_video_file.py       # 실시간 실제 동영상/카메라 스트리밍 프레임 송출기 (OpenCV 기반)
├── send_test_frame.py       # 모의 FLIR 카메라 시뮬레이션 프레임 송출기 (Pillow 기반)
├── .env.example             # 통합 환경 변수 템플릿
└── README.md                # 본 프로젝트 종합 안내서
```
