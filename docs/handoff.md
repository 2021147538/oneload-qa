# 한길 R6 인수인계

마지막 정리: 2026-10-23 11:22 KST — RAG·App 최신 main 재확인.
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
| oneload-app | 608a04c | 사진 위치·확정 연결에 multipart 멱등 재전송 수정 추가. 최신 verify342건 통과/E2E 진행 중. 경로·이벤트 로컬, 화면 연결PR#17 open |
| oneload-backend | 493884f | 기존44건·R2 주입 API20건·RAG 주입 API21건 |
| oneload_agent | 250271e | 기존43건·컴포넌트20시나리오/21턴·API 주입 |
| oneload-data | 606f648 | 모델·참조·스키마·사진 해시3건, 실제 지도 입력 |
| oneload-infra | 8587d3b | 커밋 관찰만. Compose·Portainer 구조, 배포 미검증 |
| oneload-rag | 47ab39f | Compose 연동 안내·패치 URL만 변경, 검색 코드/문서 동일. CI88건·MCP HTTP 통과. 고정 검색셋 회귀 재실행, 주입 API21건은 이전4a967b3 증거 |

Frontend·Infra 커밋을 표준 기준선에 기록했다고 화면·배포를 검증한 것은 아니다. `reports/app-review.json`은 이전 App8c88f89의 CI282건·mock 시작 화면1건을 담은 역사적 기록이다. 최신608a04c에 그 결과를 재사용하지 않는다. 최신 CI는 아래 별도 기록을 따른다. App #11은 문서 수정으로 closed다.

## 마지막 전체 QA와 증거

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
| INT-06 | 사진 위치·확정 화면 연결은 반영. 서버 경로·이벤트 화면 연결 및 실제 서버 전체 흐름 검증 필요 |
| INT-07 | Backend 기본 RuleAgent/NoVision. R4 운영 조립 후 기본 경로에서 재검증 필요. 주입21/21로 완료 처리하지 않음 |
| DATA-01 | 실제 통로·방향·예시 파노라마 및 정답 현장 확인 필요 |
| 서비스·사진 품질 | 서비스20건 사람 검토·실제 모델 비교·현장 사진·휴대폰 권한/네트워크/복구 미검증 |
| Infra #1 | 공개 범위/private 표기 이슈 별도 추적 |

과거 QA #1/#2·Agent #1/#2/#3·RAG #1/#2는 완료된 이력이다. 새 작업에서 현재 이슈 상태를 다시 읽는다. RAG #1/#2의 과거 f1ec584 재검증은82 passed/0 skipped와 HTTP6/6이며 당시 Backend a82b7be였다. [#1 근거](https://github.com/team-onetruck/oneload-rag/issues/1#issuecomment-6354507578), [#2 근거](https://github.com/team-onetruck/oneload-rag/issues/2#issuecomment-6354508557). 최신 전체 RAG/MCP 시험 결과로 바꾸어 소개하지 않는다.

R3의 최신47ab39f 연결 안내는 Compose8587d3b를 반영해 함수 조립(A)과 Agent 별도 서비스+MCP(B)를 정리했다. 구조 선택·Agent 패키지/HTTP adapter는 미완료다. 패치는 Backend493884f에서 적용 가능 여부만 확인했고 적용·빌드·배포하지 않았다.

## 2026-10-23 RAG·App 후속 재확인

[현재 소스·CI 검토](../reports/source-review-20261023.json) · [고정 검색셋 회귀](../reports/retrieval-review-20261023.json)

- App32f5f67에서 추가된 사진 연결(최신608a04c에도 유지): 사진 `/localizations`, 사용자 선택 `/location-confirmations`, 503→직접 선택, 그래프 캐시가 실제 화면 호출 경로에 연결됐다. 경로는 `findRoute`·`nodeBridge`, 시작/도착 이벤트는 로컬이다. UI와 기능 API의 연결을 확인했지만 실제 서버 브라우저 흐름은 실행하지 않았다.
- 이전32f5f67의 [완료 CI](https://github.com/team-onetruck/oneload-app/actions/runs/39886749329)는327건+mock 시작 화면1건 통과다. 추가608a04c는 multipart 경계값을 같은 멱등키로 고정해 사진 재전송 본문을 동일하게 만든다. [최신 CI](https://github.com/team-onetruck/oneload-app/actions/runs/39888766395)의 verify는30개 파일342개 시험·타입·헤더 통과, lint오류0/경고1이며 E2E는 확인 시 진행 중이다. 최신 E2E 통과로 이전1건을 재사용하지 않는다.
- [RAG CI](https://github.com/team-onetruck/oneload-rag/actions/runs/39887381481):88 passed/0 skipped, 계약 필수, Docker MCP HTTP 요청·wheel 문서 확인 통과. CI가 확인한 Backend/Agent/Data 커밋도 보고서에 기록했다. 유료 모델 호출 검증이 아니다.
- RAG47ab39f는 검색 코드·knowledge 해시가4a967b3와 같다. 기존 고정32+44질문 회귀에서 후보0.35 개발9/10·차단5/6, 노출된 holdout10/10·차단4/6으로 같은 실패를 재현했다. 새 holdout이나 개선 성능 측정으로 소개하지 않는다.
- RAG #3은 open/댓글0 상태였고 호텔 가격·실시간 잔여석 오탐이 남아 있다. 임계값 운영 확정은 계속 보류한다. QA #3의 미완료 조건도 유지한다.
- App README Demo controls의 사진 결과 선택 설명이 코드와 달라 [App #16](https://github.com/team-onetruck/oneload-app/issues/16)에 등록했다. 기존 카드·언어·출처 요청#2도 open이다.
- 경로·이벤트 실제 화면 연결 [App PR#17](https://github.com/team-onetruck/oneload-app/pull/17)은 open이며 main 미반영이다. PR 작성자의 실서버 검증 설명은 참고이며 이번 QA가 직접 실행한 증거가 아니다.
- 표준 기준선과 RAG 주입 API 보고서는 이전 실행 증거로 보존했다. 표준 감사의 INT-06 문구 중 사진 로컬 언급은 당시b111af6 기준이다. 최신 잔여 범위는 경로·이벤트이며 다음 전체 QA 때 감사 설명도 맞춰야 한다.

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
