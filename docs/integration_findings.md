# 현재 통합 점검 결과

기준: Agent 250271e, Backend 493884f, Data 606f648, Frontend b111af6 (2026-10-23).
[계약 검사](../reports/contract-audit.json)와 [실제 API 연결 검사](../reports/integration-probe.json)를 함께 봅니다.

## 해결 확인 항목

| ID | 상태 | 확인 내용 |
|---|---|---|
| INT-01 | 해결 확인 | handle_message(ctx, message, image, selected_poi_id)와 AgentResult 반환 구조 일치 |
| INT-02 | 해결 확인 | AgentResponse·Slots·Source·위치 특징 스키마와 상태·의도 enum 일치 |
| INT-03 | 해결 확인 | 일반열차 슬롯은 allstop으로 통일 |
| INT-04 | 해결 확인 | 실제 Backend Slots로 일반열차 → 없어요 대화 및 슬롯 저장 통과 |
| INT-05 | 해결 확인 | 공유 지도에서 R2 VisionFeatures→Backend matcher 후보 생성. 고정 fixture와의 차이는 별도 기록 |
| INT-08 | 해결 확인 | 실제 Vision 장애를 Backend 예외로 포착하고 API가 503 / AI_SERVICE_UNAVAILABLE 반환 |

현재 Agent는 이전에 사용하던 pending_intent/pending_topic을 요구하지 않습니다.
현재 공개 계약을 유지하며 실제 실행 경로를 연결하는 것이 우선입니다.

## 남은 문제

| ID | 우선순위 | 재현·근거 | 필요한 작업 | 담당 협업 |
|---|---|---|---|---|
| INT-06 | P0 | 최신608a04c는 사진 위치·확정까지 서버 연결, 경로 findRoute·이벤트 로컬 실행 | 서버 경로·이벤트 화면 연결과 실제 서버 전체 흐름 검증 | R4·R5 |
| INT-07 | P0 | Backend app = create_app(), 내부 기본값 RuleAgent/NoVision | R2 패키지와 의존성 연결, 실제 Agent/Vision 주입, R3 검색 교체 | R2·R3·R4 |
| DATA-01 | 출시 전 확인 | 지도 통로·거리·방향과 예시 파노라마, 모의 지식 자료 | 공식 근거·답사·개인정보 검토 후 평가 정답 확정 | R1·R3·R6 |

INT-06/07이 남아 전체 실행 종료 코드는 1입니다.
QA의 R2 주입 API 20/20 통과는 운영 기본 연결·화면 완료를 뜻하지 않습니다.

## INT-08 수정과 QA #2 재검증

이전 Agent 7b7501f는 사본 VisionUnavailable을 던져 Backend가 잡지 못했고 HTTP 500을 반환했습니다.
Agent 250271e는 예외를 던지는 시점에 Backend의 실제 클래스를 선택해 이 문제를 수정했습니다.

그 뒤에도 QA의 정적 issubclass(사본, Backend) 비교는 INT-08을 실패로 보고했습니다.
[QA #2](https://github.com/team-onetruck/oneload-qa/issues/2)에서는 이 판정을 실제 동작 검사로 바꿨습니다.

1. LLMVision(FakeLLM(down=True)).extract에 합성 바이트를 전달합니다.
2. Backend의 VisionUnavailable로 잡히는지 확인하고 실제 예외 클래스와 판정 근거를 기록합니다.
3. 다른 예외나 장애 누락은 계약 실패로 처리합니다. Backend가 잡을 수 있는 하위 클래스는 통과합니다.
4. 일회용 DB의 실제 /localizations API에서 기대값을 유지해 503 / AI_SERVICE_UNAVAILABLE을 재확인합니다.

회귀 시험 5개를 추가해 QA 11/11, Agent 43/43, Backend 44/44, API 20/20 통과를 확인했습니다.
예외 메시지는 공개 증거에 남기지 않고 클래스만 기록합니다.
컴포넌트 v2의 질문·기대값·평가셋 SHA는 변경하지 않았습니다.

## 연결 때 함께 확인할 사항

- FAQ·README 예시는 같은 Vision을 LLMAgent.vision과 create_app(vision=...)에 모두 주입하도록 수정됐습니다.
  API-15로 대화 사진 읽기를 확인했으며 실제 기본 연결은 INT-07로 추적합니다.
- /messages의 15초 처리 예산을 실제 모델로 측정합니다. 이해·문장 생성에 사진 읽기가 추가되고,
  호출당 6초 timeout과 재시도가 있어 전체 요청 예산을 별도로 보장해야 합니다.
- 표준 QA 검색은 MockKnowledgeSearch입니다. 별도 MemorySearch 주입 API21/21을 확인했으며 운영 기본 연결과 실제 모델 품질은 미검증입니다.
- 실제 사진 입력, no_match, 503→수동 선택 화면, revision 충돌은 모바일 화면까지 확인합니다.
- Agent docs/handoff.md의 테스트 수 33건은 실제 실행 43건과 다릅니다. 보고서에는 실행 증거의 수를 사용합니다.

## 관련 수정 기록

- [QA #1](https://github.com/team-onetruck/oneload-qa/issues/1): oneload-data/maps 사용·입력 누락 사전 검사 반영.
- [Agent #1](https://github.com/team-onetruck/oneload_agent/issues/1): 사진 장애 예외 처리 수정, 이번 API 검사 통과.
- [Agent #2](https://github.com/team-onetruck/oneload_agent/issues/2): LLMAgent.vision 연결 예시 보완.
- [Agent #3](https://github.com/team-onetruck/oneload_agent/issues/3): 자체 호환성 도구의 공유 지도 경로 수정.

실제 공유 지도와 Backend·Agent 시험 fixture는 목적이 다르므로 파일 차이만으로 계약 실패를 만들지 않습니다.
실제 지도 입력·버전·해시는 reports/data-validation.json과 각 단계 메타데이터로 확인합니다.


## App 후속 검토 (최신 b111af6)

App b111af6은 세션 생성에 이어 HTTP 채팅·POI 칩·언어 변경을 서버에 연결했습니다. 사진 위치·경로 화면의 로컬 흐름이 남아 INT-06은 유지합니다.
이전 [App 검토](../reports/app-review.json)는8c88f89의 역사적 CI 증거입니다. App #11은 문서 수정으로 closed이며, 최신 App의 실제 서버·모바일 E2E를 이번 QA에서 실행한 것은 아닙니다.

## QA #3 검색·근거 보완

[변경 및 판정](issue3-resolution.md): service v2·근거20건·독립검색32문항·RAG API21건을 추가했습니다.
범위밖 검색 오탐은 [RAG #3](https://github.com/team-onetruck/oneload-rag/issues/3)에 등록했습니다. 임계값 확정과 INT-07 이후 운영 경로 재검사는 남아 있습니다.

## 최신 소스 재확인: App608a04c / RAG47ab39f

[재확인 기록](../reports/source-review-20261023.json). 사진 위치·사용자 선택 확정·503 직접 선택은 App에 연결됐다. INT-06의 남은 범위는 서버 경로·이벤트 및 실제 서버 전체 흐름이다. 위 API 통과 수는 기존11:04 실행 기준이며 이번 소스 관찰로 새 통과 처리하지 않는다.
RAG는 검색 코드·근거가 그대로여서 호텔 가격·잔여석 검색 오탐이 재현됐다. RAG #3/QA #3은 미완료 상태를 유지한다. 최신 App608a04c verify342건은 통과했고 E2E는 확인 시 진행 중이다. 이전32f5f67은327건+mock 시작 화면1건 통과다. RAG는88건+MCP HTTP 점검 통과이며 운영 조립 완료를 의미하지 않는다. App 경로·이벤트 화면 연결은 PR#17 open으로 main 미반영이다.
