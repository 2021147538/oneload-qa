# 최신 QA — 2026-10-23 11:36 KST

QA #4의 INT-06 거짓 미연결 판정을 수정하고 최신 Backend 대화 복원·멱등성 변경을 포함해 다시 검증했다.

| 대상 | 버전·범위 | 결과 |
|---|---|---|
| QA | 기존17건+Frontend 회귀11건 | 28/28, skip0 |
| 데이터 | 606f648 | 3/3 |
| Agent | 250271e·FakeLLM | 43/43 |
| Backend | c9b8d8a·일회용 DB | 48/48 |
| 컴포넌트 v2 | 기존 질문·기대값·SHA 유지 | 20시나리오·21턴 자동 검사 통과 |
| 표준 R2↔Backend API | 모의 검색·합성 JPEG | 20/20 |
| 별도 RAG API | RAG47ab39f·MemorySearch0.35·FakeLLM | 21/21 |
| Frontend 소스 | Appb5d6835·검토 기록 대조 | wired, 실제 브라우저 NOT_RUN |
| Infra | 8587d3b | 커밋 기록만, 배포 미실행 |

[전체 기준선](baseline.json) · [계약 감사](contract-audit.json) · [Frontend 스냅샷](frontend-wiring-review.json) · [모의 API](integration-probe.json) · [RAG API](rag-integration-probe.json)

## 해결한 QA #4

mock 분기 문자열이 남았다는 이유만으로 실제 HTTP 화면을 미연결로 보고하지 않는다. 검토한 호출 경로와 런타임 소스·의존성 해시를 연결했다. 기존 bc2d9f1·b111af6은 incomplete/P0, 최신 b5d6835는 wired, 미검토 코드는 review_required/nonzero다.

실제 Git 스냅샷3개와 현재 체크아웃으로 재현했다. 어댑터·의존성 변경·삭제·추가, 주석/미사용 helper, 문서/테스트 변경 등을 회귀로 검사했다. 실행 중 registry가 바뀌면 보고서를 갱신하지 않는다. [판정과 유지 절차](../docs/issue4-resolution.md).

wired는 검토된 소스 수준 판정이다. 이번 실제 서버·휴대폰 전체 흐름은 실행하지 않았으며 기능 TC를 자동 PASS로 올리지 않았다. 과거 contract-audit-review-20261023.json은 수정 전 오판 재현 기록이다.

## 남은 조건

현재 감사의 P0는 **INT-07: Backend 기본 RuleAgent/NoVision**이다. 전체 exit1을 유지한다. 실제 현장 정답·예시 파노라마(DATA-01)도 확인 전이다.
[QA #3](https://github.com/team-onetruck/oneload-qa/issues/3)은 Q10·20문항 근거 열은 완료했지만 검색 오탐([RAG #3](https://github.com/team-onetruck/oneload-rag/issues/3))과 운영 연결 후 검사가 남아 open이다. 0.35를 운영 승인값으로 바꾸지 않았다.

실제 모델·임베딩 호출0회, 현장 사진 정답0건, 컴포넌트21턴 사람 검토 대기·최종 품질 점수null이다. 기존 service v2·component v2·retrieval v1의 질문·정답·분할은 변경하지 않았다. 이전 App/RAG CI는 [별도 역사적 기록](source-review-20261023.json)이며 이번 실제 브라우저 결과로 집계하지 않는다.
