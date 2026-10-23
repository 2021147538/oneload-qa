# 저장소 구조와 현재 버전

2026-10-23 11:36 KST의 [표준 기준선](../reports/baseline.json)과 별도 [RAG API](../reports/rag-integration-probe.json)·[검색](../reports/retrieval-evaluation.json) 증거를 구분한다. 전체 SHA는 [repos.lock.json](../repos.lock.json)에 있다.

| 저장소 / 폴더 | 커밋 | 역할·이번 범위 |
|---|---|---|
| oneload-app | b5d6835 | 사진·확정·경로·이벤트 HTTP 연결, 소스 검토 wired. 이번 실제 브라우저 미실행 |
| oneload-backend | c9b8d8a | 대화 복원·멱등성 포함48건+주입 API |
| oneload_agent | 250271e | LLMAgent·Vision·프롬프트v3, 기존43건 |
| oneload-data | 606f648 | 공유 지도·스키마·예시 파노라마 |
| oneload-infra | 8587d3b | Compose·Portainer·Caddy, 배포 미실행 |
| oneload-rag | 4a967b3 | 공식 근거·MemorySearch·MCP 추가. 이번 MemorySearch만 검사 |
| oneload-qa / qa | 이 문서 포함 커밋 | QA28건·컴포넌트·검색·서비스 정답 초안·증거 |

```text
project/
  oneload-app/src/                 웹 상태·API 계층·화면
  oneload-backend/
    app/api/, app/ai/, app/domain/ API·계약·guard·경로·위치 매칭
    tests/fixtures/maps/          Backend 자체 시험 지도
    migrations/                   DB 마이그레이션
  oneload_agent/
    hangil_r2/, mocks/maps/        Agent·Vision·타입 사본·자체 시험 지도
    prompts/, tests/, docs/
  oneload-data/
    maps/, panos/, schema/, tools/ 공유 지도·예시 사진·데이터 검증
  oneload-infra/macserver/         Compose·Caddy·배포 스크립트
  oneload-rag/
    src/hangil_rag/, knowledge/    검색·공식/커뮤니티 문서(커뮤니티 QA 제외)
    eval/, docs/, localization/   R3 진단·협업 자료·합성 위치 평가
  qa/
    scripts/qa_inputs.py           공유 지도·데이터·커밋 입력
    scripts/run_checks.py          표준 전체 실행·공개 증거 갱신
    scripts/rag_inputs.py          명시적 공식 MemorySearch 프로필
    scripts/evaluate_retrieval.py  개발 선택·holdout·R3 진단
    scripts/run_backend_tests.py   자신이 만든 일회용 DB만 사용
    tests/                        지도·장애·평가 회귀28건
    eval/                         서비스v2·컴포넌트v2·검색v1·기능TC·사진명세
    reports/                      검토된 공개 증거
    docs/handoff.md                시작점·미완료·재현
    results/                      Git 제외 원시 실행 결과
```

통합 지도는 oneload-data/maps/seoul-station.json(version2026-10-22.1)이다. Backend·Agent 고정 fixture와 다를 수 있으며 파일 차이만으로 계약 오류를 만들지 않는다. 관련 커밋·지도·사진·실행기 해시를 기록한다.
기존 지도 경로 수정(QA #1), 사진 장애 거짓 실패 수정(QA #2)은 유지했다. QA #3은 서비스 정답·검색 평가·별도 RAG API를 보완했다. 자세한 판정은 [결과 설명](issue3-resolution.md), 이후 작업은 [인수인계](handoff.md)에 있다. 이전 Git 이력 복구는 [기록](git-sync.md)을 참고한다.

## QA #4 반영

Frontend 검토 기록(eval/frontend_wiring.json)과 실행 모듈(scripts/frontend_wiring.py)을 추가했다. 검토한 소스 연결만 확인하며 미검토 코드에는 review_required로 중단한다. 과거 미연결 버전은 계속 P0다. [해결 설명](issue4-resolution.md)과 [인수인계](handoff.md)를 따른다. 전체 기준선은 이번 실행으로 갱신했고 이전 소스/CI 관찰 보고서는 당시 기록으로 보존했다.
