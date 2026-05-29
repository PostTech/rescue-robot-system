# 요구사항 추적성 매트릭스

## 1. 목적

본 문서는 요구사항, 설계, 구현, 테스트, 운영 기준의 연결 관계를 정의한다.

---

## 2. 추적성 매트릭스

| Requirement | Design | Implementation | Test | Operation |
|---|---|---|---|---|
| FR-001 Thermal 탐지 | SDD 5, Interface Detector | DetectorAdapter | TC-DET-001 | Victim Detection SOP |
| FR-004 Fusion | SDD 5 | Fusion Logic | TC-DET-004 | Operator Review |
| FR-005 Gas Hazard | SDD 5 | Gas Decision Logic | TC-SAFE-002 | Gas Hazard SOP |
| FR-006 SLAM | SDD 2, Interface SLAM | SLAMAdapter | TC-ACC-003 | Navigation Operation |
| FR-008 Emergency Stop | Integration 11, Operation 7 | Safety Logic | TC-SAFE-001 | Emergency Stop SOP |
| FR-009 WebRTC Track | Interface 9 | WebRTCAdapter | TC-IF-002 | Communication Operation |
| FR-011 Local Autonomous | Integration 15 | Failover Logic | TC-COMM-002 | Communication SOP |
| FR-012 Critical Local Save | Integration 12 | StorageAdapter | TC-IF-003 | Storage Operation |
| FR-014 AI 권고 전용 | Interface 11 | SOPAgentAdapter | TC-IF-004 | AI/SOP Operation |
| FR-016 탐색 임무 생성 | Mission Creation Plan, Interface Search Mission Setup | MissionCreationService | TC-MISSION-001, TC-IF-050 | Mission Setup Operation |
| FR-017 탐색 구역 지정 | Mission Creation Plan, Detailed Interface Schema 7 | SearchAreaValidator | TC-MISSION-002, TC-FUNC-BND-010 | Mission Setup Operation |
| FR-018 탐색 방법 선택 | Mission Creation Plan, Interface SearchMethod | SearchMethodPolicy | TC-MISSION-003, TC-FUNC-DEC-010 | Mission Setup Operation |
| FR-019 SOP 기반 임무 설정 | Mission Creation Plan, Interface SOP Configurator | SopMissionConfiguratorAdapter | TC-MISSION-004, TC-IF-052 | AI/SOP Operation |
| FR-020 승인 전 활성화 차단 | Operation 4.2, Interface Mission Creation Service | MissionApprovalGuard | TC-MISSION-005, TC-FUNC-BND-011 | Mission Commander Approval |
| FR-021 3D LiDAR 지형 분석 | SDD Terrain Driven Navigation, Interface TerrainAnalyzer | TerrainAnalyzerAdapter | TC-TERRAIN-001, TC-TERRAIN-002, TC-IF-060 | Navigation Operation |
| FR-022 지형+탐색방법 기반 주행 | Mission Creation Plan 5.1, Interface SearchDrivePolicy | SearchDrivePolicyAdapter | TC-TERRAIN-004, TC-TERRAIN-005, TC-IF-061 | Autonomous Operation |
| NFR-010 Code Quality | Quality Lint Plan | CI Gate | TC-LINT-* | Release Gate |
| MOD-001 Client-1 Bridge 분리 | Interface 6.1 | ROS2/WebRTC Bridge | TC-MOD-001 | Communication Operation |
| MOD-002 Client-2 Detection 분리 | Interface 6.1 | DetectorAdapter | TC-MOD-002 | Detection Operation |
| MOD-003 Client-3 Navigation 분리 | Interface 6.1 | SLAM/Navigation/Controller | TC-MOD-003 | Navigation Operation |
| MOD-004 Server-1 Mission Core 분리 | Interface 6.2 | Mission Core | TC-MOD-004 | Mission Operation |
| MOD-005 Server-2 UI 분리 | Interface 6.2 | Operator UI | TC-MOD-005 | Operator Operation |
| MOD-006 Server-3 Storage 분리 | Interface 6.2 | StorageAdapter | TC-MOD-006 | Storage Operation |
| MOD-007 Server-4 SOP 분리 | Interface 6.2 | SOPAgentAdapter | TC-MOD-007 | AI/SOP Operation |
| NFR-011 ROS 경량 계층화 | ROS Layering Plan, Interface 2.3 | ROS Adapter Boundary | TC-LAYER-* | Release Gate |
| NFR-012 계층별 TDD/Harness | Layer TDD Harness Matrix | Test Harness, Mock Adapter | TC-LAYER-*, TC-IF-*, TC-MOD-* | Release Gate |
| NFR-013 환경 프로파일 전환 | Environment Profile Plan | Runtime Profile Config | Windows Gate / Linux Gate | Deployment Gate |
| NFR-014 Windows 테스트 범위 | Environment Profile Plan, Test Plan | Mock/Fake Adapter | TC-LINT-*, TC-LAYER-*, TC-MOD-* | Default Test Gate |
| NFR-015 Deterministic Validation | Deterministic Validation Plan | FakeClock, Fixed Seed, Snapshot Test | TC-DETVAL-* | Default Test Gate |
| NFR-016 Interface Baseline Freeze | Interface Baseline Freeze | Client/Server Contract | TC-IF-*, TC-MOD-* | Interface Change Gate |
| NFR-017 Function Unit Test | Function Unit Test Plan | Decision/Boundary Functions | TC-FUNC-DEC-*, TC-FUNC-BND-* | Default Test Gate |
| NFR-018 Mission Setup Determinism | Mission Creation Plan, Deterministic Validation Plan | FakeClock, Deterministic Mission ID | TC-MISSION-008, TC-DETVAL-* | Default Test Gate |
| NFR-019 Terrain Driven Navigation | Interface SearchDriveProfile, Integration Terrain Analysis | TerrainDrivenNavigationPolicy | TC-TERRAIN-*, TC-FUNC-DEC-012 | Default Test Gate |
| NFR-020 Dependency Direction | Dependency Direction Plan, Interface 2.2 | Import Boundary Check | TC-DEP-* | Default Test Gate |

---

## 3. 변경 관리

1. 요구사항이 변경되면 관련 설계와 테스트를 함께 수정한다.
2. Interface Schema가 변경되면 Adapter와 Test Harness를 함께 수정한다.
3. Client/Server Interface Baseline 변경은 Change Request와 승인 절차를 필요로 한다.
4. P0 요구사항의 테스트 누락은 Acceptance 진입 차단 사유다.
5. Lint Gate 변경은 Tech Lead 승인을 필요로 한다.
