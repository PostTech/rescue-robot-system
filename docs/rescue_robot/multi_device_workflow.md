# Rescue Robot Project: Multi-Device Continuous Development Workflow

본 가이드는 개발자가 **여러 대의 노트북(노트북 A, B 등)**을 교체하며 사용할 때, **코드, 로컬 인프라(DB/Object Storage), 설정, 그리고 AI 에이전트(Antigravity)의 개발 상태**를 끊김 없이 연속적으로 작업하기 위한 표준 워크플로우를 정의합니다.

---

## 1. 3대 영역 동기화 전략 (Three-Tier Sync Strategy)

연속적인 개발 흐름을 유지하려면 아래 세 가지 요소가 모든 디바이스에서 동일하게 정렬되어야 합니다.

```
  [ 노트북 A ]                           [ 원격 저장소 (GitHub / GitLab) ]                     [ 노트북 B ]
+---------------+                       +-----------------------------------+                       +---------------+
| Code & Config | -- git push (WIP) --> |  - Git Repository (Code & WIP)    | -- git pull (WIP) --> | Code & Config |
| AI Context    |                       |  - AI Sync Docs (task.md in Git)  |                       | AI Context    |
+---------------+                       +-----------------------------------+                       +---------------+
        |                                                                                                   |
  docker compose                                                                                      docker compose
        |                                                                                                   |
        v                                                                                                   v
+---------------+                                                                                   +---------------+
| Postgres/MinIO|                                                                                   | Postgres/MinIO|
+---------------+                                                                                   +---------------+
```

### ① 코드 및 AI 컨텍스트 동기화 (Git & AI Context)
* **Git WIP (Work In Progress) 브랜치 활용**: 미완성된 코드나 테스트 도중 랩탑을 이동해야 할 때, 로컬에 묵혀두지 않고 `wip/feature-name` 브랜치에 과감히 커밋 후 Push합니다.
* **AI 에이전트(Antigravity) 상태 이식**: 
  * AI 에이전트는 로컬에 설치된 App Data 폴더(`C:\Users\cosmo\.gemini\antigravity`)에 대화 기록과 아티팩트를 보존합니다.
  * **해결책**: 에이전트가 작성하는 핵심 관리 아티팩트(`task.md`, `implementation_plan.md`, `walkthrough.md`)를 **Git 프로젝트 폴더 내부(`docs/dev-state/`)에 포함하여 함께 커밋**합니다.
  * 새로운 랩탑에서 새로운 AI 대화 세션을 시작할 때, AI에게 **"docs/dev-state/ 하위의 task.md와 implementation_plan.md를 읽고 하던 일을 이어서 해줘"**라고 요청하면, AI는 즉시 이전 랩탑에서의 진행 상태를 100% 이해하고 연속성 있게 협업을 시작합니다.

### ② 개발 인프라의 컨테이너화 (Docker Compose)
* **문제점**: 노트북마다 PostgreSQL 및 MinIO 버전을 맞추고, PostGIS 확장팩을 수동 설치하고, S3 버킷을 수동 생성하는 작업은 환경 불일치를 초래합니다.
* **해결책**: 프로젝트 루트에 `docker-compose.yml`을 구성합니다.
  * **PostgreSQL + PostGIS**: 컨테이너 기동 시 지리 연산 도구가 자동 활성화되도록 구성.
  * **MinIO**: 컨테이너가 켜질 때 초기 헬스체크 및 테스트용 버킷(`video`, `audio`, `maps`)을 자동 생성하는 엔트리포인터 쉘 스크립트 결합.
  * 노트북 교체 시, 터미널에서 `docker compose up -d` 한 줄이면 즉각 완벽히 동일한 인프라가 1초 만에 구성됩니다.

### ③ 데이터베이스 스키마 및 더미 데이터 정렬
* **DB 마이그레이션 도구 도입**: Go 서비스 내에 `golang-migrate`나 `GORM AutoMigrate`를 탑재합니다. 코드가 최신화될 때 스키마 정의도 자동으로 최신화되도록 만듭니다.
* **시드(Seed) 스크립트 작성**: 지형 데이터 피스, 모의 SOP 프로필, 가상의 로봇 데이터 등 개발에 필수적인 기초 데이터를 테이블에 채워주는 `seed.sql` 혹은 Go 스크립트를 작성하여 Git에 공유합니다.

---

## 2. 프로젝트 초기 설정 및 노트북 교체 시 체크리스트

### 🛠️ 프로젝트 루트 설정 가이드

#### 1) 로컬 환경 설정 파일 (`.env.example`)
보안상 민감한 정보나 각 노트북 고유의 경로(예: 로컬 카메라 인덱스 등)를 제외하고, 기본 DB 접속 주소와 MinIO 접속 프로필을 정의한 공유 템플릿입니다.

```ini
# .env.example
PORT=8080
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=secretpassword
DB_NAME=rescue_robot
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_USE_SSL=false
```

#### 2) 인프라 통합 실행 스크립트 (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    container_name: rescue_postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: rescue_robot
    volumes:
      - pgdata:/var/lib/postgresql/data

  minio:
    image: minio/minio:RELEASE.2024-01-28T22-35-53Z
    container_name: rescue_minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  miniodata:
```

---

## 3. 연속적 교체 작업 시나리오 (Daily Workflow)

#### 노트북 A에서 퇴근/이동 준비를 할 때:
```bash
# 1. 작업 내용 및 AI 아티팩트 이식 복사
# (AI 에이전트의 task.md 등을 docs/dev-state/ 폴더로 복사해 둔다)

# 2. 미완성 작업을 임시 WIP 브랜치에 저장 및 push
git checkout -b wip/mission-core-go
git add .
git commit -m "WIP: decide_drive_profile Go implementation & task sync"
git push origin wip/mission-core-go
```

#### 노트북 B에서 출근/이어서 시작할 때:
```bash
# 1. 코드 원격 풀링
git fetch
git checkout wip/mission-core-go
git pull origin wip/mission-core-go

# 2. 로컬 인프라 (Postgres, MinIO) 원클릭 구동
docker compose up -d

# 3. 로컬 DB 마이그레이션 및 시드 스크립트 실행
go run cmd/migrate/main.go --action=up
go run cmd/seed/main.go

# 4. AI 에이전트(Antigravity)를 켜고 다음과 같이 발화:
# "docs/dev-state/task.md 와 docs/dev-state/implementation_plan.md를 분석해서 우리가 어디까지 진행했고, 다음 예정 작업이 무엇인지 확인한 뒤 하던 일을 이어서 코딩해 줘."
```

이 규칙을 준수하면, 디바이스의 하드웨어 한계를 뛰어넘어 단 1분의 흐름 유실도 없이 **완전하고 끊김 없는 원격 1인 다중기기 연속 개발**이 실현됩니다.
