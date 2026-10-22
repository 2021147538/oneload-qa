# 현재 버전 점검 결과 — 2026-10-22

| 대상 | 버전·대상 | 결과 |
|---|---|---|
| QA 회귀 시험 | 지도 분리 대응 실행기 | 6/6 통과 |
| 데이터 검사 | oneload-data 606f648 | 3/3 통과 |
| Backend | a82b7be | 기존 44/44 시험 통과, 고정 fixture·일회용 DB |
| Agent | 7b7501f | 기존 37/37 시험 통과, FakeLLM |
| 컴포넌트 v2 | 실제 공유 지도 + Backend·Agent | 20/20 시나리오·21/21 턴 자동 검사 통과 |
| R2↔Backend API | 실제 공유 지도 + 일회용 DB | 19/20 통과, INT-08 실패 유지 |
| Frontend | bc2d9f1 | 이번 build·브라우저 검사 미실행 |
| Infra | 3dcccd8 | 커밋 기록, 배포 실행 미실행 |

[실행 요약](baseline.json) · [데이터 검사](data-validation.json) ·
[계약 감사](contract-audit.json) · [API 증거](integration-probe.json) ·
[컴포넌트 정보](component-metadata.json) · [컴포넌트 CSV](component-results.csv)

## 지도 분리 대응

QA issue #1의 옛 Backend 지도 경로 참조를 수정했습니다.
실제 통합·컴포넌트 입력은 oneload-data/maps, Backend 자체 시험은 tests/fixtures/maps입니다.
선택한 지도가 없으면 검사 전에 읽기 쉬운 오류로 중단하며 --map-dir도 지원합니다.

관련 저장소 5개의 커밋, 지도의 ID·버전·SHA256, 고정 fixture SHA256,
사진 파일 해시를 기록하고 단계별 증거가 같은 입력인지 대조했습니다.
이번 지도의 version은 2026-10-22.1, 노드 10·엣지 9·POI 4·파노라마 6개입니다.
참조된 고유 사진 파일 4개가 모두 존재하고 Backend 모델·데이터 스키마도 일치합니다.

QA 회귀 시험에는 데이터 저장소 누락, 선택 지도 누락, 명시적 지도 버전 선택,
빈 지도 폴더, 스키마 변경, 사진 누락을 포함했습니다.
컴포넌트 질문·기대값·평가셋 SHA는 이전 v2와 같습니다.

## 남은 통합 문제

사진 모델 접속 장애 INT-08은 기대 503 AI_SERVICE_UNAVAILABLE 대신 HTTP 500을 반환합니다.
이 실패를 유지하므로 전체 실행 종료 코드는 1입니다.
Frontend 모의 구현(INT-06), Backend 기본 RuleAgent/NoVision(INT-07), 현장 자료(DATA-01)도 남아 있습니다.

관련 이슈:
- [QA #1: 지도 분리 대응](https://github.com/team-onetruck/oneload-qa/issues/1) — 이번 수정 대상
- [Agent #1: 사진 장애 예외](https://github.com/team-onetruck/oneload_agent/issues/1)
- [Agent #2: 사진 질문 연결 예제](https://github.com/team-onetruck/oneload_agent/issues/2)
- [Agent #3: 자체 호환성 도구의 옛 지도 경로](https://github.com/team-onetruck/oneload_agent/issues/3)
- [Infra #1: 문서 공개 범위 표기](https://github.com/team-onetruck/oneload-infra/issues/1)

QA는 자체 계약 감사를 실행하며, Agent 저장소의 별도 호환성 도구 문제는 해당 이슈로 추적합니다.

## 판정 범위

FakeLLM·MockKnowledgeSearch·합성 JPEG 검사이며 실제 LLM/VLM 호출은 0회입니다.
모든 파노라마 참조는 예시 사진이고 현장 사진 정답 자료는 0건입니다.
실제 AI 품질, 공식 RAG, 현장 인식 정확도, 휴대폰 UI·운영 배포 완료를 나타내는 결과가 아닙니다.
