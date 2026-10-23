# 최신 QA — 2026-10-23 13:33 KST

RAG #3 답글의 R6 신규 평가 요청을 수행했다. 새40문항을 검색 전 QA7f41130으로 고정했고 수정 전47ab39f/후e6c03f2를 같은0.25에서 각1회 비교했다. 원래 호텔 객실 가격·실시간 빈 좌석은 수정됐지만 **새 오탐3건과 정상 질문 누락3건으로 이슈는 open**이다. [절차·실패 질문](../docs/rag-issue3-revalidation.md).

| 대상 | 버전·범위 | 결과 |
|---|---|---|
| QA | 기존28+holdout6+패키지 자산4 | 38/38, skip0 |
| 데이터 | 606f648 | 3/3 |
| Agent | 54c321f·FakeLLM | 43/43 |
| Backend | c9b8d8a·일회용 DB | 48/48 |
| 컴포넌트 v2 | 기존 질문·기대값·SHA 유지 | 20시나리오·21턴 통과 |
| 표준 R2↔Backend API | 모의 검색·합성 JPEG | 20/20 |
| 별도 RAG API | e6c03f2·MemorySearch0.25·FakeLLM | 21/21 |
| 새 R6 v2 검색 | 前47ab39f→後e6c03f2·min_score0.25 | top3 20/20→17/20, 범위밖 빈 결과5/20→17/20 |
| Frontend 소스 | App2666e44·검토 profile | wired, 이번 실제 브라우저 NOT_RUN |
| Infra | 8587d3b | 커밋 기록만, 배포 미실행 |

[전체 기준선](baseline.json) · [계약 감사](contract-audit.json) · [모의 API](integration-probe.json) · [RAG API](rag-integration-probe.json) · [검색 전후 증거](rag-issue3-revalidation.json)

Agent 패키지가 실제 읽는 PROMPT_DIR/MOCK_DIR에 맞춰 평가 실행기 경로·해시를 수정했다. 과거 repo/prompts/mocks를 가정하지 않고 선택한 checkout 내부 자산인지 확인한다. component v2 SHA와 질문·기대값은 그대로다.

RAG 답글의 기존 수치도 재현했다. 수정 후 R6 개발/노출 holdout 각각 top3 10/10·범위밖6/6, R3기존38/40·4/4, R3노출 holdout16/16·11/12다. 이들은 새 독립 holdout 수치가 아니다. 새 v2도 이제 노출됐으며 다음 수정의 회귀용으로만 사용한다. 임계값 운영 확정은 보류한다.

Frontend 감사의 [QA #4 수정 원칙](../docs/issue4-resolution.md)은 유지한다. App2666e44 CI365+E2E4는 [이전 관찰](app-review-2666e44.json)이며 이번 실행한 실제 브라우저 결과로 합산하지 않는다. RAGe6c03f2 [CI](https://github.com/team-onetruck/oneload-rag/actions/runs/39897084335)는 success지만 로컬 pgvector/MCP 전체 재시험은 아니다.

남은 P0는 **INT-07: Backend 기본 RuleAgent/NoVision**이다. 전체 exit1을 유지하고 DATA-01 현장 정답도 대기한다. [QA #3](https://github.com/team-onetruck/oneload-qa/issues/3)은 마지막 두 조건이 미완료다. 실제 모델·임베딩 호출0회, 현장 사진 정답0건, 컴포넌트21턴 사람 검토 대기·최종 품질 점수null이다. 기능 TC의 PARTIAL/NOT_RUN을 자동 PASS로 바꾸지 않았다.
