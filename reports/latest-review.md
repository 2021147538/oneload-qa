# 현재 버전 점검 결과 — 2026-10-22

| 대상 | 커밋 | 결과 |
|---|---|---|
| Frontend | d45f466 | 같은 커밋의 이전 build·lint 결과 유지. 이번 실행 제외 |
| Backend | 2502e65 | 기존 44/44 시험 통과, 일회용 PostgreSQL 17 |
| Agent | 7b7501f | 동기화한 로컬 main에서 기존 37/37 시험 통과 |
| R6 컴포넌트 v2 | 위 Backend·Agent | 20/20 시나리오·21/21 턴 자동 검사 통과 |
| R2↔Backend 연결 | 위 Backend·Agent | 19/20 확인 통과, 사진 인식 장애 처리 1건 실패 |

[실행 요약](baseline.json) · [계약 증거](contract-audit.json) ·
[API 연결 증거](integration-probe.json) · [컴포넌트 정보](component-metadata.json) ·
[컴포넌트 결과 CSV](component-results.csv)

## 이번 변경

Agent main의 unrelated histories 문제를 기존 이력 백업 후 해소했습니다.
7b7501f는 FAQ·README 변경이며 실행 코드는 이전 평가 버전과 같습니다.
QA는 동기화한 원본 저장소를 대상으로 다시 실행했습니다.

API 검사를 11개에서 20개로 확장했습니다.
일반열차 카드 있음/없음, 영어 직통, 비교 근거 유무, 요금 보류,
미등록 POI 거부, /messages 사진 질문 전달, 형식이 깨진 사진 결과와 수동 복구를 확인했습니다.
새 검사 9개 모두 통과했으며, [FAQ 연결표](../docs/faq-qa-traceability.md)에 근거를 남겼습니다.

run_checks.py를 추가해 단위 시험·계약·컴포넌트·DB/API 검사와 공개 증거 갱신을 묶었습니다.
실패한 단계도 기록하고, 누락되거나 서로 다른 커밋의 증거로 보고서를 갱신하지 않습니다.

## 남은 문제

INT-08: 사진 모델 접속 장애는 기대한 503 AI_SERVICE_UNAVAILABLE 대신 HTTP 500을 반환합니다.
R2와 Backend의 VisionUnavailable이 서로 다른 클래스라 except가 받지 못합니다.
정상 인식·형식 오류·수동 복구 통과와 별도로 이 실패를 유지했습니다.
[원인과 재현](../docs/integration_findings.md).

Frontend 모의 흐름(INT-06), Backend 기본 RuleAgent/NoVision(INT-07), 공식·현장 자료(DATA-01)도 남아 있습니다.
따라서 전체 실행 종료 코드는 1이며 서비스 통합 완료로 표시하지 않습니다.

## 판정 범위

FakeLLM·MockKnowledgeSearch·합성 JPEG 검사입니다. 실제 LLM/VLM 호출은 0회입니다.
사람이 확인한 AI 품질 점수, 공식 RAG, 현장 사진 정확도, 모바일 브라우저 동작은 미측정입니다.
사진 정답 자료는 0건이고 서비스 20문항의 공식 근거는 검토 대기입니다.
컴포넌트 평가셋 SHA는 이전 v2와 같고, API 확인 개수 증가는 검사 범위 확장입니다.
