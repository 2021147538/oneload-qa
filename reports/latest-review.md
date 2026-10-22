# 현재 버전 점검 결과 — 2026-10-22

| 대상 | 커밋 | 결과 |
|---|---|---|
| Frontend | d45f466 | 이전 동일 커밋의 build·lint 통과 결과 유지. Fast Refresh 경고 1건, API 연결 전 |
| Backend | 2502e65 | 기존 44/44 시험 통과, 일회용 PostgreSQL 17 |
| Agent | b5c5dde | 기존 37/37 시험 통과, FakeLLM |
| R6 컴포넌트 v2 | 위 Backend·Agent | 20/20 시나리오·21/21 턴 자동 검사 통과 |
| R2↔Backend 연결 | 위 Backend·Agent | 10/11 확인 통과, 사진 인식 장애 처리 1건 실패 |

[구조화된 실행 요약](baseline.json) · [계약 증거](contract-audit.json) ·
[API 연결 증거](integration-probe.json) · [컴포넌트 실행 정보](component-metadata.json) ·
[컴포넌트 결과 CSV](component-results.csv)

## 이번에 확인한 변화

이전 INT-01~05(메서드·응답 형식·일반열차 슬롯·후속 대화·지도 형식)은 최신 Agent에서 해결 확인했습니다.
실제 Backend context/Slots/지도/guard와 함께 평가했고, API에서도 일반열차 → 교통카드 없음 → 목적지 설정을 확인했습니다.

대화 → 사진 후보 → 사용자 위치 확인 → 등록 경로 → 출발 → 도착까지 합성 입력으로 통과했습니다.
LLM 장애 시 RuleAgent fallback도 통과했습니다.

INT-08: 사진 인식 장애에서는 기대한 503 AI_SERVICE_UNAVAILABLE 대신 HTTP 500이 발생했습니다.
R2와 Backend가 각각 정의한 VisionUnavailable이 서로 다른 클래스인 것이 원인입니다.
[원인·재현·필요 작업](../docs/integration_findings.md)에 기록했습니다.
계약 점검과 --with-r2 실행기의 종료 코드 1은 이 실패를 숨기지 않고 유지한 결과입니다.

## 판정의 범위

모델은 FakeLLM, 검색은 MockKnowledgeSearch, 사진은 합성 바이트입니다.
실제 모델 호출, 답변 사실성 사람 검토, 공식 RAG, 현장 사진 top-1/top-3,
휴대폰 촬영·네트워크·브라우저 흐름은 미실행입니다. 최종 AI 품질 점수는 없습니다.

Frontend는 로컬 모의 흐름, Backend 기본 실행은 RuleAgent/NoVision이므로 서비스 통합 완료 상태가 아닙니다.
사진 정답 자료 0건이고 서비스 20문항의 공식 근거도 확인 대기입니다.
현재 테스트 결과를 발표의 실제 AI 정확도나 사진 인식 정확도로 사용하지 않습니다.

v1(Agent 84c5f66)의 46개 단위 시험과 컴포넌트 결과는 과거 기록입니다.
v2는 계약·질문·기대값이 바뀐 새 기준선이므로 이전 점수와 개선율을 비교하지 않습니다.

최종 원격 확인에서 Agent 이력이 재작성되어 최신 커밋이 b5c5dde가 됐습니다.
기존 로컬 ce4cbc0와의 실행 코드는 같고 README 문구만 다릅니다.
원본 체크아웃을 유지하고 최신 원격의 별도 사본으로 위 Agent·컴포넌트·연결 검사를 재실행했습니다.
