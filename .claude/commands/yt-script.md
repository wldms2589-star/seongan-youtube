---
description: 시즌 주제로 유튜브 롱폼+숏폼 대본 생성
argument-hint: "S11-1  또는  결산 절세"
---

# 시즌 주제 대본 생성

대상: `$ARGUMENTS`

## 절차

### 0단계 · 항상 먼저 읽기
1. `planning/00_브랜드_규칙집.md` — 톤·화법·구성의 기준
2. `season/topics.json` — 시즌과 주제 데이터 (단일 소스)
3. `season/00_세무캘린더.md` — 발행 시점 판단
4. **대시보드의 지침** — 아래 "지침 반영" 참조

### 1단계 · 주제 확정
- 인자가 주제 ID(`S11-1`)면 그대로
- 인자가 키워드면 `topics.json` 에서 찾는다
- 인자가 없으면 **오늘 날짜 기준으로 발행이 임박한 시즌**의 우선순위 1번 주제

각 주제에는 이미 `message` / `hook` / `angle` / `outline` / `verify` / `shorts` / `next` 가 들어 있다.
**새로 기획하지 말고 이 구조를 대본으로 펼친다.**

### 2단계 · 지침 반영 (필수)
대시보드에 사용자가 적어둔 지침이 있다. 대본을 쓰기 전에 반드시 읽는다.

```
Artifact(action="read_db", url="<대시보드 URL>", db_op="get",
         collection="guide", doc_id="global")
```

편별 지침은 `topics/<주제id 소문자>` 문서의 `guide` 필드에 있다.
**공통 지침 → 편별 지침 순으로 적용하고, 충돌하면 편별 지침이 이긴다.**

### 3단계 · 대본 작성
- 롱폼 7단계 구조 (문제 → 의외성 → 얻을 것 → 자기소개 → 본론 → 판단 → CTA)
- 본문은 **실제로 말할 문장** 그대로. 개요가 아니다
- `[자막]` `[그래픽]` `[00:00]` 표기
- 세법 수치는 `[수치검증]`, 세무사 판단이 필요한 자리는 `[촬영 전 확인]`
- "저라면 ~합니다" 판단 필수
- 숏폼 3편 (`topics.json` 의 `shorts` 를 대본으로 펼친다)

저장: `scripts/season/<주제id>_<주제명>.md`

### 4단계 · 대시보드에 올리기 (필수)
```
Artifact(action="write_db", url="<대시보드 URL>", db_op="set",
         collection="topics", doc_id="<주제id 소문자>",
         file_path="<임시 JSON>")
```
JSON 형태: `{"id":"S11-1","title":"...","script":"<대본 전문>","guide":"<기존 편별 지침 유지>","status":"","statusAt":""}`

`seriesId` / `shootAt` / `uploadAt` 도 대시보드가 관리하는 필드다. **대본을 다시 쓸 때 지우지 않는다.**
시리즈 목록은 db `series` 컬렉션에 있고, `{id, name(관리용), title(화면 제목), desc, order}` 형태다.

`status` 는 대시보드가 관리하는 진행 단계다: `""`(작성됨) / `reviewed`(검토 완료, 촬영 대기) / `shot`(촬영 완료).
**대본을 다시 쓸 때 기존 `status` 를 임의로 지우지 않는다.** 이미 검토가 끝난 대본을 새로 쓰면
검토 상태를 지우고 사용자에게 다시 검토가 필요하다고 알린다.

## 반대 방향 — "보드 내용 반영해줘"
1. `read_db` 로 `guide/global` 과 `topics` 컬렉션을 읽는다
2. 사용자가 대시보드에서 고친 대본을 `scripts/season/` 원본에 반영한다
3. 새로 추가된 지침이 있으면, 기존 대본 중 그 지침에 어긋나는 것을 찾아 알린다

## 주제가 어디에 있나 — 세 곳

| 위치 | 무엇 | 수정 방법 |
|---|---|---|
| `season/topics.json` 의 `seasons` | 시즌 주제 24개 | 파일 수정 후 대시보드 재발행 |
| `season/topics.json` 의 `evergreen` | 상시 주제 15개 | 위와 같음 |
| 대시보드 db `custom` 컬렉션 | **사용자가 직접 추가한 주제** | 대시보드에서 추가·삭제 |

사용자가 대시보드에서 추가한 주제는 `custom` 컬렉션에 있고 `id` 가 `S11-C…` 형태다.
`제목만 있고 각도·본론이 비어 있을 수 있으니` 대본을 쓸 때 직접 설계한다.

```
Artifact(action="read_db", url="<대시보드 URL>", db_op="list", collection="custom")
```

사용자가 추가한 주제를 정식 주제로 승격하려면 `season/topics.json` 에 옮겨 적고
`custom` 에서 지운 뒤 대시보드를 재발행한다.
