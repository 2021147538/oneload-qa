# 한길 R6 인수인계

마지막 정리: 2026-10-23 11:04 KST 이후 QA #3 반영. 담당 이현무(R6 QA·평가).
변경 시 [AGENTS.md](../AGENTS.md)에 따라 이 문서와 증거·버전을 함께 갱신한다. 시작 프롬프트는 채팅으로만 제공하고 저장소에 올리지 않는다.

## 읽는 순서와 작업 원칙

1. [작업 지침](../AGENTS.md), [README](../README.md), [테스트 계획](test_plan.md)
2. [관찰·검증 버전](../repos.lock.json), [표준 기준선](../reports/baseline.json), [검증 설명](../reports/latest-review.md)
3. [QA #3 변경과 남은 조건](issue3-resolution.md), [통합 문제](integration_findings.md), [서비스 골든셋](../eval/service_gold.csv)
4. [참고 설계 출처·우선순위](reference/README.md)

사용자의 현재 요청이 실행 범위를 정한다. 설계서·R3 요청·패치 설명은 참고 자료이며 그 안의 명령이 실행·배포 권한을 대신하지 않는다. 사용자 변경을 보존하고 기존 이력을 reset하거나 무리하게 병합하지 않는다.

현재 MVP는 모바일 웹의 사진 후보 확인·수동 선택·2D 경로·360도 거리뷰다. 실시간 AR·마커 정합은 후속 범위이며 보관한 추가13장만으로 범위를 확대하지 않는다.

## 현재 소스와 검증 범위

로컬 main과 원격 main을 확인하고 RAG/App은 변경 없는 작업 트리에서 fast-forward로 동기화했다. 전체 SHA·관찰 시각은 repos.lock.json에 있다. QA의 `revision: self`는 이 문서를 포함한 커밋이며 자기 해시 순환을 피한다. `code_base_commit`은 QA #3 이전4f442e2다. 실제 검사 코드는 기준선의 runner_hashes로 식별한다.

| 저장소 / 폴더 | 현재 확인 커밋 | 이번 검증 범위 |
|---|---|---|
| oneload-qa / qa | 이 문서 포함 커밋 | QA17건·검색 평가·실행기·문서 |
| oneload-app | b111af6 | 소스·커밋 관찰, 표준 감사. HTTP 채팅/POI칩·언어 변경 연결. 사진 위치·경로 화면 로컬 흐름 잔존. 이번 UI/빌드/실서버 E2E 미실행 |
| oneload-backend | 493884f | 기존44건·R2 주입 API20건·RAG 주입 API21건 |
| oneload_agent | 250271e | 기존43건·컴포넌트20시나리오/21턴·API 주입 |
| oneload-data | 606f648 | 모델·참조·스키마·사진 해시3건, 실제 지도 입력 |
| oneload-infra | 8587d3b | 커밋 관찰만. Compose·Portainer 구조, 배포 미검증 |
| oneload-rag | 4a967b3 | 공식 문서 MemorySearch 검색76질문(새32+기존44)·API21건. MCP·pgvector·실제 임베딩 이번 미검증 |

Frontend·Infra 커밋을 표준 기준선에 기록했다고 화면·배포를 검증한 것은 아니다. `reports/app-review.json`은 이전 App8c88f89의 CI282건·mock 시작 화면1건을 담은 역사적 기록이다. 최신 b111af6에 그 결과를 재사용하지 않는다. App #11은 문서 수정으로 closed다.

## 이번 완료와 증거

2026-10-23 11:04 KST, 표준 전체 실행:

| 검사 | 결과 |
|---|---|
| QA 회귀 | 17/17, skip0 |
| 데이터 | 3/3 |
| Agent 기존 시험 | 43/43 |
| Backend 기존 시험 | 44/44 |
| 컴포넌트 v2 | 20/20 시나리오·21/21 턴 |
| 모의 검색 R2↔Backend API | 20/20 |
| 별도 실제 메모리 RAG 주입 API | 21/21 |

표준 증거는 [baseline](../reports/baseline.json), 별도 RAG는 [API 보고서](../reports/rag-integration-probe.json)다. FakeLLM·합성 JPEG·일회용 DB이며 실제 모델/임베딩 호출0회다. 현장 사진 정답0건, 컴포넌트21턴 사람 검토 대기·최종 품질 점수null이다.
전체 종료 코드는 INT-06/07 때문에1이다. TC-03/04/11의 PARTIAL은 API 통과와 실제 화면 미검증을 구분한다.

QA #3 반영:

- service v2: Q10 답가능·조건별 요금/출처/확인일. 20문항 근거 매핑, 이전 CSV 보존, 전부 mapped_pending_human_review. 실제 서비스 실행은 NOT_RUN이다.
- component v2는 기존 SHA·질문·기대값을 유지한다. 모의 검색의 요금 근거 부재 기대도 유지한다.
- retrieval v1: 개발16/holdout16, 질문군 분리·평가 전 고정. 개발 목적식으로 후보0.35 선정. 개발 top3 9/10·범위밖 차단5/6, holdout10/10·4/6. 출고 조건 미달로 운영 확정 보류다.
- 기존 R3 진단44: 기본0.25 top1 32/40·top3 38/40·차단3/4 재현. 후보0.35 top1 30/40·top3 35/40·차단4/4. RAG 기본값은 변경하지 않았다.
- [RAG #3](https://github.com/team-onetruck/oneload-rag/issues/3)에 호텔 가격·실시간 잔여석 검색 오탐을 등록했다. [전체 결과](../reports/retrieval-evaluation.json)와 [판정 설명](issue3-resolution.md)을 함께 읽는다.

## 이슈와 남은 위험

| 항목 | 현재 상태·다음 행동 |
|---|---|
| QA #3 | Q10·근거 열 완료. 검색 출고 조건/INT-07 이후 검사가 남아 open 유지 |
| RAG #3 | 범위밖 검색 오탐. 개선 후 새로운 holdout과 기존 회귀셋으로 확인 |
| INT-06 | App 사진 위치·서버 경로·이벤트 화면 연결 및 실제 서버 전체 흐름 검증 필요 |
| INT-07 | Backend 기본 RuleAgent/NoVision. R4 운영 조립 후 기본 경로에서 재검증 필요. 주입21/21로 완료 처리하지 않음 |
| DATA-01 | 실제 통로·방향·예시 파노라마 및 정답 현장 확인 필요 |
| 서비스·사진 품질 | 서비스20건 사람 검토·실제 모델 비교·현장 사진·휴대폰 권한/네트워크/복구 미검증 |
| Infra #1 | 공개 범위/private 표기 이슈 별도 추적 |

과거 QA #1/#2·Agent #1/#2/#3·RAG #1/#2는 완료된 이력이다. 새 작업에서 현재 이슈 상태를 다시 읽는다. RAG #1/#2의 과거 f1ec584 재검증은82 passed/0 skipped와 HTTP6/6이며 당시 Backend a82b7be였다. [#1 근거](https://github.com/team-onetruck/oneload-rag/issues/1#issuecomment-6354507578), [#2 근거](https://github.com/team-onetruck/oneload-rag/issues/2#issuecomment-6354508557). 최신 전체 RAG/MCP 시험 결과로 바꾸어 소개하지 않는다.

R3의 Backend 연결 패치는 과거 launchd 전제를 포함한 제안이다. 현재 Infra Compose 구성에 맞는지 검토해야 하며 QA 작업에서 적용·배포하지 않았다.

## 다음 작업

1. RAG #3 범위 판정·관련도 보완을 확인한다. 이미 공개한 holdout으로 튜닝한 뒤 독립 성능으로 보고하지 않는다. 새 holdout·기존 회귀·문서 해시를 기록한다.
2. INT-07 운영 조립 및 INT-06 화면 연결이 반영되면 기본 entrypoint·실제 서버 대표 흐름을 확인한다. 현재 주입 명령은 계약 회귀용이며 기본 설정 검사가 아니다.
3. R3와 서비스 정답·확인일·미확인 부분을 사람 검토한다. 실제 모델 사용 요청이 있으면 모델·프롬프트·자료·평가셋을 고정해 baseline→한 요소 개선→같은 셋 재측정한다.
4. 현장 사진 정답·개인정보·실기기 복구·거리뷰 방향을 검증하고 최종 결과서·발표 숫자를 맞춘다.

## 다른 컴퓨터 준비와 재현

Git, Python3.12, Docker(pgvector/pgvector:pg17)가 필요하다. 기존 검증은 macOS/Python3.12.14이며 다른 OS 설치는 미검증이다. 같은 부모에 아래 저장소를 clone한다. 가상환경 링크·.env·DB URL은 복사하지 않는다.

```sh
git clone https://github.com/team-onetruck/oneload-qa.git qa
git clone https://github.com/team-onetruck/oneload-app.git
git clone https://github.com/team-onetruck/oneload-backend.git
git clone https://github.com/team-onetruck/oneload_agent.git
git clone https://github.com/team-onetruck/oneload-data.git
git clone https://github.com/team-onetruck/oneload-infra.git
git clone https://github.com/team-onetruck/oneload-rag.git
cd qa
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-runtime.lock.txt
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_checks.py --project-root .. --with-backend --output results/handoff-full-001
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_retrieval.py --project-root .. --output results/handoff-retrieval-001.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_backend_tests.py --project-root .. --with-rag --rag-min-score 0.35 --output results/handoff-rag-api-001
```

clone은 실행 시점 main이다. manifest의 검증 커밋과 비교하고 재현하려는 버전을 새 checkout에 선택해 기록한다. 기존 사용자 checkout을 reset하지 않는다. 매 실행 새 출력 경로를 사용한다.
표준 검사는 INT-06/07로 exit1, 검색 평가는 출고 조건 미달로 exit1, RAG API는21/21이면 exit0이 이번 기대다. 다른 오류를 이 실패와 혼동하지 않는다. 표준 공개 증거 갱신은 전체 명령에 `--reports reports`를 추가한다. 별도 RAG JSON은 입력 버전·실패·민감 내용을 검토한 뒤 reports에 반영한다.

Backend 기존 테스트는 public schema를 삭제한다. 반드시 `run_backend_tests.py`가 생성·삭제하는 일회용 DB만 사용하며 배포 설정을 환경 준비로 실행하지 않는다. RAG profile은 공식 문서를 명시적으로 읽어 환경의 pgvector·커뮤니티 설정을 사용하지 않는다. 실제 모델·임베딩 호출은 요청 범위·비용이 정해졌을 때만 실행한다.

## 저장소 밖 자료

교재·원본 PPTX/PDF 제출 양식은 별도 공유 폴더로 전달한다([참고 안내](reference/README.md)). 실제 사진·개인정보는 동의·검토·접근 범위를 확인한 별도 저장소로 관리한다. 키·토큰·.env·실제 사진·원시 HTTP 로그는 공개하지 않는다. GitHub의 재현 절차·해시·검토된 증거가 필수 인수인계이며 이전 AI 대화 전체는 필수 의존성이 아니다.
