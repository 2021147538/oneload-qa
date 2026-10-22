# Agent FAQ와 QA 검증 연결

기준 문서: [oneload_agent 7b7501f FAQ](https://github.com/team-onetruck/oneload_agent/blob/7b7501f8606dd5a5948892c881382e032c65a0e6/docs/FAQ.md).
FAQ의 구현 설명을 검사 대상으로 사용하며, 완료 여부는 실제 실행 증거로 판정합니다.

| FAQ 항목 | QA 검사·확인 방법 | 현재 판정 |
|---|---|---|
| Q1 /messages와 /localizations 연결 | API-04·05·15, 현재 Backend 기본 entrypoint 별도 확인 | QA 주입 경로 통과. 실제 기본 연결은 INT-07 대기 |
| Q3·Q4 모의 평가의 의미 | 기존 37개 시험, 컴포넌트 v2 20시나리오·21턴 | 자동 구조 검사 통과. 실제 정확도 아님 |
| Q5 Backend 사본 계약 | audit INT-01~05 | 스키마·enum·지도·정상 API 통과. 예외 클래스 INT-08은 실패 |
| Q6 검증된 목적지·등록 경로 | API-07·14 | 등록 경로 사용·미등록 목적지 거부 통과 |
| Q7 열차·교통카드 분기 | API-01·02·03·10·11 | 직통 영어·일반 카드 있음/없음 및 슬롯 저장 통과 |
| Q8 근거 있는 열차 비교 | API-12·16 | 비교 출처 사용, 근거 없을 때 확인 전 표시 통과 |
| Q9 요금 근거 없음 | API-13 | cannot_answer, 출처·숫자 추측 없음 통과 |
| Q10 대화 모델 장애 | API-09 | RuleAgent fallback 통과 |
| Q10 사진 모델 접속 장애 | INT-08-vision-down | 기대 503, 실제 500. FAQ의 복구 설명을 충족하지 못함 |
| Q10 사진 결과 형식 오류 | API-17·18 | no_match·재촬영 안내·수동 위치 확정 통과 |
| Q12 실제 사진 후보 정확도 | photo_manifest와 현장 정답 필요 | 사진 0건, 미측정 |
| Q13 시각표 기본 비활성 | API-12 | 시각표 미주입 시 도착시각 items가 비어 있음 |
| Q14 R3 근거·열차 필터 | R2 기존 시험·컴포넌트 출처 추적, 실제 R3 연결 후 재시험 | 모의 검색만 확인, 공식 RAG 대기 |
| Q15 평가 결과 일치 | run_checks.py가 커밋·CSV 수·실행기 해시를 대조 | 현재 보고서 갱신. Agent experiments/검증 결과서와 실제 모델 수치 일치는 추후 |
| Q17 같은 평가셋으로 비교 | component_cases.json v2 SHA 유지 | 이번에는 질문·정답 변경 없음, API 검사만 확장 |

모든 API 검사는 실제 Backend+R2 코드, 일회용 DB, FakeLLM, 모의 검색, 합성 JPEG로 실행했습니다.
[API 결과](../reports/integration-probe.json)와 [통합 문제](integration_findings.md)를 함께 봅니다.
FAQ 연결 예시에서 LLMAgent.vision 주입이 빠져 있으므로 사진 질문 처리에는 이를 별도로 연결해야 합니다.

## 공유 데이터 분리 후 재검증

현재 API·컴포넌트 결과는 Backend a82b7be와 oneload-data 606f648 기준입니다.
실제 공유 지도 경로와 고정 시험 fixture 경로를 구분했습니다.
QA 자체 감사는 새 경로로 정상 실행하며, Agent의 check_backend_compat.py는
[Agent #3](https://github.com/team-onetruck/oneload_agent/issues/3)의 별도 수정 대상입니다.
