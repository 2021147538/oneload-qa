# 현재 구현 확인 — 2026-10-23 15:31 KST

[커밋·검사·CI 근거](../reports/current-system-review-20261023.json). 사용자가 공유한 토론은 현재 구현을 이해하는 맥락으로만 참고했다. 더미 위치·텍스트 전용 안내·가상 역 구현을 확정 요구로 적용하거나 기존 인수조건을 변경하지 않았다.

## 현재 동작

| 항목 | 실제 구현 | 확인 범위·한계 |
|---|---|---|
| 입력과 질문 | 한/영 대화, 열차/교통카드 되묻기, 사진 첨부, 안내 중 채팅 복귀 | FakeLLM 흐름·App CI. 실제 외국인 사용성은 미측정 |
| 모의 위치 찾기 | mock adapter가 사진 시나리오별 고정 후보를 반환 | 사진 내용을 인식한 성능으로 집계하지 않음 |
| Live 위치 찾기 | JPEG → LLMVision의 글자/시설 특징 → 지도 matcher → 후보 → 사용자 확정 | 배포 OpenAPI에 LLMVision 활성 표시. 이번 실제 사진/모델 호출은 안 함 |
| 안내 | 서버의 등록 노드 경로·층·거리·단계 문구, 도식형 노선, 구간 거리뷰 | 실제 역 평면도 이미지를 그리는 구현은 아님 |
| 사진 | 구간 출발 노드의 파노라마와 예시 사진 표시 | 실제 서울역 도착지 입구 사진 전용 카드/출발·도착 사진 비교는 미구현. 데이터6장은 예시 |
| SOP | 표 구매/이용 설명과 출처, 표 사는 곳 도착 후 구매 방법→승강장 후속 질문 | 운영 검색은 데모 문서. 실제 기기 버튼/요금 근거·사람 사실성 검토 대기 |
| LangGraph | 사진 특징 읽기→의도 이해→슬롯 갱신→안전/되묻기/답변/목적지 분기 | 실제 경로 계산은 Backend 등록 그래프, LLM이 임의 경로 생성하지 않음 |

위치나 절차가 불명확하면 질문하고 사용자에게 후보 확정을 받는 구조는 이미 있다. 도착/다음 단계는 버튼으로 사용자가 진행하며 연속 위치 추적·자동 도착 판정이 아니다. 전체 가상 서울역·AR 시뮬레이터를 새로 만든 상태도 아니다.

## 직전 버전 이후 바뀐 점

App42455dc은 mock 규칙을 ApiAdapter 구현으로 옮겨 화면과 store가 HTTP/mock 모두 같은 흐름을 사용한다. Live/Demo 라벨을 구분하고, 경로 이벤트 outbox로 시작/도착 순서·진행 중 묶음 중복을 보완했다. 홈/언어 햄버거 메뉴와 기기 언어 감지도 추가됐다. changeLang/PATCH·기존 reset으로 이어지는 호출을 검토해 최종 INT-06 profile42455dc를 추가했다.

Backendf9d790f는 키가 있으면 LLMAgent+공유 LLMVision을 운영 entrypoint에 주입한다. 키가 없을 때만 RuleAgent/NoVision으로 대체한다. 따라서 이전의 "운영은 항상 RuleAgent/NoVision" 판정은 최신 상태가 아니다. **검색은 여전히 MockKnowledgeSearch여서 INT-07은 부분 완료이며 R3 운영 연결은 미완료**다.

Agent 최신a089746의 패키지 코드·프롬프트·mock 자산은 개발 pin7f116de와 같고 문서/CI가 바뀌었다. 공용 배포는 개발 pin을 체크아웃한 Agent main으로 덮어쓰며 최신 배포 a089746을 확인했다. R2 문서는 실제 OpenAI 메시지1회 확인을 보고했지만, R6가 그 호출을 반복하거나 서비스 정확도를 측정한 것은 아니다. RAG8c8e902는 그대로이고 Agent #5의 근거 판단/인용 처리도 미반영이다.

## 확인 결과

- QA42/42, Agent43/43, Backend51/51, 데이터3/3, component v2 20시나리오/21턴, 모의 API20/20, 별도 RAG 주입 API21/21.
- actual entrypoint를 FakeLLM으로 실행해 키 유무 분기와 공유 Vision/LLM을 확인했다. 사용하지 않는 factory 선언만으로 연결 통과를 주지 않는다. 새 Backend 의존성으로 QA 검사 경로도 보완했다.
- 최신 App CI429건·E2E11건(mock7+모의 HTTP4), Agent의 자체/Backend 호환/API 시험과 배포가 모두 통과했다. 초기 GH_TOKEN 전달 실패는 공용 reusable workflow로 바뀌어 [App #32](https://github.com/team-onetruck/oneload-app/issues/32)·[Agent #6](https://github.com/team-onetruck/oneload_agent/issues/6)을 해결 확인 후 닫았다.
- [App 최신 배포](https://github.com/team-onetruck/oneload-app/actions/runs/39911399631)에서 Backendf9d790f·Agenta089746·App42455dc·Infra8f03327·Data606f648 checkout과 health 성공을 확인했다. R6가 배포를 실행한 것은 아니다.
- 배포 첫 화면/health/OpenAPI를 GET으로만 확인해 모두200, DB ok, LLMAgent·LLMVision 표시를 확인했다([증거](../reports/server-readonly-20261023.json)). 실제 대화/사진, 브라우저 전체 인수·현장 정확도는 이번 미실행이다.

R6의 실제 모델/임베딩 호출0회, 현장 사진 정답0건, 사람 검토 대기를 유지한다. 이전 검색 v2 top3 17/20·범위밖 빈 결과17/20도 과거 노출 회귀 증거로 보존했고 새 독립 검증으로 소개하지 않았다.

## 다음 QA 초점

R3 공식 검색 운영 연결·Agent 답변 보류/인용 처리와 실제 서버-브라우저 대표 흐름이 우선이다. 시연에서는 모의 사진 결과·예시 파노라마·실제 인식 결과를 구분해야 한다. 도착지 입구 사진이나 실제 평면도 방식은 토론의 검토 후보이며 이번 확인으로 새 구현·합격 조건을 확정하지 않았다.

## 후속 의존성 변경

Backend15ddd9f·Agent5038b5c·Infra6cf4a65는 제품 동작 코드 변경 없이 개발/배포 설치를 정리했다. 로컬은 ../oneload_agent editable, CI/배포는 scripts/pin_agent.sh의 정확한 SHA URL이다. 두 설치 모드와 자산 포함을 분리된 복사본에서 검증했다. 최신 전체 QA와 CI 배포는 통과했고 운영 검색 demo·현장/실제 모델 품질 대기는 그대로다. [최신 설치/검사 증거](../reports/dependency-review-20261023.json)를 따른다. 앞의7f116de 개발 pin 설명은 과거 버전이다.
