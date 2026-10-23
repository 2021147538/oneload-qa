# 저장소 구조와 현재 버전

2026-10-23 13:33 KST의 [표준 기준선](../reports/baseline.json)과 별도 [RAG API](../reports/rag-integration-probe.json)·[검색](../reports/rag-issue3-revalidation.json) 증거를 구분한다. 전체 SHA는 [repos.lock.json](../repos.lock.json)에 있다.

| 저장소 / 폴더 | 커밋 | 역할·이번 범위 |
|---|---|---|
| oneload-app | 2666e44 | 사진·확정·경로·이벤트 HTTP 연결, 소스 검토 wired. 이번 실제 브라우저 미실행 |
| oneload-backend | c9b8d8a | 대화 복원·멱등성 포함48건+주입 API |
| oneload_agent | 54c321f | LLMAgent·Vision·프롬프트v3, 기존43건 |
| oneload-data | 606f648 | 공유 지도·스키마·예시 파노라마 |
| oneload-infra | 8587d3b | Compose·Portainer·Caddy, 배포 미실행 |
| oneload-rag | e6c03f2 | 공식 근거·MemorySearch·MCP 추가. 이번 MemorySearch만 검사 |
| oneload-qa / qa | 이 문서 포함 커밋 | QA38건·컴포넌트·검색·서비스 정답 초안·증거 |

```text
project/
  oneload-app/src/                 웹 상태·API 계층·화면
  oneload-backend/
    app/api/, app/ai/, app/domain/ API·계약·guard·경로·위치 매칭
    tests/fixtures/maps/          Backend 자체 시험 지도
    migrations/                   DB 마이그레이션
  oneload_agent/
    hangil_r2/, mocks/maps/        Agent·Vision·타입 사본·자체 시험 지도
    hangil_r2/prompts/, hangil_r2/mocks/ 패키지 자산
    tests/, docs/
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
    scripts/evaluate_retrieval.py  노출된 v1 개발 선택·R3 진단
    scripts/recheck_rag_issue3.py   사전 고정 v2·고정 임계값 전후 비교
    scripts/run_backend_tests.py   자신이 만든 일회용 DB만 사용
    tests/                        지도·장애·평가 회귀38건
    eval/                         서비스v2·컴포넌트v2·검색v1/v2·기능TC·사진명세
    reports/                      검토된 공개 증거
    docs/handoff.md                시작점·미완료·재현
    results/                      Git 제외 원시 실행 결과
```

통합 지도는 oneload-data/maps/seoul-station.json(version2026-10-22.1)이다. Backend·Agent 고정 fixture와 다를 수 있으며 파일 차이만으로 계약 오류를 만들지 않는다. 관련 커밋·지도·사진·실행기 해시를 기록한다.
기존 지도 경로 수정(QA #1), 사진 장애 거짓 실패 수정(QA #2)은 유지했다. QA #3은 서비스 정답·검색 평가·별도 RAG API를 보완했다. 자세한 판정은 [결과 설명](issue3-resolution.md), 이후 작업은 [인수인계](handoff.md)에 있다. 이전 Git 이력 복구는 [기록](git-sync.md)을 참고한다.

## QA #4 반영

Frontend 검토 기록(eval/frontend_wiring.json)과 실행 모듈(scripts/frontend_wiring.py)을 추가했다. 검토한 소스 연결만 확인하며 미검토 코드에는 review_required로 중단한다. 과거 미연결 버전은 계속 P0다. [해결 설명](issue4-resolution.md)과 [인수인계](handoff.md)를 따른다. 전체 기준선은 이번 실행으로 갱신했고 이전 소스/CI 관찰 보고서는 당시 기록으로 보존했다.

## App2666e44와 RAG 후속 검증

App2666e44는 목적지 목록까지 서버 POI로 연결하고 poiBridge를 제거했다. [이전 CI·별도 검토](../reports/app-review-2666e44.json)의365+E2E4(모의 HTTP3+mock1)는 보존했고 이번에는 같은 커밋으로 전체 QA38·Backend48·모의 API20을 다시 실행했다. 실제 서버/휴대폰 UI 인수는 미실행이다.

RAGe6c03f2를 새 holdout40문항으로 검증했고 top3 17/20·범위밖 빈 결과17/20으로 미달이다. 주입 API21/21은 별도 통과다. [실패 질문·동결 커밋·다음 작업](rag-issue3-revalidation.md)을 따르며 RAG #3·QA #3은 open이다.

## 최신 관찰 (2026-10-23 14:08 KST)

App 관찰e6af580은 mock E2E5개·CI 캐시 변경이며 runtime/의존성은 위2666e44와 같다. CI365+E2E9, 별도 QA38·소스 감사 wired를 확인했다. RAG 관찰8c8e902는 RQ-32 제안 문서만 추가돼 검색·API 실제 검증은 위e6c03f2 증거다. [변경/CI 기록](../reports/app-rag-update-20261023.json), [후속 역할과 한계](handoff.md)를 따른다. 위13:33 전체 기준선을 최신 관찰 커밋으로 재라벨하지 않았다.
