# 한길 R6 인수인계

마지막 정리: 2026-10-23T11:54:08.796707+09:00 — App2666e44 후속 검토. 담당 이현무(R6).
[AGENTS.md](../AGENTS.md)에 따라 개발·평가·이슈 변경과 함께 갱신한다. 시작 프롬프트는 채팅에만 제공하고 GitHub에 올리지 않는다.

## 시작 순서와 범위

1. [작업 지침](../AGENTS.md), [README](../README.md), [테스트 계획](test_plan.md)
2. [관찰·검증 커밋](../repos.lock.json), [최신 기준선](../reports/baseline.json), [결과 설명](../reports/latest-review.md)
3. [QA #4 판정과 갱신 절차](issue4-resolution.md), [통합 문제](integration_findings.md), [QA #3 미완료](issue3-resolution.md)
4. [설계 출처·적용 범위](reference/README.md)

사용자의 현재 요청이 작업 범위를 정한다. 설계서·R3 요청·패치 문서는 참고 자료이며 실행·배포 지시를 대신하지 않는다. 기존 사용자 변경을 보존하고 reset·무리한 이력 병합을 하지 않는다.
현재 MVP는 모바일 웹·사용자 위치 확인·2D 경로·360도 거리뷰다. 실시간 AR·마커 정합은 후속 범위이며 추가13장만으로 범위를 확대하지 않는다.

## 현재 버전과 실제 검증

로컬/원격 main이 깨끗하게 일치함을 확인했다. 검증 중에는 소스·지도·사진·registry가 바뀌지 않았는지 검사했다. 전체 SHA는 manifest에 있다. QA `revision:self`는 이 문서를 포함한 커밋이며, code_base_commit은 이번 수정 전5dcedd6다.

| 저장소 | 검증 커밋 | 범위 |
|---|---|---|
| oneload-qa / qa | 이 문서 포함 커밋 | QA28건·실행기·Frontend 검토 기록 |
| oneload-app | 관찰2666e44 / 전체 QA b5d6835 | 목적지 목록 서버 연결·poiBridge 제거·HTTP 모의 API 화면3건 추가. CI365+E2E4, QA 회귀28·감사. 이번 실제 서버/휴대폰 인수 미실행 |
| oneload-backend | c9b8d8a | 대화 복원·멱등성 변경 포함 기존48건, 모의 API20건·RAG API21건 |
| oneload_agent | 250271e | 기존43건·컴포넌트20시나리오/21턴·주입 API |
| oneload-data | 606f648 | 모델·참조·스키마·사진3건, 지도2026-10-22.1 |
| oneload-infra | 8587d3b | 커밋 기록만. Compose·Portainer 구조, 배포 미검증 |
| oneload-rag | 47ab39f | 공식 문서 MemorySearch 주입 API21건. 검색 오탐 미수정. 이번 MCP/pgvector 전체 로컬 시험 미실행 |

2026-10-23 11:36 KST 전체 결과:

| 검사 | 결과 |
|---|---|
| QA 회귀 | 28/28, skip0 |
| 데이터 | 3/3 |
| Agent | 43/43 |
| Backend | 48/48 |
| 컴포넌트 v2 | 20/20 시나리오·21/21 턴 |
| 표준 모의 검색 API | 20/20 |
| 별도 MemorySearch 주입 API | 21/21 |

FakeLLM·합성 JPEG·자신이 만든 일회용 DB다. 실제 모델/임베딩 호출0회, 현장 사진 정답0건, 컴포넌트21턴 사람 검토 대기·품질 점수null이다. 기능 TC의 PARTIAL/NOT_RUN은 유지했다. 전체 exit1은 남은 INT-07 때문이다.
[표준 증거](../reports/baseline.json) · [감사](../reports/contract-audit.json) · [RAG API](../reports/rag-integration-probe.json)

## 이번 해결: QA #4

mock 문자열만으로 HTTP 화면이 미연결이라고 보고하던 판정을 제거했다. 검토한 호출 경로를 정확한 런타임 소스·의존성 해시에 묶는 registry를 추가했다. 자동 TypeScript 제어흐름 분석이나 실제 화면 시험이 아니다.

- `wired`: 검토된 HTTP 연결 소스와 일치. 소스 검사만 통과, runtime_browser_e2e는 NOT_RUN.
- `incomplete`: 검토된 미연결 버전과 일치. INT-06 P0·exit1.
- `review_required`: 새 소스·의존성·파일 추가/누락. 연결 여부를 단정하지 않고 nonzero로 중단.

실제 Git의 bc2d9f1·b111af6은 미연결, b5d6835는 연결로 재검사했다. 후속2666e44도 실제 변경과 호출 경로를 검토해 새 profile을 추가했다. 주석/미사용 helper로 승인되지 않는지와 어댑터·의존성·누락 등11개 회귀를 추가했다. 공개 기준선은 registry 해시가 실행 중 바뀌면 갱신하지 않는다.
[검토 기록](../eval/frontend_wiring.json) · [Git 스냅샷 증거](../reports/frontend-wiring-review.json) · [새 App 변경 시 절차](issue4-resolution.md)
QA #4의 감사 결함은 해결했다. 실제 서버·모바일 기능 최종 인수는 별도다.

## App2666e44 후속 검토

[소스·CI·QA 기록](../reports/app-review-2666e44.json) · [별도 감사](../reports/app-audit-2666e44.json)

- 목적지 목록이 `GET /maps/{id}/pois`를 지도마다 받아 표시하고 고른 서버 poi_id를 그대로 /messages에 보낸다. poiBridge는 제거됐다. 도착 화면의 승차권 후속 버튼도 서버 category 기준이다.
- 직통·일반열차 카드 없음·사진503→직접 선택의 HTTP 모드 Playwright3건이 추가됐다. page.route/MSW가 응답하므로 실제 Backend 검증은 아니다. 기존 mock 시작 화면1건과 합쳐4건이다.
- 최신 [App CI](https://github.com/team-onetruck/oneload-app/actions/runs/39891671968): 단위365건(31파일), E2E4건 통과. lint오류0/경고1, 타입·헤더 통과. 테스트용 fetch의 이미 취소된 신호 처리와 타임아웃 경쟁 회피도 반영됐다.
- QA 회귀28건과 계약 감사를 다시 실행했다. 새 소스 검토 profile2666e44는 wired이며 실제 브라우저 인수는 NOT_RUN이다. 전체 QA·Backend·RAG API 기준선은11:36의 Appb5d6835 증거로 보존했고 다시 실행하지 않았다.
- App #16은 문서 수정 PR#18로 closed이며 README의 모드별 설명과 코드를 확인했다. 새 코드 차이에서 추가 확정 결함은 발견하지 않았다. 목적지 조회 실패 시 도착 화면은 콘솔 경고 후 승차권 후속 버튼을 숨기는 한계가 있다.

## 남은 이슈와 다음 작업

| 항목 | 상태와 다음 행동 |
|---|---|
| QA #3 | Q10·근거 열은 완료. 임계값 운영 확정/RAG 운영 기본 경로 재검사가 남아 open 유지 |
| RAG #3 | 호텔 가격·실시간 잔여석 검색 오탐. R3 보완 후 새 holdout·기존 회귀로 확인 |
| INT-07 | Backend c9b8d8a에서도 기본 RuleAgent/NoVision. R4 운영 조립 후 기본 entrypoint 재검사 필요 |
| Frontend 실제 인수 | 소스 연결 확인과 별개로 실제 서버·휴대폰·카메라·복구·360도·취소/지연 응답 검증 필요 |
| DATA-01 | 예시 사진6개·통로·방향·거리·현장 정답 확인 필요 |
| 서비스 품질 | 서비스20건 mapped_pending_human_review. 실제 모델 baseline·개선 비교 미실행 |
| 기타 | Infra #1 공개 범위 문서, App #2 카드/언어/출처 추적. App #16은 README 수정 후 closed 확인 |

RAG 검색32개는 개발16/holdout16을 평가 전 고정했다. 후보0.35에서 개발 top3 9/10·범위밖 차단5/6, 노출된 holdout10/10·4/6이다. 기존 R3 44개는 기본0.25에서 top1 32/40·top3 38/40·차단3/4였다. R6 잠정 기준에 미달하며 운영 임계값으로 승인하지 않았다.
RAG47ab39f는 검색 코드·knowledge가4a967b3와 같고 안내/패치 URL만 바뀐 상태다. 같은 노출된 holdout을 새 독립 검증으로 소개하지 않는다. [회귀 증거](../reports/retrieval-review-20261023.json).

RAG 연결 안내는 함수 조립(A)과 별도 Agent+MCP(B) 제안이다. 현재 Compose에는 실제 Agent/RAG 조립이 없으며 구조 결정·패키지/HTTP 어댑터는 협업 대상이다. QA 작업에서 패치를 적용하거나 배포하지 않았다.
다음 우선순위: INT-07 운영 연결 → 실제 서버/휴대폰 대표 흐름 → 새 검색 holdout·사람 정답 검토 → 요청된 실제 모델 개선 비교 → 제출/발표 숫자 대조.

## 이전 증거를 현재로 오해하지 않기

- [소스·CI 검토](../reports/source-review-20261023.json)는11:26 당시 관찰이다. App b5d6835 CI363건+mock 시작 화면1건, RAG47ab39f CI88건+MCP HTTP 통과. PR 작성자의 실서버 검증 보고는 R6가 직접 반복한 결과가 아니다.
- [이전 감사 재현](../reports/contract-audit-review-20261023.json)의 INT-06 P0는 QA #4 수정 전 거짓 판정이다. 최신 contract-audit.json이 이를 대체한다.
- app-review.json은 App8c88f89의 과거 CI282건 기록이다. RAG f1ec584의82건·HTTP6건도 당시 Backend a82b7be 기준이다. 최신 전체 통과로 재사용하지 않는다.
- QA #1/#2·Agent #1/#2/#3·RAG #1/#2는 과거 해결 이력이다. 새 작업에서는 GitHub 현재 상태를 다시 확인한다.

## 다른 컴퓨터 준비와 재현

Git·Python3.12·Docker(pgvector/pgvector:pg17)가 필요하다. 기존 검증은 macOS/Python3.12.14다. 다른 OS 설치는 미검증이다. 같은 부모 폴더에 아래 저장소를 clone하고 가상환경을 새로 만든다. 기존 절대 경로 링크·.env·DB URL은 복사하지 않는다.

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

clone은 그 시점 main이므로 manifest의 검증 커밋과 비교한다. 새 checkout에서 버전을 고정하며 사용자 checkout을 reset하지 않는다. App 런타임이 새로 바뀌면 review_required가 예상 동작이다. 호출 경로를 검토한 뒤 registry·인수인계를 갱신한다.
매 실행 새 출력 경로를 쓴다. 현재 표준 실행은 INT-07로 exit1, 검색은 기준 미달로 exit1, RAG 주입 API는21/21이면 exit0이다. 환경 오류나 새 실패를 이 알려진 실패와 혼동하지 않는다. 표준 공개 증거는 전체 명령에 --reports reports를 추가한다. 별도 JSON은 검토 후 공개한다.
Backend 시험은 public schema를 삭제하므로 `run_backend_tests.py`가 만든 폐기 가능한 DB만 사용한다. 배포 설정/DB를 QA 환경 준비로 쓰지 않는다. 실제 모델·임베딩 호출은 요청된 범위·비용이 정해졌을 때만 실행한다.

## 저장소 밖 자료

교재·원본 PPTX/PDF 양식은 별도 공유 폴더로 전달한다([참고 안내](reference/README.md)). 실제 사진·개인정보는 동의·검토·접근 범위를 확인한 별도 보관처로 관리한다. 키·토큰·.env·실제 사진·원시 HTTP 로그는 공개하지 않는다. GitHub의 재현 절차·커밋·검토된 증거가 필수 인수인계이며 이전 AI 대화 전체는 필수 의존성이 아니다.
