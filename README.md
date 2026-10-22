# 한길 R6 QA/Eval

한길(Hangil) 미니프로젝트의 QA·평가 자료와 재현 실행기입니다.
담당: 이현무(R6). 공개 저장소: https://github.com/team-onetruck/oneload-qa

기준은 2026-10-22의 API·시퀀스 설계 v0.3, 시스템·AI 설계 v0.2입니다.
현재 MVP는 모바일 웹의 2D 노선 안내와 360도 거리뷰입니다. 실시간 AR은 후속 범위입니다.

## 현재 확인 결과

| 검증 | 결과 | 의미 |
|---|---|---|
| Agent 기존 테스트 | 37/37 통과 | FakeLLM 기반 |
| Backend 기존 테스트 | 44/44 통과 | 일회용 PostgreSQL, 기본 Agent/Vision 대역 |
| R6 컴포넌트 평가 v2 | 20/20 시나리오, 21/21 턴 자동 검사 통과 | 실제 Backend context·지도·guard + FakeLLM·모의 검색 |
| R2↔Backend API 연결 | 11개 확인 중 10개 통과, 1개 실패 | 사진 인식 장애에서 503 대신 500 |
| 실제 AI·사진 정확도 | 미측정 | 실제 모델 호출·공식 RAG·현장 사진 평가 전 |

Frontend는 모의 구현이고 Backend 기본 실행은 RuleAgent/NoVision입니다.
위 연결 검사는 QA에서 R2를 명시적으로 주입한 결과입니다. 서비스 전체 연결 완료로 해석하지 않습니다.

- [최신 검토 결과와 버전](reports/latest-review.md)
- [해결된 규격 차이와 남은 통합 문제](docs/integration_findings.md)
- [저장소 구조](docs/repository-status.md)
- [R6 테스트 계획](docs/test_plan.md)
- [서비스 평가 초안 20문항](eval/service_gold.csv)
- [기능 인수조건 16건](eval/functional_cases.csv)
- [사진 정답 목록: 현재 0건](eval/photo_manifest.csv)

## 실행 준비

세 코드 저장소와 QA를 같은 부모 폴더 아래에 둡니다. QA는 로컬 이름을 qa로 지정합니다.

~~~text
project/
  oneload-app/
  oneload-backend/
  oneload_agent/
  qa/                 # oneload-qa 저장소
~~~

~~~sh
git clone https://github.com/team-onetruck/oneload-qa.git qa
cd qa
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-runtime.lock.txt
~~~

기준 실행 환경은 Python 3.12.14입니다. 런타임 고정 목록은 실제 검증 환경을 기록하며,
팀 전체의 배포 의존성 파일을 대체하지 않습니다.

### Agent 기존 테스트

oneload_agent 폴더에서 실행합니다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 LANGSMITH_TRACING=false LANGCHAIN_TRACING_V2=false ../qa/.venv/bin/python -m pytest -q -p no:cacheprovider
~~~

### 계약 점검

이하 명령은 qa 폴더에서 실행합니다. 미해결 P0가 있으면 종료 코드 1을 반환합니다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/audit_contracts.py --project-root .. --output results/audit-local.json
~~~

### Agent 흐름 평가

~~~sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_agent.py --project-root .. --cases eval/component_cases.json --mode fake --prompt-version v3 --output results/agent-run-001
~~~

기본 실행은 FakeLLM과 MockKnowledgeSearch입니다. 사람 검토 칸은 비워 두며 자동 통과를 AI 정확도로 집계하지 않습니다.
현재 평가셋은 r6-component-v2입니다. Agent의 공개 계약이 바뀌어 새 기준선을 만들었습니다.
archive의 v1과 점수를 직접 비교하지 않습니다. 출력 폴더는 매 실행 새 이름을 사용합니다.

실제 모델은 키·모델명을 준비한 뒤 --mode openai로 명시적으로 선택합니다.
이때도 검색은 모의 자료이므로 '실제 모델 + 모의 검색' 결과입니다.
OpenAILLM은 Agent 저장소의 .env를 읽거나 템플릿으로 생성할 수 있습니다. 키는 이 저장소에 넣지 않습니다.

### Backend + R2 연결 검사

Docker가 실행 중이어야 합니다. 기존 Backend 테스트는 public schema를 삭제하므로,
운영·개인 DB URL로 직접 실행하지 않고 다음 실행기를 사용합니다.

~~~sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_backend_tests.py --project-root .. --with-r2 --output results/backend-run-001
~~~

무작위 이름과 로컬 포트로 일회용 PostgreSQL을 만들고 자신이 만든 컨테이너만 제거합니다.
기존 DATABASE_URL/TEST_DATABASE_URL은 사용하지 않습니다. 합성 JPEG와 FakeLLM만 사용합니다.
현재 INT-08이 재현되므로 전체 종료 코드는 1입니다. Backend 기존 44개 테스트 결과와 별도로 기록됩니다.
--with-r2를 빼면 Backend 기존 테스트만 실행합니다.

## 결과 관리

실행 원본은 results/에 로컬로 보관하고 Git에서 제외합니다.
공개용으로 검토한 요약·구조화된 증거는 reports/에 둡니다.
.env, 가상환경, 사진 원본, 원시 로그, 세션 토큰은 업로드 대상에서 제외합니다.
서비스 정답은 공식 자료·현장 확인 후 고정하며, 현재 service_gold의 정답 근거는 검토 대기입니다.
