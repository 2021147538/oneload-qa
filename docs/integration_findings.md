# 현재 통합 점검 결과

기준: Agent b5c5dde, Backend 2502e65, Frontend d45f466 (2026-10-22).
[계약 검사](../reports/contract-audit.json)와 [실제 API 연결 검사](../reports/integration-probe.json)를 함께 봅니다.

## 이전 규격 차이의 재검증

| ID | 상태 | 확인 내용 |
|---|---|---|
| INT-01 | 해결 확인 | handle_message(ctx, message, image, selected_poi_id)와 AgentResult 반환 구조 일치 |
| INT-02 | 해결 확인 | AgentResponse·Slots·Source·위치 특징 스키마와 상태·의도 enum 일치 |
| INT-03 | 해결 확인 | 일반열차 슬롯은 allstop으로 통일 |
| INT-04 | 해결 확인 | 실제 Backend Slots로 일반열차 → 없어요 대화 및 슬롯 저장 통과 |
| INT-05 | 해결 확인 | 서울역 지도 사본 일치, R2 VisionFeatures를 Backend matcher에 전달해 후보 생성 |

현재 Agent는 이전에 사용하던 pending_intent/pending_topic을 요구하지 않습니다.
옛 계약을 다시 매핑하는 작업보다 현재 공개 계약을 유지하며 연결하는 것이 우선입니다.

## 남은 문제

| ID | 우선순위 | 재현·근거 | 필요한 작업 | 담당 협업 |
|---|---|---|---|---|
| INT-06 | P0 | Frontend README에 Prototype only, store.tsx의 AI_DELAY_MS·SCENARIOS 실행 | 실제 API client와 인증·revision·멱등성·응답→화면 연결 | R4·R5 |
| INT-07 | P0 | Backend app = create_app(), 내부 기본값 RuleAgent/NoVision | R2 패키지와 의존성 연결, 실제 Agent/Vision 주입, R3 검색 교체 | R2·R3·R4 |
| INT-08 | P0 | 실제 /localizations에 R2 LLMVision(FakeLLM(down=True)) 주입 시 HTTP 500 | Backend가 받는 공통 예외로 통일하거나 경계 어댑터에서 명시 변환 | R2·R4 |
| DATA-01 | 출시 전 확인 | 지도 통로·거리·방향과 예시 파노라마, 모의 지식 자료 | 공식 근거·답사·개인정보 검토 후 평가 정답 확정 | R1·R3·R6 |

### INT-08 재현과 원인

1. README의 run_backend_tests.py --with-r2를 새 출력 폴더로 실행합니다.
2. 정상 대화 → 위치 확인 → 경로 → 출발·도착과 LLM 장애 fallback은 통과합니다.
3. INT-08-vision-down에서 기대값은 503 / AI_SERVICE_UNAVAILABLE, 실제는 500 / 표준 오류 본문 없음입니다.

R2 hangil_r2/vision.py는 hangil_r2.backend.contracts.VisionUnavailable을 발생시키고,
Backend app/api/location.py는 app.ai.contracts.VisionUnavailable만 처리합니다.
두 클래스의 이름·정의가 같아도 서로 다른 클래스이므로 except가 받지 못합니다.
스키마 비교와 정상 경로 검사만으로 이 문제를 발견할 수 없습니다.

수정 후 같은 검사의 기대값을 유지해 503과 수동 선택 복구를 확인해야 합니다.
QA 작업에서 팀원의 원본 코드를 변경하거나 오류를 숨기는 변환은 넣지 않았습니다.

## 연결 때 함께 확인할 사항

- R2 인계 문서의 예시는 LLMAgent(..., vision=...) 인수가 빠져 있습니다.
  /localizations용 app.state.vision과 사진 질문용 LLMAgent.vision을 모두 연결해야 합니다.
- /messages의 15초 처리 예산을 실제 모델로 측정합니다. 이해·문장 생성에 사진 읽기가 추가되고,
  호출당 6초 timeout과 재시도가 있어 전체 요청 예산을 별도로 보장해야 합니다.
- R3 검색 계약의 scope·검증일·열차별 문서 필터와 요금 근거 유무를 합의합니다.
- 실제 사진 입력, no_match, 503→수동 선택, revision 충돌은 모바일 화면까지 확인합니다.
- R2 docs/handoff.md의 테스트 수 33건은 현재 실제 실행 37건과 다릅니다. 보고서에는 실행 증거의 수를 사용합니다.
