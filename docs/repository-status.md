# 저장소 구조와 현재 버전

2026-10-22 동기화 및 검증 기준입니다.

| 저장소 | 현재 커밋 | 상태 |
|---|---|---|
| oneload-app | d45f466 | 로컬 main = origin/main. React·TypeScript·Vite, 모의 대화·사진·경로 |
| oneload-backend | 2502e65 | 로컬 main = origin/main. FastAPI·PostgreSQL, 기본 AI는 RuleAgent/NoVision |
| oneload_agent | 7b7501f | 로컬 main = origin/main. FAQ·README 추가, 실행 코드는 이전 평가 버전과 같음 |
| oneload-qa | 이 저장소 | 현 버전용 평가셋·실행기·문서·회귀 검사 |

Agent의 기존 main ce4cbc0과 원격은 공통 조상이 없는 이력이었습니다.
기존 이력을 백업 브랜치로 보존한 뒤 main을 원격 이력에 맞췄습니다.
이후 git pull --ff-only가 정상 완료됐습니다. [처리 기록](git-sync.md).

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
  data/maps/, migrations/, tests/  시범 지도·마이그레이션·44개 시험
oneload_agent/
  hangil_r2/agent.py, vision.py     LLMAgent·사진 특징 추출
  hangil_r2/backend/               Backend 계약·지도 타입 사본
  hangil_r2/knowledge.py           모의 지식·시각표 도구
  hangil_r2/config.py, llm.py       환경 설정·LLM 어댑터
  prompts/*_v3.md                  현재 프롬프트
  mocks/maps/seoul-station.json    Backend 지도 사본
  docs/FAQ.md                     7b7501f에 추가된 연결·동작·평가 안내
  eval/, tests/, docs/handoff.md   자체 질문 17문항·37개 시험·인계
qa/
  eval/                           서비스 초안·기능 TC·사진 명세·컴포넌트 v2
  scripts/run_checks.py           현재 커밋 검증·보고서 일괄 생성
  scripts/probe_integration.py    FAQ 핵심 분기·사진·수동 복구·장애 검사
  reports/                        공개용 현재 증거
  results/                        Git 제외 로컬 원본
~~~

## 현재 QA 변화

컴포넌트 v2의 질문·기대값은 그대로 유지했습니다.
API 연결 검사를 11개에서 20개로 늘려 교통카드 보유, 영어 직통, 비교 근거,
요금 보류, 미등록 POI, 사진 질문, 인식 결과 오류와 수동 복구를 추가했습니다.
개수 증가는 검증 범위 확장이며 이전 결과 대비 AI 성능 개선을 뜻하지 않습니다.

별도 R3 저장소는 이 폴더에 없습니다. 실제 모델·공식 RAG·현장 사진 정확도는 미측정입니다.
Frontend build·lint는 같은 커밋의 이전 결과를 유지하며 이번에 다시 실행하지 않았습니다.
