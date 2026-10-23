# 최신 통합 점검 — 2026-10-23 17:00 KST

Backendb1aa5f5·Data9fc786e·Agenteca420e에서 **INT-02 계약 및 여러 턴 슬롯 유실은 해결 확인**했다. Frontend 생성 타입은 구계약이라 Agent #7은 잔여 동기화 작업으로 유지한다.

새 **Backend #2**: 미반납→반납 완료 대화 후 응답 슬롯yes와 달리 계획facts는NOT_REFUNDED이며 환급 추천이 남는다. 경계v2 API-26으로 모의26/27·공식 MemorySearch27/28에서 재현했다. [새 증거](../reports/data-backend-review-20261023.json).

Data #2의 출구/반납기 통로 단절·INT-07 운영 공식 RAG 미연결·DATA-01 현장 자료는 유지한다. QA44·Backend68·Agent47·Data3·component20/21 통과는 실제 AI/화면 품질 합격이 아니다. 최신 배포는코드와일치하며 과거아래의500·skipped는수정전관찰이다.

---

## 과거 통합 점검: 2026-10-23 16:16 KST

**INT-02 재발, P0:** Agenteca420e의 intent3개·슬롯4개 확장과 Backend15ddd9f의 공개 계약이 다르다. 기존 API 시험에서500, 다음 context에서 슬롯 소실을 확인했다. [Agent #7](https://github.com/team-onetruck/oneload_agent/issues/7), [새 감사](../reports/architecture-contract-audit-20261023.json).

**새 목적지 그래프 단절:** Data3b5ef0e의 반납기/1번 출구로 가는 경로가 line1-gates 외 주요 출발점에서 없다. [Data #2](https://github.com/team-onetruck/oneload-data/issues/2), [실제 경로 함수 증거](../reports/architecture-boundaries-20261023.json).

INT-07 partial·DATA-01·Agent #5는 그대로다. QA44·Agent47·Data3·component20/21 통과, Backend50/51·후속 API NOT_RUN이다. baseline은 과거 완결 실행으로 보존했다. [현재 전체 아키텍처](architecture-current-20261023.md)를 따른다. 아래의 INT-02 해결·API20/21 통과 등은 **15:42 이전 조합의 기록**이며 최신 조합 판정에 적용하지 않는다.

---

## 이전 통합 점검 결과


후속 의존성 검토: Backend15ddd9f·Agent5038b5c·Infra6cf4a65에서 QA42/Backend51/Agent43·모의 API20·RAG 주입 API21을 다시 확인했다. 기능 코드와 아래 INT-07 partial 판정은 동일하다. [최신 증거](../reports/dependency-review-20261023.json)를 따른다.

기준: Agenta089746(개발 pin7f116de와 패키지 코드 동일), Backendf9d790f, Data606f648, Frontend42455dc, RAG8c8e902 (2026-10-23 15:29 KST).
[계약 검사](../reports/contract-audit.json)와 [실제 API 연결 검사](../reports/integration-probe.json)를 함께 봅니다.

## 해결 확인 항목

| ID | 상태 | 확인 내용 |
|---|---|---|
| INT-01 | 해결 확인 | handle_message(ctx, message, image, selected_poi_id)와 AgentResult 반환 구조 일치 |
| INT-02 | 해결 확인 | AgentResponse·Slots·Source·위치 특징 스키마와 상태·의도 enum 일치 |
| INT-03 | 해결 확인 | 일반열차 슬롯은 allstop으로 통일 |
| INT-04 | 해결 확인 | 실제 Backend Slots로 일반열차 → 없어요 대화 및 슬롯 저장 통과 |
| INT-05 | 해결 확인 | 공유 지도에서 R2 VisionFeatures→Backend matcher 후보 생성. 고정 fixture와의 차이는 별도 기록 |
| INT-06 | 소스 연결 확인 | QA #4 수정. 검토한 HTTP 호출 경로·런타임 해시 일치. 실제 브라우저 인수는 별도 NOT_RUN |
| INT-08 | 해결 확인 | 실제 Vision 장애를 Backend 예외로 포착하고 API가 503 / AI_SERVICE_UNAVAILABLE 반환 |

현재 Agent는 이전에 사용하던 pending_intent/pending_topic을 요구하지 않습니다.
현재 공개 계약을 유지하며 실제 실행 경로를 연결하는 것이 우선입니다.

## 남은 문제

| ID | 우선순위 | 재현·근거 | 필요한 작업 | 담당 협업 |
|---|---|---|---|---|
| INT-07 | P0·partial | 운영 Agent/Vision 조건부 연결 완료, 지식은 MockKnowledgeSearch | R3 공식 검색 연결 후 운영 API 재검사 | R2·R3·R4 |
| DATA-01 | 출시 전 확인 | 지도 통로·거리·방향과 예시 파노라마, 모의 지식 자료 | 공식 근거·답사·개인정보 검토 후 평가 정답 확정 | R1·R3·R6 |

현재 P0는 INT-07이며 전체 실행 종료 코드는1입니다. 새 Frontend 런타임 소스가 미검토이면 review_required로 별도 중단합니다.
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


## App 과거 검토 (b111af6)

App b111af6은 세션 생성에 이어 HTTP 채팅·POI 칩·언어 변경을 서버에 연결했습니다. 사진 위치·경로 화면의 로컬 흐름이 남아 INT-06은 유지합니다.
이전 [App 검토](../reports/app-review.json)는8c88f89의 역사적 CI 증거입니다. App #11은 문서 수정으로 closed이며, 최신 App의 실제 서버·모바일 E2E를 이번 QA에서 실행한 것은 아닙니다.

## QA #3 검색·근거 보완

[변경 및 판정](issue3-resolution.md): service v2·근거20건·독립검색32문항·RAG API21건을 추가했습니다.
범위밖 검색 오탐은 [RAG #3](https://github.com/team-onetruck/oneload-rag/issues/3)에 등록했습니다. 임계값 확정과 INT-07 이후 운영 경로 재검사는 남아 있습니다.

## QA #4 수정 당시 판정 (이전 전체 검사)

최신 Appb5d6835는 사진·확정·서버 경로·시작/도착/취소·재탐색의 HTTP 호출 경로를 연결했다. mock 문자열만으로 미연결이라고 판정하던 QA #4를 수정했다. [판정 절차](issue4-resolution.md)·[Git 스냅샷 증거](../reports/frontend-wiring-review.json)를 따른다. 실제 서버·휴대폰 전체 인수는 별도다.
Backendc9b8d8a까지 포함해 QA28/28·Backend48/48·모의 API20/20·RAG 주입 API21/21을 재확인했다. 기본 Agent/Vision 조립은 바뀌지 않아 INT-07은 유지한다. RAG 검색 오탐/임계값 미승인도 QA #3·RAG #3으로 계속 추적한다.

## RAG 답글 후 이전 판정 (13:33)

2026-10-23 13:33 KST에 Agent54c321f의 패키지 자산 경로를 반영해 전체 검사를 갱신했다. QA38/38·Agent43/43·Backend48/48·컴포넌트20시나리오/21턴·모의 API20/20·별도 RAG API21/21이다. App2666e44는 소스 wired이며 실제 브라우저 인수는 NOT_RUN, 운영 INT-07도 그대로다.

RAG 원래 호텔 가격·빈 좌석은 빈 결과로 개선됐으나 R6 신규 holdout40문항에서 오탐3·정상 누락3이 남았다. top3 17/20·범위밖 빈 결과17/20으로 임계값 운영 확정은 보류하고 RAG #3·QA #3은 open이다. [동결 절차·전후 증거](rag-issue3-revalidation.md)를 따른다. 실제 모델·pgvector 품질은 이 검사 범위가 아니다.

## 현재 판정 (15:29 KST)

QA42·Agent43·Backend51·컴포넌트20/21·모의 API20·RAG 주입 API21을 재확인했다. App ApiAdapter 단일 흐름·outbox를 검토해 새 profile42455dc으로 wired다. 운영 entrypoint 두 키 분기를 FakeLLM으로 실행해 Agent/Vision 공유를 확인했다. 배포 GET에서도 활성 구성 표시를 확인했지만 공식 R3 검색은 미연결이라 INT-07 partial이며 전체 exit1이다.

App #32·Agent #6의 초기 배포 전달 토큰 문제는 공용 reusable 배포 전환과 최신 실행 성공으로 해결 확인해 닫았다. [현재 구현·토론 맥락·한계](current-implementation-20261023.md)를 따른다.
