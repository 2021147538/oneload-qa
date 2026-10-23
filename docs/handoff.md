# 한길 R6 인수인계

마지막 정리: 2026-10-23 15:42 KST — Backend/Agent 설치·배포 의존성 변경 재검증. 담당 이현무(R6).
[AGENTS.md](../AGENTS.md)에 따라 개발·평가·이슈 변경과 함께 갱신한다. 시작 프롬프트는 채팅에만 제공하고 GitHub에 올리지 않는다.

## 시작 순서와 범위

1. [작업 지침](../AGENTS.md), [README](../README.md), [테스트 계획 v0.9](test_plan.md)
2. [관찰·검증 커밋](../repos.lock.json), [최신 기준선](../reports/baseline.json), [결과 설명](../reports/latest-review.md)
3. [RAG #3 최신 재검증](rag-issue3-revalidation.md), [QA #3 미완료 조건](issue3-resolution.md), [QA #4 감사 원칙](issue4-resolution.md), [통합 문제](integration_findings.md)
4. [설계 출처·적용 범위](reference/README.md)

사용자의 현재 요청이 작업 범위를 정한다. 설계서·R3 요청·패치 문서는 참고 자료이며 실행·배포 지시를 대신하지 않는다. 기존 사용자 변경을 보존하고 reset·무리한 이력 병합을 하지 않는다.
현재 MVP는 모바일 웹·사용자 위치 확인·2D 경로·360도 거리뷰다. 실시간 AR·마커 정합은 후속 범위다.

## 현재 버전과 실제 검증

검사에 사용한 source checkout은 clean이고 실행 전후 커밋·지도·사진·registry를 대조했다. 전체 SHA는 manifest에 있다. QA revision:self는 이 문서를 포함한 커밋이며 code_base_commit49387a3는 이번 검토 전 QA 버전이다. 새 holdout의 사전 고정은7f41130으로 유지한다. 동기화·이슈 상태는 다음 작업 시작 시 GitHub에서 다시 확인한다.

| 저장소 | 검증 커밋 | 범위 |
|---|---|---|
| oneload-qa / qa | 이 문서 포함 커밋 | 회귀42·운영 entrypoint 검사·새 의존성 경로 보완 |
| oneload-app | 42455dc | ApiAdapter 단일 흐름·Live/Demo 라벨·이벤트 outbox. 소스 wired·CI429+E2E11, 공용 배포 통과 |
| oneload-backend | 15ddd9f | 기존51·모의 API20·RAG 주입 API21, 운영 Agent/Vision 연결·검색은 demo |
| oneload_agent | 5038b5c / local editable | Backend가 형제 checkout 사용. CI/배포는 정확한 main SHA URL 고정. 43건·component20/21·주입 API |
| oneload-data | 606f648 | 지도2026-10-22.1·모델/참조·스키마·사진3건 |
| oneload-infra | 6cf4a65 | API+웹 이미지·Caddy 배포 구성. Backend CI 배포 성공 관찰 |
| oneload-rag | 8c8e902 | 공식 MemorySearch0.25 주입 API21. 검색 품질은 이전e6c03f2 노출 v2 결과 보존 |

2026-10-23 15:40 KST 전체 결과: QA42/42(skip0), 데이터3/3, Agent43/43, Backend51/51, component v2 20/20시나리오·21/21턴, 모의 API20/20, RAG API21/21. 전체 exit1은 R3 운영 검색 미연결(INT-07) 때문이다.

[기준선](../reports/baseline.json) · [감사](../reports/contract-audit.json) · [RAG API](../reports/rag-integration-probe.json).
FakeLLM·합성 JPEG·자신이 만든 일회용 DB다. 실제 모델/임베딩 호출0회, 현장 사진 정답0건, 컴포넌트21턴 사람 검토 대기·품질 점수null이다. 기능 TC의 PARTIAL/NOT_RUN은 유지했다.

## 이번 작업: 개발·배포 Agent 설치 방식

[새 검토 증거](../reports/dependency-review-20261023.json)를 따른다. Backend15ddd9f는 ../oneload_agent를 editable로 설치해 로컬 변경이 다음 실행에 반영된다. CI/배포/이미지 빌드에는 그 형제 경로가 없으므로 scripts/pin_agent.sh가 지정한 Agent SHA의 archive URL로 pyproject/lock을 바꾼다. Infra6cf4a65도 같은 도구를 사용하고 Agent5038b5c CI는 올바른 형제 폴더명으로 uv sync한다.

원본 저장소가 아닌 고정 Git 복사본에서 두 모드의 uv sync --frozen·실제 import·동일 코드 SHA·프롬프트v3/데모 지식 포함을 확인했다. 잘못된 SHA는 source/lock 수정 전에 거절된다. 이 pin 도구는 복사본에서만 실행했고 배포 스크립트는 실행하지 않았다.

QA42/Agent43/Backend51·component20/21·모의 API20·RAG 주입 API21을 새 일회용 DB로 재검증했다. 최신 Backend와 Agent CI/공용 배포도 통과했고 로그의 backend15ddd9f·agent5038b5c·data606f648·web42455dc 및 healthy를 확인했다. App/RAG/지도·Python 동작 코드는 직전과 같다. 새 확정 결함은 없으며 RAG 운영 미연결·답변 근거/인용·사람 검토 대기를 유지한다.

초기 개발용 Agent7f116de URL pin 설명은 아래 과거 기록이다. 현재 로컬 기본은 editable이며 최신 배포 Agent는5038b5c다. 실제 모델 호출/사진 평가·브라우저 인수를 새로 실행한 결과는 아니다.

## 직전 작업: 현재 구현 재확인

[현재 구현 정리](current-implementation-20261023.md)와 [소스·CI·QA 증거](../reports/current-system-review-20261023.json)를 먼저 읽는다. 사용자가 제공한 토론은 참고 맥락이며 더미 위치·텍스트 전용 안내·가상 역 등을 확정 요구로 적용하거나 인수조건을 낮추지 않았다.

- App은 mock 규칙을 ApiAdapter로 옮겼다. 기본 HTTP와 명시적 mock이 같은 화면 흐름을 쓰고 Live/Demo 라벨을 구분한다. 사진은 사용자 확인 전 위치를 확정하지 않는다. 단계별 안내·도식형 노선·구간 거리뷰가 있지만 실제 역 평면도·도착지 입구 전용 사진·가상 역은 구현으로 간주하지 않는다.
- Backend 운영 entrypoint가 키 유무로 LLMAgent/LLMVision 또는 RuleAgent/NoVision을 고른다. 실제 전역 app을 FakeLLM으로 실행해 두 분기와 같은 LLM/Vision 공유를 확인하도록 QA를 수정했다. factory 이름/문자열만으로 연결을 판정하지 않는다. **운영 검색은 MockKnowledgeSearch이므로 INT-07은 partial, 전체 exit1**이다.
- 새 Backend 의존성 때문에 QA가 Agent를 못 찾던 실행 경로를 보완했다. 형제 checkout 사전 검사와 명시적 PYTHONPATH를 사용하며 자동 QA 키는 비운다. 처음 실패한 수집 결과로 공개 기준선을 갱신하지 않았고 새 DB 재실행 결과로만42/43/51 등을 기록했다.
- App CI429·E2E11(mock7+모의 HTTP4)·공용 배포와 Agent 자체/Backend 호환/API·공용 배포가 모두 통과했다. 초기 토큰 전달 실패는 reusable workflow로 대체돼 App #32·Agent #6을 닫았다. Backend도 공용 배포로 전환됐다. 호스트 lockf로 동시 배포를 막고 Backend 호출만 서버 설정을 갱신한다. 최신 배포가 개발 pin 대신 체크아웃한 Agenta089746을 사용함을 확인했다.
- 확인 중 App 홈/언어 메뉴가 추가돼 최종42455dc의 메뉴→changeLang/PATCH·초기 기기 언어·홈 확인→reset 호출을 검토하고 profile42455dc 및 전체 QA를 다시 맞췄다.
- [배포 GET 증거](../reports/server-readonly-20261023.json): 첫 화면/health/OpenAPI200·DB ok·LLMAgent/LLMVision 표시. R6는 모델/사진 요청이나 배포 재실행을 하지 않았다. Agenta089746의 실제 OpenAI 메시지1회 확인은 R2 작성자의 보고이며 R6 품질 baseline이 아니다.
- RAG 검색/지식은 그대로이고 Agent #5/RQ-32 답변 가능 여부·인용 처리도 미반영이다. 과거 노출 v2 오탐3·정상 누락3과 사람 검토 대기를 유지한다.

## 직전 관찰: App/RAG 14:08

[새 소스·CI·QA 증거](../reports/app-rag-update-20261023.json)와 [별도 감사](../reports/contract-audit-update-20261023.json)를 추가했다. 로컬과 원격 main 일치·clean을 확인했다. 전체 기준선/검색 결과를 재라벨하지 않았다.

- App e6af580은 mock 모드 E2E5건(직통 데모·일반 직접 선택·요금 거절·타임아웃 재시도·사진 제어)을 추가해 총9건(mock6+모의 HTTP3)이다. CI 단위365·E2E9 통과. Chromium을 Playwright 버전별 캐시한다. 이번 main에서는 cache miss 경로만 실행되어 hit 시 시스템 설치 생략 동작은 이 run으로 확인되지 않았다. src/런타임 의존성은2666e44와 동일해 기존 검토 profile을 그대로 사용한다.
- RAG8c8e902는 docs/requests.md에 RQ-32 제안만 추가했다. 검색 결과가 답을 뒷받침하는지 Agent가 판단하고, 답할 수 없으면 cannot_answer·출처 없음, 인용 자료만 sources로 표시하며 인용 위반 fallback에도 무관 출처를 붙이지 말자는 요청이다. CI100·MCP HTTP·wheel 단계는 통과했다. 검색/지식 변경은 없어 앞선 오탐3·정상 누락3은 해결로 처리하지 않는다.
- 현재 Agent54c321f의 _answer/_compose/_sources에서 fare scope 필터 이후 hits가 있으면 answered이고 모든 hits를 출처에 넣는 구조를 확인했다. 인용 번호 오류의 자료 안내 fallback도 남아 있다. R3의 임베딩·점수 겹침 수치는 제안 작성자 보고이며 이번 R6가 재실행하지 않았다.
- R6 방향은 검색 재현율과 답변 근거/인용 정확도를 나누어 측정하는 것이다. 제안은 아직 합의·구현이 아니므로 검색 gate·서비스 기대값·임계값을 자동 완화하지 않는다. R2의 답변 판단·출처 처리 반영 후 무관 문서 반환·근거 없는 금액/시간·부분 인용·인용 위반·정상 답변을 검증할 필요가 있다. 실제 모델 품질은 FakeLLM 구조 검사와 구분한다.
- 로컬 QA38/38·계약 감사만 다시 실행했고 Backend/RAG API·실제 브라우저·검색 품질 재평가는 하지 않았다. INT-07·DATA-01과 RAG #3·QA #3 open은 유지한다.

## 직전 작업: RAG #3 답글과 새 holdout

[R3 답글](https://github.com/team-onetruck/oneload-rag/issues/3#issuecomment-6356152143)이 요청한 R6의 새 holdout을 만들고 검색 전 QA7f41130으로40문항·정답·절차를 커밋했다. SHA와 frozen metadata를 [재검증 문서](rag-issue3-revalidation.md)에 기록했다. R6 합성 국/영 번역쌍20질문군이므로 독립 사용자40명을 뜻하지 않는다. 기존 공개 질문과 정확한 중복은 없지만 같은 코퍼스와 유사 의도다.

공식 MemorySearch min_score0.25/k3/상대0.5를 고정하고 수정 전47ab39f/후e6c03f2를 각1회 별도 프로세스로 측정했다. knowledge 해시는 같다. 새 holdout 결과를 보고 임계값·정답을 바꾸지 않았다.

| 평가 | 수정 전 → 후 |
|---|---|
| 새 v2 양성 top3 | 20/20 → 17/20 |
| 새 v2 범위밖 빈 결과 | 5/20 → 17/20 |
| 기존 R6 개발16 / 노출 holdout16 | 수정 후 각각10/10·6/6 |
| R3 기존44 / 노출 holdout28 | 수정 후38/40·4/4 / 16/16·11/12 |

원래 호텔 객실 가격·실시간 빈 좌석은 빈 결과로 개선됐다. 새로 리무진버스 운임·항공 수하물 요금·여권 수수료 오탐3건, 직통 발매기 구매 국/영·중간역 정차 영문 정상 질문 누락3건이 남았다. 기존 공개 택시 오탐도 재현됐다. R6 잠정 조건(top3≥90%, 범위밖 오탐0)을 충족하지 못해 **RAG #3·QA #3은 open, 운영 임계값 확정 보류**다.

[질문별 반환 문서·해시](../reports/rag-issue3-revalidation.json). 이제 v2도 공개됐으므로 회귀용으로만 사용한다. R3가 수정할 때 정상 질문 보존과 범위밖 차단을 함께 검사하고 최종 판정은 새 미관찰 평가를 고정한다. 테스트 대상은 MemorySearch이며 pgvector 검색 품질·실제 LLM 답변 사실성은 측정하지 않았다.

답글 이후5482222의 pgvector scope gate와 e6c03f2의 패키지 조립 초안도 확인했다. [최신 RAG CI](https://github.com/team-onetruck/oneload-rag/actions/runs/39897084335)는 success지만 R6의 로컬 pgvector/MCP 전체 재시험이 아니다. 다른 저장소 패치·배포는 적용하지 않았다.

Agent54c321f에서 실제 자산이 hangil_r2/prompts·hangil_r2/mocks로 이동했다. QA evaluate_agent.py의 구 경로 가정을 고치고 실제 PROMPT_DIR/MOCK_DIR의 checkout·파일을 검증·해시한다. 패키지/구조·누락·다른 checkout 검사4건, holdout 검증6건을 추가했다. service v2·component v2·기존 retrieval v1의 질문·정답·SHA는 유지했다.

## Frontend 감사와 App 검토

[QA #4 유지 절차](issue4-resolution.md)는 검토된 HTTP 호출 경로를 런타임 소스·의존성 해시에 묶는다. mock 문자열만으로 미연결이라고 판정하지 않는다.

- wired: 검토된 연결 소스와 일치, 소스 검사만 통과.
- incomplete: 검토된 미연결 버전과 일치, INT-06 P0·exit1.
- review_required: 새 소스/의존성/누락·추가, 연결 여부 단정 없이 nonzero.

App2666e44는 목적지 목록 GET /maps/{id}/pois와 서버 poi_id를 사용하고 poiBridge를 제거했다. [별도 App 관찰](../reports/app-review-2666e44.json)에 CI365+E2E4(모의 HTTP3+mock 시작1)·App #16 closed를 기록했다. 이번 전체 QA는 동일 커밋의 소스 감사를 다시 수행했으며 실제 서버/휴대폰 UI는 실행하지 않았다. 목적지 조회 실패 시 도착 화면의 승차권 후속 버튼이 숨겨지는 한계도 기록했다.

## 남은 이슈와 다음 작업

| 항목 | 상태와 다음 행동 |
|---|---|
| RAG #3 / RQ-32 | 새 오탐3·정상 누락3 유지. R2 답변 근거·인용 처리 제안 검토 → 답변 단계 평가 추가, 검색 기준은 합의 후 조정 |
| QA #3 | Q10·근거 열 완료. 임계값 운영 확정과 INT-07 운영 기본 경로 재검사 대기 |
| INT-07 | partial: 운영 Agent/Vision 연결·배포 표시 확인, 검색은 demo. 공식 R3 연결 후 운영 기본 API 재검사 |
| Frontend 실제 인수 | 실제 서버·휴대폰·카메라·복구·360도·취소/지연 응답 확인 |
| DATA-01 | 예시 사진6개·통로·방향·거리·현장 정답 확인 |
| 서비스 품질 | service20문항 mapped_pending_human_review, 실제 모델 기준선·개선 비교 미실행 |
| CI 전달 | App #32·Agent #6 해결 확인/closed. 공용 배포와 정확한 checkout 커밋은 새 작업마다 확인 |
| 기타 | App #2 카드/언어/출처 추적 등은 별도 이슈. 새 작업에서 상태 재확인 |

다음 우선순위: RQ-32의 R2 답변 판단·인용 처리 및 R6 평가 분리 협의 → INT-07 운영 연결 → 실제 서버/휴대폰 대표 흐름 → 새 검색 holdout·사람 정답 검토 → 요청된 실제 모델 개선 비교 → 제출 숫자 대조.

## 이전 증거와 구분

- retrieval-evaluation.json·retrieval-review-20261023.json은 이전 RAG의 v1/후보0.35 기록이다. 이번 고정0.25·새 v2 전후 결과는 rag-issue3-revalidation.json이다. 수치를 직접 이어 붙이지 않는다.
- app-review-2666e44.json은 이전 App CI·별도 QA28 관찰이다. 최신 전체 QA의 실제 커밋·수치는 baseline.json이다.
- source-review-20261023.json은11:26 당시 Appb5d6835·RAG47ab39f 관찰이며 최신 전체 결과로 재사용하지 않는다.
- contract-audit-review-20261023.json의 INT-06 P0는 QA #4 수정 전 거짓 판정 재현이다. 최신 contract-audit.json이 대체한다.
- app-review.json의 App8c88f89·RAGf1ec584·Backenda82b7be 결과는 과거 기록이다. QA #1/#2/#4·Agent #1/#2/#3·RAG #1/#2의 해결도 이후 변경의 자동 합격이 아니다.

## 다른 컴퓨터 준비와 재현

Git·Python3.12·Docker(pgvector/pgvector:pg17)가 필요하다. 검증 환경은 macOS/Python3.12.14이며 다른 OS 설치는 미검증이다. 같은 부모 폴더에 README의7개 저장소를 clone하고 가상환경을 새로 만든다. 기존 절대 경로 링크·.env·DB URL은 복사하지 않는다.

```sh
cd qa
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-runtime.lock.txt
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_checks.py --project-root .. --with-backend --output results/handoff-full-001
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_backend_tests.py --project-root .. --with-rag --rag-min-score 0.25 --output results/handoff-rag-api-001
```

새 holdout 전후 비교는 [두 고정 clone의 재현 절차](rag-issue3-revalidation.md)를 따른다. 이미 공개된 평가의 재현이며 새 독립 검증은 아니다. 기존 evaluate_retrieval.py는 노출된 v1 개발/holdout 진단용이다.
clone 시점 main과 manifest 검증 커밋을 비교하고 새 checkout에서 버전을 고정한다. 사용자 checkout을 reset하지 않는다. 새 App 코드는 review_required가 예상되며 실제 호출 경로 검토 후 registry·handoff를 갱신한다. 매 실행 새 출력 경로를 쓴다.

표준 전체 검사는 R3 운영 검색 미연결인 INT-07 partial로 exit1, v2 고정 전후 검색은 기준 미달로 exit1, RAG 주입 API는21/21이면 exit0이 예상된다. 환경 오류와 알려진 실패를 혼동하지 않는다. 표준 공개 증거는 전체 명령에 --reports reports를 추가하고 별도 JSON은 검토 후 공개한다.
Backend 시험은 public schema를 삭제하므로 run_backend_tests.py가 새로 만든 폐기 DB만 사용한다. 배포 설정을 QA 준비로 쓰지 않는다. 실제 모델·임베딩은 사용자가 요청한 목적·범위·비용 안에서만 실행한다.

## 저장소 밖 자료

교재·원본 PPTX/PDF 양식은 별도 공유 폴더로 전달한다([참고 안내](reference/README.md)). 실제 사진·개인정보는 검토·접근 범위를 확인한 별도 보관처로 관리한다. 키·토큰·.env·실제 사진·원시 로그는 공개하지 않는다. 재현 절차·커밋·검토된 증거가 필수 인수인계이며 이전 AI 대화 전체는 필수 의존성이 아니다.
