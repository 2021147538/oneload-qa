# 현재 버전 점검 결과 — 2026-10-23

| 대상 | 버전·대상 | 결과 |
|---|---|---|
| QA 회귀 시험 | 지도 입력 6건·사진 장애 예외 판정 5건 | 11/11 통과 |
| 데이터 검사 | oneload-data 606f648 | 3/3 통과 |
| Backend | a82b7be | 기존 44/44 시험 통과, 고정 fixture·일회용 DB |
| Agent | 250271e | 기존 43/43 시험 통과, FakeLLM |
| 컴포넌트 v2 | 실제 공유 지도 + Backend·Agent | 20/20 시나리오·21/21 턴 자동 검사 통과 |
| R2↔Backend API | 실제 공유 지도 + 일회용 DB | 20/20 통과, 사진 장애 503 확인 |
| Frontend | bc2d9f1 | 이번 build·브라우저 검사 미실행 |
| Infra | 3dcccd8 | 커밋 기록, 배포 실행 미실행 |

[실행 요약](baseline.json) · [데이터 검사](data-validation.json) ·
[계약 감사](contract-audit.json) · [API 증거](integration-probe.json) ·
[컴포넌트 정보](component-metadata.json) · [컴포넌트 CSV](component-results.csv)

## QA #2: 사진 장애 판정 수정

Agent 250271e는 사진 장애 시 Backend의 실제 예외를 던지도록 수정됐습니다.
기존 QA의 사본 클래스 비교가 이를 실패로 보고해 실제 장애 발생 시 잡히는 예외를 검사하도록 바꿨습니다.
계약 감사 INT-08이 통과하고 실제 API도 503 / AI_SERVICE_UNAVAILABLE을 반환했습니다.

정상 Agent·사본 예외·다른 예외·장애 누락·Backend 예외 하위 클래스를 회귀 시험으로 확인했습니다.
잘못된 예외는 계속 실패로 잡으며 예외 메시지는 공개 증거에 남기지 않습니다.
TC-11은 API 장애 처리 통과와 화면 복구 미실행을 구분해 PARTIAL로 갱신했습니다.
컴포넌트 질문·기대값·평가셋 SHA는 이전 v2와 같습니다.

## 검사 입력과 남은 문제

실제 통합·컴포넌트 입력은 oneload-data/maps, Backend 자체 시험은 tests/fixtures/maps입니다.
관련 저장소 5개의 커밋, 지도·고정 fixture·사진 해시를 기록하고 단계별 입력 일치를 대조했습니다.
지도 version은 2026-10-22.1, 노드 10·엣지 9·POI 4·파노라마 6개입니다.
고유 사진 파일 4개가 모두 존재하고 Backend 모델·데이터 스키마도 일치합니다.

Frontend 모의 구현(INT-06), Backend 기본 RuleAgent/NoVision(INT-07) 때문에 전체 종료 코드는 1입니다.
현장 자료 확인(DATA-01)도 남아 있습니다. INT-08은 더 이상 미해결 실패로 집계하지 않습니다.

관련 이슈:

- [QA #2: 사진 장애 거짓 실패](https://github.com/team-onetruck/oneload-qa/issues/2) — 이번 수정 대상
- [QA #1: 지도 분리 대응](https://github.com/team-onetruck/oneload-qa/issues/1) — 기존 수정 유지
- [Agent #1: 사진 장애 예외](https://github.com/team-onetruck/oneload_agent/issues/1) — Agent 수정 후 재검증 통과
- [Agent #2: 사진 질문 연결 예제](https://github.com/team-onetruck/oneload_agent/issues/2) — 연결 예시 보완
- [Agent #3: 자체 호환성 도구의 옛 지도 경로](https://github.com/team-onetruck/oneload_agent/issues/3) — 공유 지도 경로 수정
- [Infra #1: 문서 공개 범위 표기](https://github.com/team-onetruck/oneload-infra/issues/1) — 별도 추적

## 판정 범위

FakeLLM·MockKnowledgeSearch·합성 JPEG 검사이며 실제 LLM/VLM 호출은 0회입니다.
모든 파노라마 참조는 예시 사진이고 현장 사진 정답 자료는 0건입니다.
실제 AI 품질·R3 검색 연결·현장 인식 정확도·휴대폰 UI·운영 배포는 이번 검사에서 미측정입니다.
