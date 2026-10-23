# RAG #3 답글 재검증 — 2026-10-23

[R3 답글](https://github.com/team-onetruck/oneload-rag/issues/3#issuecomment-6356152143)은 수정 후 R6가 새 holdout을 만들고 결과를 확인해 달라는 요청이다. 원래 신고한 호텔 객실 가격·실시간 빈 좌석은 빈 결과로 바뀌었다. **새 질문에서는 오탐 3건과 정상 질문 누락 3건이 남아 RAG #3은 open, 운영 임계값 확정도 보류한다.** RAG 소스·기준값은 수정하지 않았다.

## 평가를 고정한 근거

- [질문·정답·절차](../eval/retrieval_holdout_v2.json)와 [메타데이터](../eval/retrieval_holdout_v2.meta.json)를 검색 결과 관찰 전에 QA [7f41130](https://github.com/team-onetruck/oneload-qa/commit/7f41130e3d3bac6ebb340da31a71b0a3b45f2a4a)으로 커밋했다.
- 데이터 SHA256: `278f16fc787acffe36a4ccbc903d422cbd03d9a1ccf8e4f21c43f6c8e56fc168`.
- R6 합성 국/영 40문항, 양성20·범위밖20, 20질문군이다. 한/영 번역쌍은 서로 연관되어 있어 독립 사용자40명을 뜻하지 않는다. 기존32+R3 44+R3 28문항과 정확히 같은 질문은 없다. 유사 의도와 같은 코퍼스를 사용하며 현장 독립 표본은 아니다.
- 수정 전 RAG `47ab39f1748c92318bfc29e79ba39b5f94b6f159`, 수정 후 당시 main `e6c03f242482151a69d00ce94056c502d724c205`. 두 저장소의 knowledge 해시는 모두 같았다. 후자는 답글의 검색 수정320bf1e를 포함한다.
- 공식 문서13개만 사용. `MemorySearch(min_score=0.25, k=3)`, 상대 컷오프0.5를 고정했다. 새 coverage gate는 수정 후0.25다. 환경의 pgvector·community 설정을 따르지 않는다.
- 버전별 별도 Python 프로세스로 1회씩 측정. 임계값 sweep·holdout 기반 재튜닝·정답 변경을 하지 않았다. 원래 신고2건과 이미 공개된 택시는 별도 진단이다.
- 사전 잠정 QA 기준은 양성 top3≥90%, 범위밖 오탐0이다. 팀 최종 서비스 품질 목표를 대신하지 않는다.

## 결과

[전체 질문별 반환 문서·커밋·해시](../reports/rag-issue3-revalidation.json)

| 평가셋 | 수정 전 top3 / 범위밖 빈 결과 | 수정 후 top3 / 범위밖 빈 결과 |
|---|---|---|
| **새 R6 v2 40문항** | **20/20 · 5/20** | **17/20 · 17/20** |
| R6 개발16 (노출 진단) | 9/10 · 1/6 | 10/10 · 6/6 |
| R6 기존 holdout16 (노출 진단) | 10/10 · 2/6 | 10/10 · 6/6 |
| R3 기존44 (노출 진단) | 38/40 · 3/4 | 38/40 · 4/4 |
| R3 기존 holdout28 (노출 진단) | 16/16 · 5/12 | 16/16 · 11/12 |

새 v2 top1은17/20→14/20이다. top3는 정답 문서 하나라도 포함하면 적중이며 반환 문서 전체의 정밀도·답변 사실성 점수는 아니다. 이전0.35 후보와 직접 비교하지 않고 이번에는 양쪽 모두0.25로 고정했다.

### 남은 범위밖 오탐

| ID | 질문 | 수정 후 반환 문서 |
|---|---|---|
| H2-25 | 서울역에서 인천공항 가는 리무진버스 승차권은 얼마인가요? | doc-seoul-help-desks, doc-fare-arex-express, doc-fare-arex-allstop |
| H2-29 | 인천공항에서 항공사 위탁수하물 추가 요금을 조회해 주세요. | doc-seoul-help-desks, doc-fare-arex-allstop |
| H2-36 | What is the passport replacement fee near Seoul Station? | doc-climate-card-short-term, doc-express-ticket, doc-fare-passes-cards |

이들 문서에는 해당 버스 운임·항공 수하물 요금·여권 수수료 근거가 없다. 답글에서 공개한 택시 기본요금 오탐도 여전히 재현됐다(새 holdout 수치에는 포함하지 않음).

### 새로 누락된 정상 질문

| ID | 질문 | gold |
|---|---|---|
| H2-07 | 서울역 직통열차 표는 매표창구 말고 발매기로도 살 수 있나요? | doc-express-ticket |
| H2-08 | At Seoul Station, can I purchase Express tickets from a machine instead of the counter? | doc-express-ticket |
| H2-20 | Do the AREX Express and all-stop services make the same intermediate stops? | doc-arex-train-types |

수정 전 세 문항 모두 gold를 반환했지만 수정 후에는 모두 빈 결과다. 직통 표 문서의 발매기 위치(20·31행), 열차 종류 문서의 무정차/모든 역 정차 설명(20~21·31~32행)을 근거로 gold를 유지했다. 원인은 새 scope gate와 연관될 수 있으나 추가 조정으로 이 holdout 점수를 높이지 않았다. R3에서 원인 분석과 수정 시 정상 질문 회귀를 함께 확인해야 한다.

## API와 QA 회귀

- 최신 Backend c9b8d8a·Agent54c321f·App2666e44·Data606f648·Infra8587d3b로 [전체 기준선](../reports/baseline.json)을 다시 실행했다. QA38/38, Agent43/43, Backend48/48, 데이터3/3, 컴포넌트20시나리오/21턴, 모의 검색 API20/20이다. 남은 INT-07 때문에 전체 exit1이다.
- Agent 패키지 변경으로 실행기에서 구 경로 `repo/prompts`를 찾던 문제를 수정했다. 실제 모듈의 PROMPT_DIR/MOCK_DIR를 따라 패키지 자산을 검사·해시하고, 다른 checkout·누락·과거 복사본을 검사하는 회귀4건을 추가했다. 질문·정답·component v2 SHA는 유지했다.
- [별도 RAG 주입 API](../reports/rag-integration-probe.json)21/21. RAG e6c03f2, MemorySearch0.25, FakeLLM·합성 JPEG·자신이 만든 폐기 DB다. 요금 근거/URL/확인일 전달·빈 검색 대조군·사진503 등을 검사했다. 검색 오탐 해결이나 실제 모델 품질을 뜻하지 않는다.
- [RAG CI](https://github.com/team-onetruck/oneload-rag/actions/runs/39897084335)는 e6c03f2에서 success이고 계약 시험·MCP HTTP·wheel 지식 포함 단계가 통과했다. R6의 로컬 pgvector/MCP 전체 재실행으로 집계하지 않는다.
- 답글 작성 후5482222에서 pgvector에도 MemorySearch scope gate가 추가된 코드를 확인했다. 이번 검색 품질 평가는 MemorySearch만 대상이며 pgvector/실제 임베딩 품질은 미측정이다.

Backend 기본 경로는 여전히 RuleAgent/NoVision(INT-07)이다. 실제 모델/임베딩 호출0회·현장 사진 정답0건·사람 검토 대기는 유지한다.

## 재현과 다음 판정

[실행기](../scripts/recheck_rag_issue3.py)는 frozen commit과 파일 일치, 중복/노출 질문, 정책, clean checkout, 전후 입력 해시를 확인한다. 같은 부모에 `oneload-rag`를 둔 두 개의 **새 Git clone**을 만들고 위 두 SHA를 각각 detached checkout한다. 기존 작업 checkout을 reset하지 않는다. 아래 root는 각각 그 clone의 부모다.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/recheck_rag_issue3.py --before-root ../rag-issue3-before --after-root ../rag-issue3-after --freeze-repo . --freeze-commit 7f41130e3d3bac6ebb340da31a71b0a3b45f2a4a --output results/issue3-reproduction-001.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_backend_tests.py --project-root .. --with-rag --rag-min-score 0.25 --output results/issue3-rag-api-002
```

첫 명령은 조건 미달로 exit1이 예상되며 환경 오류와 구분한다. 재실행은 이미 공개된 결과의 재현이다. 이제 v2도 노출됐으므로 이후 수정의 회귀용으로만 사용하고, 최종 판정에는 결과를 보지 않은 새 평가셋을 별도로 고정한다. 범위밖 대상/가격·실시간 정보와 정상 안내 문장을 함께 개선하고, R6 잠정 기준 및 운영 기본 경로 연결 후 다시 판정한다. RAG #3·QA #3은 닫지 않는다.
