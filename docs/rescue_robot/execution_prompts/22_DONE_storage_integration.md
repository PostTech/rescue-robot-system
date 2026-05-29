# 16 TODO — Storage Integration

## Phase Reference
- Phase-8 Storage Integration

## Prompt

Event/Mission/Media 저장 흐름을 구현해 주세요.

### Dependency Rule
```text
Adapters -> Service -> Config -> Types
```

### Reference Docs
- `implementation_roadmap.md` Phase-8
- `interface.md` (IEventRepository, IMediaRepository)
- `detailed_interface_schema.md`

### Create
```text
src/adapters/storage/in_memory_event_repository.py
src/adapters/storage/in_memory_media_repository.py
src/service/storage_sync_service.py    — Local save -> remote sync
tests/unit/service/test_storage_sync_service.py
tests/contract/test_storage_contracts.py
```

### Features
- InMemoryEventRepository implements IEventRepository Protocol
- InMemoryMediaRepository implements IMediaRepository Protocol
- Local-first save: always save locally before sync
- Retry on sync failure with exponential backoff
- Critical events (EMERGENCY_STOP, GAS_ALERT) never discarded
- Storage full handling: discard non-critical, keep critical

### Required TC
- TC-STORAGE-001: Event save and retrieve
- TC-STORAGE-002: Media save and retrieve
- TC-STORAGE-003: Sync retry on failure
- TC-STORAGE-004: Critical events preserved on storage full
- TC-DETVAL-006: Deterministic storage key
- TC-DETVAL-007: Same failure scenario = same retry order

### Completion Criteria
1. All repositories implement their Protocol interfaces
2. Critical events never lost
3. Deterministic retry ordering
4. No real database dependency
