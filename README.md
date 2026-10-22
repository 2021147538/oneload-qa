# 한길 R6 QA/Eval

한길(Hangil) 미니프로젝트의 QA·평가 자료와 재현 실행기입니다.
담당: 이현무(R6). 공개 저장소: https://github.com/team-onetruck/oneload-qa

기준은 2026-10-22의 API·시퀀스 설계 v0.3, 시스템·AI 설계 v0.2입니다.
현재 MVP는 모바일 웹의 2D 노선 안내와 360도 거리뷰이며 실시간 AR은 후속 범위입니다.

## 현재 확인 결과

| 검증 | 결과 | 의미 |
|---|---|---|
| QA 회귀 테스트 | 11/11 통과 | 지도 입력 6건·실제 사진 장애 예외 판정 5건 |
| 데이터 검사 | 3/3 통과 | Backend 모델·참조, 스키마 사본 일치, 사진 파일 존재 |
| Agent 기존 테스트 | 43/43 통과 | FakeLLM 기반 |
| Backend 기존 테스트 | 44/44 통과 | 일회용 PostgreSQL, 고정 시험 fixture |
| R6 컴포넌트 평가 v2 | 20/20 시나리오·21/21 턴 자동 검사 통과 | oneload-data 지도·실제 Backend context/guard + 모의 AI |
| R2↔Backend API 연결 | 20/20 확인 통과 | 사진 장애에서 503 / AI_SERVICE_UNAVAILABLE 확인 |
| 실제 AI·사진 정확도 | 미측정 | 실제 모델·공식 RAG·현장 사진 평가 전 |

2026-10-23에 Agent 250271e·Backend a82b7be·oneload-data 606f648 기준으로 다시 실행했습니다.
[QA #2](https://github.com/team-onetruck/oneload-qa/issues/2)의 INT-08 거짓 실패를 수정했습니다.
사진 장애를 실제로 발생시켜 Backend가 잡는 예외를 확인하며 잘못된 예외·장애 누락도 회귀 검사합니다.
Frontend는 모의 구현이고 Backend 기본 실행은 RuleAgent/NoVision입니다.
API 연결 검사는 QA에서 R2를 주입한 결과이며 서비스 전체 연결 완료로 집계하지 않습니다.

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

관련 저장소 5개와 QA를 같은 부모 폴더에 둡니다. QA의 로컬 폴더 이름은 qa입니다.

~~~text
project/
  oneload-app/
  oneload-backend/
  oneload_agent/
  oneload-data/       # 실제 지도·예시 파노라마
  oneload-infra/      # 배포 설정; QA는 커밋만 기록
  qa/                # oneload-qa 저장소
~~~

빈 project 폴더에서 준비하는 예시입니다.

~~~sh
git clone https://github.com/team-onetruck/oneload-app.git
git clone https://github.com/team-onetruck/oneload-backend.git
git clone https://github.com/team-onetruck/oneload_agent.git
git clone https://github.com/team-onetruck/oneload-data.git
git clone https://github.com/team-onetruck/oneload-infra.git
git clone https://github.com/team-onetruck/oneload-qa.git qa
cd qa
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-runtime.lock.txt
~~~

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

INT-08은 통과했고, 실제 연결 전 항목 INT-06/07 때문에 전체 종료 코드는 1입니다.
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
