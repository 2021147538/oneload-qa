# 저장소 구조와 현재 버전

2026-10-22에 원격을 확인했습니다. Frontend·Backend는 로컬 main과 origin/main이 같습니다.
Agent 원격은 이력 재작성으로 b5c5dde가 되었고 로컬 main은 ce4cbc0에 유지했습니다.
두 버전의 파일 차이는 README 마지막 문구 1건뿐입니다. 최신 원격을 별도 사본으로 시험했으며, 원래 세 저장소 작업 트리는 변경하지 않았습니다.

| 저장소 | 커밋 | 현재 상태 |
|---|---|---|
| oneload-app | d45f466 | React·TypeScript·Vite. 대화·사진 인식·경로는 메모리 모의 구현 |
| oneload-backend | 2502e65 | FastAPI·PostgreSQL. Swagger 한국어·수동 시험 편의 개선, 기본 AI는 대역 |
| oneload_agent | b5c5dde | Backend 계약에 맞춰 재구성, 프롬프트 v3, .env 자동 준비 지원 |
| oneload-qa | 이 저장소 | 독립 QA 자료·평가셋·계약 및 API 연결 검사 |

## 주요 구조

~~~text
oneload-app/src/
  store.tsx, assistant.ts, data.ts   모의 세션·AI·사진·출처
  route.ts, streetview.tsx          경로·360도 거리뷰
oneload-backend/
  app/api/                         세션·대화·사진·지도·경로 API
  app/ai/                          계약·guard·RuleAgent·NoVision
  app/domain/                      지도·경로·위치 매칭·상태
  app/openapi.py                   Swagger 입력·설명 보완
  data/maps/, migrations/, tests/  시범 지도·실제 DB 마이그레이션·44개 시험
oneload_agent/
  hangil_r2/agent.py               LangGraph LLMAgent
  hangil_r2/vision.py              사진→글자·시설 특징
  hangil_r2/backend/               Backend 계약·지도 타입 사본
  hangil_r2/knowledge.py           모의 지식·시각표 도구
  hangil_r2/config.py, llm.py       환경 설정·LLM 어댑터
  prompts/*_v3.md                  현재 프롬프트
  mocks/maps/seoul-station.json    Backend 지도 사본
  eval/, tests/, docs/handoff.md   자체 평가 17문항·37개 시험·인계
qa/
  eval/                           서비스 초안·기능 TC·사진 명세·컴포넌트 v2
  scripts/                        계약·컴포넌트·일회용 DB·API 연결 실행기
  reports/                        공개용 최신 증거와 점검 결과
  results/                        Git 제외 로컬 실행 원본
~~~

## 지난 기준 이후 변경

Agent 84c5f66→b5c5dde은 공개 계약과 내부 구조 변경입니다.
기존 Agent/SessionContext/MockPoiSearch와 별도 localization 모듈 대신
LLMAgent·LLMVision·Backend 계약 사본을 사용합니다. 상태·슬롯·POI ID·지도도 Backend와 맞췄습니다.
따라서 QA 실행기와 컴포넌트 평가셋을 v2로 갱신했습니다. 이전 v1은 archive에 보존했습니다.

Backend bc64318 이후에는 launchd 재시작 대기와 Swagger 문서·입력 UX 변경이 있습니다.
최신 버전에서도 기존 44개 시험을 재실행해 통과했습니다.
Frontend는 같은 커밋이므로 이전 build·원본 소스 lint 결과를 유지합니다.
브라우저·휴대폰 통합 동작은 아직 확인하지 않았습니다.

별도 R3 저장소는 이 폴더에 없습니다. 실제 모델·공식 RAG·현장 사진 정확도는 미측정입니다.
