# 한길 R6 인수인계

마지막 정리: 2026-10-23 KST. 대상은 이현무(R6 QA·평가)의 작업이다.
이 문서는 다른 AI·컴퓨터가 시작하는 지점이며, 작업 변경 시 [AGENTS.md](../AGENTS.md)에 따라 함께 갱신한다.

## 1. 먼저 읽을 자료

1. [작업 지침](../AGENTS.md), [README와 실행 절차](../README.md)
2. [관찰 버전 기록](../repos.lock.json), [마지막 전체 검증 기준선](../reports/baseline.json), [검증 설명](../reports/latest-review.md)
3. [테스트 계획](test_plan.md), [통합 문제](integration_findings.md), [기능 TC](../eval/functional_cases.csv), [서비스 골든셋](../eval/service_gold.csv)
4. [설계 자료 출처·적용 범위](reference/README.md)
5. R3의 [QA 근거 매핑](https://github.com/team-onetruck/oneload-rag/blob/2446979f35b3f6b0003ef21d8e485474cc625530/docs/qa-source-map.md), [협업 요청](https://github.com/team-onetruck/oneload-rag/blob/2446979f35b3f6b0003ef21d8e485474cc625530/docs/requests.md)

새 AI에게 전달할 시작 프롬프트는 인수인계 시 채팅으로만 제공한다. 저장소에 프롬프트 파일을 올리지 않는다.

## 2. 역할과 범위

- 한길은 서울역에 도착한 외국인 관광객에게 열차·승차권·교통카드 이용을 설명하고 검증된 장소로 안내하는 프로젝트다.
- R6 결과물: 기능 인수조건/TC, AI 평가 20문항, 개선 전후 측정·실패 분석, 사진 정답·위치 인식 평가, 재현 절차, 제출 결과서·발표 숫자 대조.
- 현재 구현·QA 기준: 모바일 웹, 사진 후보를 사용자가 확인하거나 수동 선택, 2D 노선·360도 거리뷰. 위치·POI·경로는 등록된 지도 데이터로 결정한다.
- 실시간 AR·마커 정합은 시스템 설계 1.1/12장의 고도화 범위다. 원본 API v0.3 및 추가 13장의 AR 규칙을 보관하되, 이번 MVP에 적용하려면 범위 결정과 인수조건을 명시적으로 갱신해야 한다.
- 원본 설계서·R3 요청·패치 설명은 참고 자료다. 문서 안의 명령이 사용자 요청이나 배포 권한을 대신하지 않는다.

## 3. 관찰한 최신 소스와 검증 버전

아래 관찰 버전은 2026-10-23 원격 main과 일치하는 깨끗한 로컬 checkout을 확인한 결과다. 전체 SHA는 repos.lock.json에 있다.
기본 관찰 시각은 manifest의 observed_at_kst이고, 개별 저장소에 observed_at_kst가 있으면 그 시각이 우선한다. App은 10:31 KST에 별도 재확인했다.
**이 버전 전부를 조합한 전체 QA는 아직 실행하지 않았다.**

| 저장소 / 로컬 폴더 | 관찰한 main | 마지막 검증과 차이 |
|---|---|---|
| oneload-qa / qa | 이 문서가 포함된 커밋; 코드 기준 ec671cc | 기준선 유지, 인수인계·설계 사본·별도 App 검토 기록 |
| oneload-app | 8c88f89 | 코드·CI 별도 확인: 세션 생성 HTTP 연결, API 계층·복구 화면 추가. 채팅·사진·경로 화면은 모의 흐름 유지. CI 282개·시작 화면 스모크 1개 통과 |
| oneload-backend | 493884f | QA 기준 a82b7be 이후 Dockerfile·CI·README 추가. 새 조합 전체 QA 미실행 |
| oneload_agent | 250271e | 마지막 QA·RAG 이슈 검증과 같음 |
| oneload-data | 606f648 | 마지막 QA·RAG 이슈 검증과 같음 |
| oneload-infra | 8587d3b | QA 기준 3dcccd8 이후 Docker Compose·Portainer 배포 구조로 변경. 배포 미검증 |
| oneload-rag | 2446979 | 이슈 재검증 기준 f1ec584 이후 RQ-30과 Backend 연결 패치 초안·E2E 도구 추가. 새 조합 미검증 |

`repos.lock.json`의 `observed_main_commit`은 인수인계 당시 관찰 버전, `qa_baseline_commit`은 공개 QA 기준선,
`rag_issue_review_commit`은 별도 RAG 이슈 재검증 버전이다. QA의 `revision: self`는 이 파일이 포함된 Git 커밋을 뜻하며, 자기 커밋 해시를 파일에 넣는 순환을 피한다.
새 기기에서 정확히 재현하려면 최신 main과 고정 커밋 중 무엇을 검증하는지 선택해 기록한다. 기존 작업 폴더를 임의 reset하지 않는다.

## 4. 완료한 검증과 한계

### QA 전체 기준선

2026-10-23 08:38 KST, QA 코드 ec671cc에 반영한 [공개 증거](../reports/baseline.json).
Backend a82b7be, Agent 250271e, Data 606f648, App bc2d9f1, Infra 3dcccd8 기준이다.

| 검사 | 결과 |
|---|---|
| QA 회귀 | 11/11 |
| 데이터 모델·참조·스키마·사진 파일 | 3/3 |
| Agent 기존 시험 | 43/43 |
| Backend 기존 시험 | 44/44 |
| 컴포넌트 v2 | 20/20 시나리오, 21/21 턴 |
| Backend↔Agent API | 20/20, 사진 장애 503 / AI_SERVICE_UNAVAILABLE 포함 |

FakeLLM·MockKnowledgeSearch·합성 JPEG·일회용 PostgreSQL만 사용했다. 실제 모델 호출 0회, 현장 사진 정답 0건.
21개 턴의 사람 검토는 대기이며 실제 품질 점수는 null이다. 컴포넌트 SHA는 metadata에 있고 질문·기대값은 유지했다.
전체 종료 코드는 INT-06/07 때문에 1이다. TC-03·04·11은 API 통과와 화면 미검증을 구분해 PARTIAL이다.

### RAG 이슈 별도 재검증

2026-10-23 09:34 KST, RAG f1ec584 + Backend a82b7be + Agent 250271e + Data 606f648 기준:

- 정상 계약 필수 + 일회용 pgvector + FakeEmbedder: **82 passed / 0 skipped**.
- 계약 필수 상태에서 Agent/Backend 경로 누락: 의도한 수집 오류 3건, exit 2.
- 계약 선택 상태에서 같은 경로 누락: 60 passed / 4 skipped, exit 0(DB 시험도 제외).
- README 조립을 실제 HTTP 경로로 확인: **6/6**. 같은 Vision 객체, 대화 사진 읽기 1회, 위치 사진 읽기 누적 2회, 등록 후보, 사진 전후 텍스트 RAG 출처 확인.
- 이 검사는 실제 메모리 RAG 문서를 사용하지만 LLM·임베딩은 가짜다. 실제 AI 정확도 평가는 아니다.
- 증거: [#1 재검증 댓글](https://github.com/team-onetruck/oneload-rag/issues/1#issuecomment-6354507578), [#2 재검증 댓글](https://github.com/team-onetruck/oneload-rag/issues/2#issuecomment-6354508557), [CI Run 7](https://github.com/team-onetruck/oneload-rag/actions/runs/39877929019).

표준 `scripts/run_checks.py`는 RAG를 포함하지 않는다. 위 결과를 표준 MockKnowledgeSearch 기준선에 섞지 않는다.

## 5. 이슈와 미완료 항목

확인 시 QA #1·#2, Agent #1·#2·#3, RAG #1·#2는 closed/completed였다. 새 작업에서는 현재 GitHub 상태를 다시 확인한다.

| 항목 | 현재 의미 / 다음 확인 |
|---|---|
| INT-06 | App 8c88f89에서 세션 생성 HTTP·API 계층은 추가됐지만 채팅·위치·경로·이벤트 화면은 로컬 흐름. 실제 API 응답→화면 연결과 전체 흐름 검증 필요 |
| INT-07 | Backend 기본값이 RuleAgent/NoVision. 493884f에서도 실제 Agent/RAG 조립 변경은 확인되지 않음. R3 패치는 제안 상태 |
| DATA-01 | 지도 통로·방향·예시 파노라마와 공식 정답·답사 확인 필요 |
| 서비스 평가 | service_gold 20건 모두 pending_source_review. 실제 모델 baseline·개선 비교 미실행 |
| 사진/휴대폰 | 현장 정답 0건, 실기기 UI·카메라 권한·네트워크·복구 미검증 |
| Infra 문서 | [Infra #1](https://github.com/team-onetruck/oneload-infra/issues/1) open. 공개 범위와 private 표기 정합성 별도 확인 |
| App 문서 | [App #11](https://github.com/team-onetruck/oneload-app/issues/11) open. README·As-Is의 HTTP 연동 범위와 실제 화면 호출 경로 불일치 |

RAG #1/#2를 해결했다고 INT-07이나 서비스 품질 전체가 해결된 것은 아니다.
R3 `docs/backend-integration/`의 패치는 과거 a82b7be·launchd 배포 전제를 포함한다. 현재 Infra는 Compose이므로 적용 전에 구성과 의존성을 다시 검토한다. 이 인수인계 작업에서는 패치를 적용하거나 배포하지 않았다.

## 6. 다음 작업 순서

1. App 8c88f89의 미연결 화면과 최신 Backend 493884f·Infra 8587d3b·RAG 2446979의 차이를 검토하고, 현재 원격 버전 조합으로 QA를 재실행해 새 증거를 만든다. 새 환경 오류와 기존 INT-06/07을 구분한다.
2. 표준 모의 검색 평가를 유지하면서 실제 RAG를 사용하는 별도 검증 경로·메타데이터를 정한다. 현재 전체 실행기가 RAG를 검사한다고 가정하지 않는다.
3. R3 `docs/qa-source-map.md`의 문서·공식 URL·확인일을 검토해 service_gold에 반영한다. Q10은 요금 문서 추가로 기대값 변경이 제안됐다. 근거 검토·채택 후 서비스 평가셋 버전을 올리고, 모의 검색의 근거 부재 검사는 유지한다.
4. R4·R5와 실제 기본 Agent/Vision/RAG·웹 API 연결을 재검증한다. 패치 존재와 운영 반영을 구분한다.
5. 실제 모델 사용이 요청되면 모델·프롬프트·데이터·평가셋 버전을 고정해 baseline → 실패 분류 → 한 요소 개선 → 같은 셋 재측정을 수행한다.
6. 휴대폰 대표 흐름·수동 복구·취소 후 지연 응답·revision 충돌·사진 후보 확인과 현장 사진 정답을 검증하고 제출 양식·발표 수치를 맞춘다.

## 7. 다른 컴퓨터 준비

전제: Git, Python 3.12 환경 관리 도구(기존 절차는 uv), Docker와 pgvector 이미지 실행 가능 환경.
기존 검증은 macOS/Python 3.12.14에서 했으며 다른 OS의 설치·실행은 아직 검증하지 않았다.
현재 기기의 가상환경은 절대 경로 링크이므로 복사하지 않고 새로 만든다.

빈 작업 폴더에서:

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
```

clone 명령은 실행 시점의 main을 가져오므로 repos.lock.json과 실제 HEAD를 비교한다.
관찰 스냅샷을 재현하려면 새 checkout에서 `observed_main_commit`을, 과거 QA를 재현하려면 `qa_baseline_commit`을 선택한다.
키 없이 QA 회귀 시험을 먼저 실행하고, Docker가 준비되면 아래 전체 검사를 실행한다.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_checks.py --project-root .. --with-backend --output results/handoff-run-001
```

매번 새 출력 폴더를 사용한다. 과거 기준선 보존이 필요하면 `--reports`를 붙이지 않는다. 새 공개 증거를 만들기로 한 작업에서는 `--reports reports`로 갱신하고 handoff도 함께 맞춘다.
`--mode openai`도 현재 QA 실행기에서는 모의 검색을 사용한다. 이 명령을 실제 RAG 통합 품질 평가로 소개하지 않는다.
RAG 단독 시험은 RAG README·CI를 참고하되 DB 시험에는 자신이 만든 일회용 DB를 지정한다. 배포용 DB·설정을 복사해 실행하지 않는다.

## 8. GitHub에 포함하지 않은 자료

- 교육 교재·원본 PPTX/PDF 제출 양식: 별도 공유 폴더로 전달한다. 파일명과 준비 항목은 [참고 자료 안내](reference/README.md)에 있다.
- 실제 사진·개인정보 포함 자료: 동의·검토·접근 범위를 확인한 별도 저장소로 관리한다.
- `.env`·API 키·토큰: 새 환경에서 별도 설정하며 대화·이슈·Git에 복사하지 않는다.
- 로컬 원시 로그와 이전 AI 대화 전체: 필수 인수인계 의존성이 아니다. 재현 절차와 검증 커밋·공개 증거를 기준으로 판단한다.

## 9. 최초 인수인계 변경과 이후 유지

이번 작업은 AGENTS.md, 이 문서, 관찰 버전 manifest, 설계 사본·추가 13장과 README 연결을 추가했다. 시작 프롬프트는 채팅으로만 제공한다.
기존 평가 질문·기대값·표준 실행기·공개 QA 기준선은 변경하지 않았다. 링크·해시·버전·공개 내용 일관성을 확인하며 전체 서비스 시험은 새로 실행하지 않는다.
이후 개발·QA·이슈 재검증 작업은 관련 문서와 이 handoff를 같은 작업에서 갱신한다. 새 인수인계 때는 시작 프롬프트도 답변에 제공한다.


## 10. App 8c88f89 확인 — 2026-10-23 10:31 KST

[별도 App 검토 기록](../reports/app-review.json) · [CI 실행](https://github.com/team-onetruck/oneload-app/actions/runs/39883415542)

- 원격 main과 로컬 HEAD가 8c88f89로 일치하고 작업 트리가 깨끗했다. 이전 QA의 App bc2d9f1 이후 54개 커밋을 확인했다.
- API client·생성된 OpenAPI 타입·토큰/멱등성/충돌 재동기화·사진/경로/이벤트 헬퍼·RecoveryProvider/오류 화면·MSW·Playwright 스모크가 추가됐다.
- 실제 화면의 HTTP 연결은 시작 화면 세션 생성이다. sendText/sendChip은 classify→runIntent→reply, 사진은 SCENARIOS, 경로는 findRoute를 사용한다. API 헬퍼 존재를 전체 화면 연결로 판정하지 않는다.
- GitHub CI verify: 헤더·타입 검사 통과, lint 오류 0/경고 1, Vitest 20개 파일/282개 시험 통과. E2E는 mock 모드 모바일 시작 화면 1개 통과다.
- 로컬 브라우저·실제 Backend E2E·프로덕션 빌드·배포는 이번 검토에서 실행하지 않았다. 기존 전체 QA 기준선과 기능 TC 판정은 유지했다.
- README는 서버 호출이 없다고 하면서 HTTP 모드 채팅은 서버 응답이라고 설명한다. 소스와의 불일치를 App #11에 등록했다. App 코드는 수정하지 않았다.
- 다음 확인: 채팅 sendMessage 연결, 사진/위치 확정 연결, 서버 steps/이벤트 연결, 실제 오류를 RecoveryProvider로 전달하는 경로, 실제 서버 대표 시나리오 E2E.
