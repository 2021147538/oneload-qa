# 한길 R6 QA/Eval

한길(Hangil) 미니프로젝트의 QA·평가 자료와 재현 실행기입니다.
담당: 이현무(R6). 공개 저장소: https://github.com/team-onetruck/oneload-qa

기준은 2026-10-22의 API·시퀀스 설계 v0.3, 시스템·AI 설계 v0.2입니다.
현재 MVP는 모바일 웹의 2D 노선 안내와 360도 거리뷰이며 실시간 AR은 후속 범위입니다.

다른 AI·컴퓨터에서 이어받을 때는 **[인수인계](docs/handoff.md)**부터 읽습니다. 시작 프롬프트는 인수인계 시 채팅으로만 제공합니다.
작업자는 [AGENTS.md](AGENTS.md)의 인수인계 갱신 절차를 따릅니다. 설계 사본은 [참고 자료](docs/reference/README.md)에 있습니다.
[repos.lock.json](repos.lock.json)은 최근 관찰 버전과 마지막 검증 버전을 구분합니다. 표준 QA와 별도 RAG 검사의 커밋·범위를 구분합니다. 소스 커밋 기록은 Frontend UI·Infra 배포 검증을 뜻하지 않습니다.

## 마지막 전체 QA 확인 결과

2026-10-23 13:33 KST, App2666e44·Backendc9b8d8a·Agent54c321f·Data606f648·Infra8587d3b에서 다시 실행했습니다.

| 검증 | 결과 | 의미 |
|---|---|---|
| QA 회귀 테스트 | 38/38 통과 | 기존28 + holdout 검증6 + Agent 패키지 자산4 |
| 데이터 검사 | 3/3 통과 | 모델·참조·스키마·파일 존재 |
| Agent 기존 테스트 | 43/43 통과 | FakeLLM 기반 |
| Backend 기존 테스트 | 48/48 통과 | 새 일회용 PostgreSQL |
| R6 컴포넌트 v2 | 20/20 시나리오·21/21 턴 | 실제 Backend context/guard + 모의 AI |
| R2↔Backend API | 20/20 | 명시적 주입·모의 검색 |
| 별도 RAG API | 21/21 | RAGe6c03f2·MemorySearch0.25·FakeLLM |
| 새 R6 검색 holdout v2 | top3 17/20·범위밖 빈 결과17/20 | 오탐3·정상 질문 누락3, 기준 미달 |
| 실제 AI·사진 정확도 | 미측정 | 사람 검토·현장 평가 대기 |

[RAG #3 답글 재검증](docs/rag-issue3-revalidation.md): 새 질문40개를 QA7f41130으로 검색 전에 고정한 뒤 수정 전47ab39f/후e6c03f2를 각1회 비교했습니다. 원래 호텔 가격·빈 좌석2건은 수정됐지만 새 오탐과 누락이 남아 RAG #3과 QA #3을 open으로 유지합니다. 임계값은 양쪽 모두0.25로 고정했고 재조정하지 않았습니다.

Agent 패키지의 실제 PROMPT_DIR/MOCK_DIR에 맞춰 평가 실행기의 자산 검사·해시 경로를 수정했습니다. component v2의 질문·정답·SHA는 유지했습니다.
Frontend HTTP 연결 소스는 App2666e44에서 wired입니다. [QA #4 수정 원칙](docs/issue4-resolution.md)을 유지하며 **이번 실제 서버·휴대폰 브라우저 인수는 NOT_RUN**입니다. App CI365+E2E4는 [별도 관찰 기록](reports/app-review-2666e44.json)입니다.
남은 P0는 Backend 기본 RuleAgent/NoVision(INT-07)이며 전체 exit1입니다. 현장 데이터(DATA-01)도 남아 있습니다. 실제 모델·임베딩 호출0회입니다.

- [최신 결과와 버전](reports/latest-review.md)
- [데이터 검사 증거](reports/data-validation.json)
- [남은 통합 문제와 이슈](docs/integration_findings.md)
- [저장소 구조](docs/repository-status.md)
- [R6 테스트 계획](docs/test_plan.md)
- [Agent FAQ와 QA 검증 연결](docs/faq-qa-traceability.md)
- [Git 동기화 처리 기록](docs/git-sync.md)
- [서비스 평가 초안 20문항](eval/service_gold.csv)
- [기능 인수조건 16건](eval/functional_cases.csv)
- [현장 사진 정답 목록: 현재 0건](eval/photo_manifest.csv)

## 실행 준비

표준 QA 대상 5개와 QA를 같은 부모 폴더에 둡니다. 인수인계에는 별도 RAG 검사용 oneload-rag도 함께 준비합니다. QA의 로컬 폴더 이름은 qa입니다.

~~~text
project/
  oneload-app/
  oneload-backend/
  oneload_agent/
  oneload-data/       # 실제 지도·예시 파노라마
  oneload-infra/      # 배포 설정; QA는 커밋만 기록
  oneload-rag/        # R3 검색; 표준 QA와 별도 검증
  qa/                # oneload-qa 저장소
~~~

빈 project 폴더에서 준비하는 예시입니다.

~~~sh
git clone https://github.com/team-onetruck/oneload-app.git
git clone https://github.com/team-onetruck/oneload-backend.git
git clone https://github.com/team-onetruck/oneload_agent.git
git clone https://github.com/team-onetruck/oneload-data.git
git clone https://github.com/team-onetruck/oneload-infra.git
git clone https://github.com/team-onetruck/oneload-rag.git
git clone https://github.com/team-onetruck/oneload-qa.git qa
cd qa
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-runtime.lock.txt
~~~

가상환경은 컴퓨터마다 새로 만듭니다. 다른 컴퓨터의 .venv나 절대 경로 링크를 복사하지 않습니다.
검증 환경은 Python 3.12.14입니다. 의존성 목록은 QA 환경 기록이며 팀의 배포 의존성을 대체하지 않습니다.

## 지도 선택과 기록

- 실제 통합·컴포넌트 검사는 기본적으로 oneload-data/maps/seoul-station.json을 사용합니다.
- Backend 단위 테스트는 oneload-backend/tests/fixtures/maps의 고정 fixture를 사용합니다.
- Agent 단위 테스트는 Agent 저장소의 모의 fixture를 사용합니다.
- 고정 fixture와 실제 답사 데이터의 파일 내용이 달라도 그 차이만으로 계약 실패를 판정하지 않습니다.
- 지도 폴더·선택 파일이 없으면 모델 호출이나 Docker 시작 전에 명시적인 오류로 중단합니다.
- 필요하면 각 지도 관련 명령에 --map-dir 경로를 전달할 수 있습니다. 명시한 지도는 실제 API 앱의 MAP_DIR에도 적용됩니다.

공개 증거에는 관련 저장소 5개의 커밋, 실제 지도의 map_id·version·SHA256,
Backend 시험 fixture의 SHA256, 파노라마 파일 해시를 기록합니다.
실행 전후 커밋·작업 트리·지도·데이터 스키마·사진 해시를 대조합니다.

## 전체 점검과 공개 증거 갱신

Docker가 실행 중이어야 합니다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_checks.py --project-root .. --with-backend --output results/full-run-001 --reports reports
~~~

QA 회귀 테스트 → 데이터 검사 → Agent 시험 → 계약 감사 → 컴포넌트 평가 →
일회용 DB의 Backend·R2 API 검사를 실행합니다.
개별 실패도 기록하고 전체 실패 종료 코드를 유지합니다.
누락되거나 다른 버전의 증거가 섞이면 공개 보고서를 갱신하지 않습니다.
--reports는 --with-backend와 함께 사용하며, 매 실행 새 출력 폴더를 지정합니다.

INT-06은 검토된 소스 연결로 확인했고 INT-08은 통과했습니다. 남은 INT-07 때문에 전체 종료 코드는1입니다. 재검토되지 않은 App 코드도 review_required로 nonzero를 유지합니다.
자세한 단계별 종료 코드와 실제 실패 항목은 reports/baseline.json에 있습니다.
실행 원본은 results/, 공개용 구조화 증거는 reports/에 기록합니다.

## 개별 실행

이하 명령은 qa 폴더에서 실행합니다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/validate_data.py --project-root .. --output results/data-local.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/audit_contracts.py --project-root .. --output results/audit-local.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_agent.py --project-root .. --cases eval/component_cases.json --mode fake --prompt-version v3 --output results/agent-run-001
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_backend_tests.py --project-root .. --with-r2 --output results/backend-run-001
~~~

QA 테스트를 다른 경로의 사본에서 실행할 때는 QA_PROJECT_ROOT에 원본 project 경로를 지정합니다.
Agent 자체 시험은 oneload_agent 폴더에서 다음처럼 실행합니다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 LANGSMITH_TRACING=false LANGCHAIN_TRACING_V2=false ../qa/.venv/bin/python -m pytest -q -p no:cacheprovider
~~~

Backend 시험은 public schema를 삭제하므로 기존 DB URL로 직접 실행하지 않고 QA 실행기를 사용합니다.
실행기는 무작위 이름·로컬 포트의 일회용 PostgreSQL을 만들고 자신이 만든 컨테이너만 제거합니다.
--with-r2를 빼면 Backend 고정 fixture 시험만 실행합니다.

## 평가 수준과 결과 관리

전체 검사는 FakeLLM·모의 검색·합성 JPEG만 사용합니다. 실제 모델 호출은 없습니다.
컴포넌트 v2의 질문·기대값·SHA는 이전 버전과 같고 사람 검토 칸은 비워 둡니다.
서비스 평가셋은 공식 정답 근거 검토 대기이며 현장 사진 정답은 0건입니다.
데이터 저장소의 예시 파노라마 6개는 실제 서울역 인식 정확도 평가 자료가 아닙니다.

실제 모델 평가는 별도로 준비한 키·모델명과 evaluate_agent.py의 --mode openai로 명시적으로 선택합니다.
이때도 검색은 모의 도구이므로 '실제 모델 + 모의 검색' 평가입니다.
OpenAILLM은 Agent의 .env를 읽거나 템플릿으로 생성할 수 있습니다.

.env·가상환경·사진 원본·원시 로그·세션 토큰은 업로드 대상에서 제외합니다.
공개용으로 검토한 결과만 reports/에 둡니다.

## 실제 메모리 RAG 별도 검증

`oneload-rag` checkout이 필요합니다. 환경의 RAG_BACKEND·지식 폴더·커뮤니티 설정을 따르지 않고 공식 문서를 명시적으로 읽습니다. 키·모델·임베딩·운영 DB를 사용하지 않습니다.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_retrieval.py --project-root .. --output results/retrieval-001.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_backend_tests.py --project-root .. --with-rag --rag-min-score 0.25 --output results/rag-api-001
```

기존 evaluate_retrieval.py는 v1 개발셋으로 임계값을 고르고 노출된 holdout·R3셋을 측정하는 진단 실행기입니다. 과거0.35는 실험 후보이며 운영 확정값이 아닙니다. 이번 v2는 별도 recheck_rag_issue3.py로0.25를 고정해 전후 각1회 측정했습니다. [고정 커밋·새 clone 재현 절차](docs/rag-issue3-revalidation.md)를 따릅니다. v2도 이제 노출됐으므로 이후에는 회귀용이며 새 독립 검증으로 재사용하지 않습니다.
`--with-rag`는 `--with-r2`를 포함하고 RAG 누락 시 Docker 전에 중단합니다. 표준 `run_checks.py`는 계속 모의 검색을 사용합니다.
새 출력 경로로 실행하고 검토한 JSON만 공개합니다. 검색 보고서와 주입 API 보고서는 표준 기준선에 합산하지 않습니다.

## Frontend 소스 연결 감사

`eval/frontend_wiring.json`은 실제 HTTP 호출 경로를 검토한 App 런타임 소스·의존성의 해시를 기록합니다. mock 코드가 있다는 이유로 미연결로 판정하지 않습니다.

- 검토된 전체 연결: `wired`, 소스 검토만 통과. 실제 브라우저 인수는 NOT_RUN.
- 검토된 미연결: `incomplete`, INT-06 P0.
- 새 코드·의존성·파일 누락: `review_required`, nonzero. 연결/미연결로 단정하지 않음.

새 App 런타임 코드가 들어오면 [갱신 절차](docs/issue4-resolution.md)에 따라 호출 경로를 검토하고 새 기록을 추가합니다. 문서·테스트만 바뀌면 기존 소스 검토를 유지합니다. 전체 보고서 공개 전 registry 해시도 다시 대조합니다.
