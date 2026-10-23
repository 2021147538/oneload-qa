# 저장소 구조와 현재 버전

2026-10-23 08:38 KST에 다음 버전으로 전체 QA를 실행했습니다.
아래 표는 reports/baseline.json의 FakeLLM·모의 검색 검사 대상입니다.
그 뒤 Backend·Infra·RAG에 변경이 추가됐습니다. 최신 관찰 커밋은 [repos.lock.json](../repos.lock.json),
차이와 다음 검증은 [인수인계](handoff.md)에 기록합니다. 새 관찰 버전을 기존 통과 결과로 대체하지 않습니다.

| 저장소 | 커밋 | 역할 |
|---|---|---|
| oneload-app | bc2d9f1 | React 웹 프로토타입, 실제 API 연결 전 |
| oneload-backend | a82b7be | FastAPI·PostgreSQL 코드, 고정 시험 fixture |
| oneload_agent | 250271e | LLMAgent·Vision·모의 지식·프롬프트 v3 |
| oneload-data | 606f648 | 실제 실행 지도·예시 파노라마·지도 스키마 |
| oneload-infra | 3dcccd8 | Caddy·launchd·배포 설정 |
| oneload-qa | 이 저장소 | 독립 QA 검사·평가셋·검증 증거 |

## 코드·데이터 분리 후 구조

~~~text
project/
  oneload-app/src/                  모의 세션·AI·경로·360도 거리뷰
  oneload-backend/
    app/api/, app/ai/, app/domain/  API·계약·guard·경로·위치 매칭
    tests/fixtures/maps/           고정 지도, 기존 44개 시험
    migrations/                    DB 마이그레이션
  oneload_agent/
    hangil_r2/                     Agent·사진 특징 추출·Backend 타입 사본
    mocks/maps/                    Agent 자체 시험용 지도 사본
    prompts/, tests/, docs/        프롬프트·43개 시험·FAQ
  oneload-data/
    maps/                          실제 통합 검사·서버 실행 지도
    panos/                         현재는 타 역 예시 사진 4개
    schema/, tools/                지도 스키마·자체 검증 도구
  oneload-infra/macserver/          배포 스크립트·Caddy·launchd
  qa/
    scripts/qa_inputs.py            공통 지도 선택·데이터·커밋 메타데이터
    scripts/validate_data.py        Backend 모델·참조·스키마·사진 파일 검사
    scripts/run_checks.py           전체 검사·공개 증거 갱신
    tests/                         경로·누락·명시적 지도 선택 등 회귀 검사
    eval/                          서비스 초안·기능 TC·사진 명세·컴포넌트 v2
    reports/                       현재 버전의 공개 증거
    results/                       Git 제외 실행 원본
~~~

Backend 내부의 옛 data/maps 경로는 삭제됐습니다.
현재 통합 대상 지도는 oneload-data/maps/seoul-station.json이며
map version은 2026-10-22.1입니다.
Backend·Agent 고정 fixture는 시험 안정성을 위한 자료로 따로 기록합니다.

## QA 수정 기록

모든 지도 관련 실행기가 공통 경로 해석을 사용하도록 바꿨습니다.
명시적 --map-dir를 컴포넌트·감사·실제 API 앱까지 전달합니다.
지도 누락 시 빈 MapStore를 Agent에 전달하지 않고 실행 초기에 중단합니다.
실제 지도와 고정 fixture가 달라도 원인이 데이터 갱신인지 구분할 수 있도록 메타데이터를 남깁니다.

관련 저장소 5개의 커밋과 지도·사진 해시가 검사 중 바뀌면 공개 증거 갱신을 막습니다.
새 경로의 회귀 시험 6개와 데이터 검사 3개를 전체 실행에 추가했습니다.

QA #2에서는 INT-08을 사본 클래스 비교 대신 실제 Vision 장애 발생 시 Backend가 잡는지로 판정합니다.
정상 Agent, 사본 예외, 다른 예외, 장애 누락, Backend 예외 하위 클래스의 5개 회귀 시험을 추가했습니다.
QA 11개·Agent 43개·Backend 44개·API 20개 검사가 통과했고 INT-06/07은 남아 있습니다.

이전 Agent Git 이력 복구는 [별도 기록](git-sync.md)에 있습니다.
Frontend build·모바일 브라우저와 배포 실행은 이번 QA 범위에서 미실행입니다.
실제 모델·공식 RAG·현장 사진 정확도도 미측정입니다.


## 인수인계와 RAG

oneload-rag는 표준 run_checks.py의 5개 입력 저장소에 포함되지 않습니다.
별도 이슈 재검증은 RAG f1ec584에서 82개 시험·HTTP 조립 6개가 통과했으며 GitHub 이슈 댓글에 증거가 있습니다.
최근 관찰한 2446979에는 Backend 연결 패치 초안과 E2E 도구가 추가됐습니다. Backend 반영·운영 적용·새 조합 검증은 별도입니다.
이후 개발·검증·이슈 변경은 AGENTS.md에 따라 handoff와 버전 기록을 같은 작업에서 갱신합니다.
