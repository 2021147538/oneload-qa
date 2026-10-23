# 현재 QA 결과 — 2026-10-23 11:04 KST

QA #3의 평가셋·실행기 변경을 반영해 표준 기준선을 갱신하고 실제 메모리 RAG를 별도 검사했다.

이후 App608a04c·RAG47ab39f의 변경/CI·고정 검색셋 회귀를 [별도 검토](source-review-20261023.json)했다. 아래 수치는11:04 표준 실행 기준이며 후속 소스 관찰로 바꾸지 않는다.

| 대상 | 버전·대상 | 결과 |
|---|---|---|
| QA 회귀 | 지도·장애11건 + 검색/근거 버전6건 | 17/17, skip0 |
| 데이터 | 606f648 | 3/3 |
| Backend | 493884f | 기존44/44, 일회용 DB |
| Agent | 250271e | 기존43/43, FakeLLM |
| 컴포넌트 v2 | 실제 공유 지도·모의 검색 | 20/20 시나리오·21/21 턴 |
| 표준 R2↔Backend API | 모의 검색·합성 JPEG | 20/20 |
| 별도 RAG 주입 API | RAG4a967b3·MemorySearch0.35·FakeLLM | 21/21 |
| Frontend | b111af6 | 소스 관찰·감사, 이번 UI/빌드/E2E 미실행 |
| Infra | 8587d3b | 커밋 기록, 배포 미실행 |

[표준 실행](baseline.json) · [계약 감사](contract-audit.json) · [데이터](data-validation.json) · [컴포넌트](component-metadata.json) · [모의 API](integration-probe.json) · [RAG API](rag-integration-probe.json)

표준 전체 exit1은 INT-06/07 때문이다. App은 HTTP 채팅·언어 변경을 연결했지만 사진 위치·경로 화면에 로컬 흐름이 남는다. Backend 기본값은 RuleAgent/NoVision이다. 주입 API 통과를 운영 연결 완료로 해석하지 않는다.
지도2026-10-22.1은 노드10·엣지9·POI4·파노라마6, 모두 예시 사진이며 실제 현장 정답0건이다.

## QA #3 반영과 미완료

[상세 판정](../docs/issue3-resolution.md) · [서비스 v2](../eval/service_gold.csv) · [검색32문항](../eval/retrieval_cases.json) · [검색 증거](retrieval-evaluation.json)

- Q10은 조건별 요금·출처·확인일을 요구하는 답가능으로 변경했고 20문항의 근거를 매핑했다. 사람 검토20건·서비스 출력은 대기다.
- component v2 질문·기대값·SHA는 유지했다. FakeLLM 모의 검색과 실제 서비스 정답 변경을 섞지 않는다.
- 개발셋으로 선정한 검색 후보0.35: top3 9/10·범위밖 차단5/6. 독립 질문군 holdout: top3 10/10·차단4/6. 출고 조건 미달로 운영 임계값은 미확정이다.
- 기존 R3 44문항 기본0.25는 top1 32/40·top3 38/40·차단3/4로 재현했다. 후보0.35에서 top3 35/40으로 회귀했다.
- 호텔 가격·실시간 잔여석 검색 오탐은 [RAG #3](https://github.com/team-onetruck/oneload-rag/issues/3)에 등록했다. 범위 판정 개선 후 새 holdout이 필요하다.
- RAG 주입 API21/21은 요금 근거·URL·확인일 전달과 빈검색 보류 대조군을 포함한다. INT-07 이후 기본 경로 재검사는 대기다.

실제 LLM/VLM/임베딩 호출0회, 실제 사진·휴대폰 화면·운영 배포 미검증, 컴포넌트21턴 사람 검토 대기·실제 품질 점수null이다. 검색 적중률은 사실성·인용 정밀도 점수가 아니다. 최신 RAG MCP·pgvector 전체 시험은 이번 범위가 아니다.
이전 App8c88f89 CI 검토는 [역사적 기록](app-review.json)이며 최신 b111af6의 실행 증거로 사용하지 않는다.
