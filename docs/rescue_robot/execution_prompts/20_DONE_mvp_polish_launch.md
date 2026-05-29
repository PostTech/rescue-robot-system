# 20 TODO — MVP Polish & Launch Script

## Phase
- Phase MVP-6: Polish

## Prompt

MVP를 한 번에 실행할 수 있도록 정리하고 최종 점검해 주세요.

### Create
```text
run_mvp.py                   — 서버 + 브라우저 자동 실행
requirements.txt             — pip 의존성
README.md                    — 프로젝트 설명 + 실행 방법
```

### run_mvp.py
```python
# 1. pip install fastapi uvicorn
# 2. Start FastAPI server on port 8000
# 3. Open browser to dashboard
# 4. Print URL to console
```

### Polish
- 에러 핸들링 (API 에러 시 사용자 친화적 메시지)
- 로딩 스피너
- 빈 상태 UI (미션 없을 때)
- favicon 설정
- 모바일 반응형 점검
- CORS 설정 확인

### Completion Criteria
1. `python run_mvp.py` 한 줄로 전체 시작
2. 브라우저에서 3개 시나리오 데모 가능
3. README에 스크린샷 포함
