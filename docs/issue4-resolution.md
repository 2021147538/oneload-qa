# QA #4: INT-06 오판 수정

[QA #4](https://github.com/team-onetruck/oneload-qa/issues/4)는 mock 분기에 남은 `AI_DELAY_MS`·`SCENARIOS` 문자열로 실제 HTTP 화면 연결을 미연결 P0로 판정하던 문제다. 이 조건을 제거하고 검토한 호출 경로의 판정을 해당 런타임 소스에만 적용하도록 바꿨다.

## 판정 방식

[frontend_wiring.json](../eval/frontend_wiring.json)에 App의 실제 호출 경로·검토 커밋·런타임 파일/의존성 SHA256을 기록한다. [감사 모듈](../scripts/frontend_wiring.py)은 실제 파일 목록과 해시를 대조한다. 주석에 API 이름이 있거나 호출되지 않는 helper가 있다는 이유로 연결 판정을 내리지 않는다.

| 결과 | 의미 | 감사 처리 |
|---|---|---|
| wired | 검토한 HTTP 연결 소스와 일치 | 소스 검사 통과, 실제 브라우저 NOT_RUN |
| incomplete | 검토한 미연결 소스와 일치 | INT-06 P0·exit1 |
| review_required | 검토하지 않은 소스/의존성, 파일 추가·누락 | 재검토 필요·exit1, 연결/미연결 단정 없음 |

이 방식은 TypeScript 제어흐름을 자동 증명하는 분석기가 아니다. 소스 검토 결과가 다른 코드에 잘못 적용되는 일을 막는 보수적인 감사다. 파일 해시는 같은 저장소에서 재현하며 코드·의존성 변경은 새 검토가 필요하다. README·테스트만 바뀌면 런타임 검토를 무효화하지 않는다.

검토 프로필:

- App bc2d9f1: 기존 화면이 로컬 실행 → incomplete.
- App b111af6: HTTP 채팅은 연결, 사진·경로·이벤트 미연결 → incomplete.
- App b5d6835: 채팅·사진·사용자 확정·서버 경로·안내 이벤트 연결 → wired. mock 데모는 별도 분기에 유지돼 있다.

## 검증

[Git 스냅샷 검증](../reports/frontend-wiring-review.json) · [계약 감사](../reports/contract-audit.json) · [전체 QA](../reports/baseline.json)

세 커밋의 실제 Git 파일을 별도 임시 폴더에 재구성해 두 과거 버전은 미연결, 최신은 연결로 판정했다. 실제 App 체크아웃도 같은 연결 판정을 받았다.

새 회귀11개로 다음을 확인했다: mock 분기가 남은 연결, 과거 미연결, 주석·미사용 helper의 우회 방지, store가 같아도 API/의존성 변경 감지, 파일 누락/추가, 문서·테스트만 변경, 빈 경로, 잘못된 검토 기록 거부, 기록 해시 변경 추적.

전체 QA28/28, Agent43/43, Backend48/48, 컴포넌트20시나리오/21턴, 모의 API20/20이 통과했다. 별도 메모리 RAG API21/21도 통과했다. INT-06 거짓 P0는 제거됐고 남은 P0는 Backend 기본 RuleAgent/NoVision(INT-07)이다. DATA-01 현장 정답 확인도 남는다.

공개 기준선에는 Frontend 소스 판정·registry 해시를 기록하고, 실행 중 검토 파일이 바뀌면 보고서를 갱신하지 않는다. 실제 모델·임베딩 호출0회, 실서버 브라우저·휴대폰 기능 인수는 NOT_RUN이다. 기능 TC를 자동 PASS로 올리지 않았다.

## 다음 App 변경 때

1. main과 실제 변경 내용을 확인한다. HTTP 모드의 화면 진입점부터 API 어댑터까지 호출을 추적하고 mock 분기와 구분한다.
2. `snapshot(app_repo)`로 대상 파일 해시를 얻는다. 파일명·해시만으로 새 코드의 연결을 승인하지 않는다.
3. 검토 커밋·호출 경로 근거·connected_features/missing_features와 해시를 registry의 새 profile로 추가한다. 기존 기록은 회귀 근거로 보존한다.
4. QA 회귀·감사·전체 검사를 실행하고 인수인계·보고서를 함께 갱신한다. 브라우저·실제 Backend 검증은 별도 증거로 기록한다.

QA #4의 감사 결함은 이 변경으로 해결한다. QA #3의 검색 임계값·운영 연결 조건은 다른 문제이며 계속 열린 상태로 추적한다.
