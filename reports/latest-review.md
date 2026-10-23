# 최신 QA — 2026-10-23 15:29 KST

[현재 구현과 토론 맥락](../docs/current-implementation-20261023.md) · [소스·CI·검증 범위](current-system-review-20261023.json) · [배포 GET 확인](server-readonly-20261023.json)

App42455dc·Backendf9d790f·Agenta089746·Data606f648·Infra8f03327을 사용했다. 개발 pin7f116de와 Agent a089746의 패키지 코드는 같고 문서/CI가 다르다. 공용 배포는 Agent main을 체크아웃해 개발 pin을 덮어쓴다.

| 검사 | 결과 |
|---|---|
| QA | 42/42, skip0 |
| 데이터 | 3/3 |
| Agent | 43/43 |
| Backend | 51/51 |
| component v2 | 20/20시나리오·21/21턴 |
| 모의 검색 API | 20/20 |
| RAG8c8e902 MemorySearch0.25 주입 API | 21/21 |
| Frontend 호출 경로 | ApiAdapter 단일 흐름의 새 profile42455dc, wired |
| 운영 entrypoint | FakeLLM으로 실제 전역 app 조립 검사, Agent·Vision 조건부 연결/공유 확인 |

[기준선](baseline.json) · [감사](contract-audit.json) · [RAG 주입 API](rag-integration-probe.json)

**INT-07은 부분 완료**다. 운영은 키가 있으면 LLMAgent·LLMVision, 없으면 RuleAgent·NoVision이다. 따라서 과거의 무조건 RuleAgent/NoVision 판정은 최신에 적용하지 않는다. 다만 검색이 MockKnowledgeSearch여서 R3 운영 연결은 미완료이고 전체 exit1이다. DATA-01과 사람 정답 검토도 남는다.

App 최신 CI는 단위429·E2E11(mock7+모의 HTTP4), Agent CI는 자체/Backend 호환/API 시험·배포가 모두 통과했다. 공용 reusable 배포로 GH_TOKEN 전달 경로를 제거해 App #32·Agent #6을 닫았다. Backend 최신 CI도 시험·이미지·배포 성공이다. App 최신 배포39911399631의 서버 실행 커밋은 위 조합과 일치한다. 홈/언어 메뉴·기기 언어 감지도 반영됐다.

배포 첫 화면/health/OpenAPI는 GET만 실행해200·DB ok·LLMAgent/LLMVision 표시를 확인했다. R2의 실제 OpenAI 메시지1회 확인 문서는 작성자 보고로 구분하며 이번 R6가 반복하지 않았다.

사용자 토론은 참고 맥락이다. 현재는 모의 고정 사진 결과와 Live 인식이 구분되고, 실제 안내는 단계 문구+도식형 노선+거리뷰다. 평면도·도착지 입구 전용 사진·완전한 가상 역을 구현하거나 인수조건을 확정한 것으로 쓰지 않는다.

실제 모델/임베딩 호출0회, 현장 사진 정답0건, component21턴 사람 검토 대기다. 이전 retrieval v2 top3 17/20·범위밖 빈 결과17/20은 노출된 과거 검색 증거로 유지했다. Agent #5/RQ-32와 RAG #3·QA #3은 미완료다. 최초 Backend 실행기 의존성 오류는 보완 후 새 일회용 DB로 재실행했으며 실패한 초기 시도를 제품 결함이나 통과 수치로 집계하지 않았다.
