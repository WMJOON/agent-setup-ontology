---
name: ontology-harness
description: >
  local-agent-ontology의 기여 하네스.
  governance(스키마 계약)는 소비자 레포(agent-setup-copilot/governance/)가 소유한다.
  이 스킬은 그 계약을 참조해 기여를 안내하고, 검증을 위임한다.
  트리거 예시: "온톨로지 검증해줘", "새 디바이스 추가해줘", "모델 추가",
  "프레임워크 추가", "PR 전 검증", "교차 참조 확인".
---

# ontology-harness

`local-agent-ontology` 기여 하네스.
**스키마 계약의 소유자는 소비자 레포**다. 이 스킬은 그 계약에 위임(delegate)한다.

```
governance 소유자:
  agent-setup-copilot/governance/
  ├── GOVERNANCE.md     ← 계약 문서 (정책)
  ├── schema.json       ← 정형 스키마 (Source of Truth)
  └── scripts/
      └── validate.py   ← 정식 검증기

이 스킬의 역할:
  1. 기여자가 add_entry.py로 ontology.yaml에 항목 추가
  2. 검증은 consumer validate.py에 위임 (fetch or local)
  3. CI는 consumer validate.py를 직접 호출
```

---

## 계약 참조

스키마 계약 전문:
```
https://github.com/WMJOON/agent-setup-copilot/blob/main/governance/GOVERNANCE.md
```

계약 변경이 필요하면 `agent-setup-copilot` 레포에 PR을 올린다.
이 레포에서 계약을 직접 수정하지 않는다.

---

## 스크립트

```
scripts/
└── add_entry.py     ← 가이드 기여 (항목 추가 + consumer validate 위임)
```

> `validate.py`는 이 레포에 없다. 검증은 consumer governance에 위임.

---

## 워크플로우 A — 가이드 기여 (add)

```bash
pip install pyyaml httpx

# 타입 명시
python3 scripts/add_entry.py --type device
python3 scripts/add_entry.py --type model
python3 scripts/add_entry.py --type framework
python3 scripts/add_entry.py --type use_case

# dry-run (ontology.yaml 수정 없이 미리보기)
python3 scripts/add_entry.py --type device --dry-run
```

추가 흐름:
```
1. 타입 확인
2. 필수 필드 수집 (consumer GOVERNANCE.md 계약 기준)
3. ID 중복 / 명명 규칙 즉시 체크
4. YAML 블록 미리보기
5. 확인 → ontology.yaml 삽입
6. consumer validate.py로 최종 검증
```

---

## 워크플로우 B — 검증 위임 (validate)

consumer validate.py를 직접 실행한다.

```bash
# consumer 레포가 로컬에 있을 때
python path/to/agent-setup-copilot/governance/scripts/validate.py \
  --ontology ontology.yaml --strict

# consumer validate.py를 임시 fetch해서 실행
python3 scripts/add_entry.py --validate-only
```

---

## CI 통합

`.github/workflows/validate.yml` 참조.
consumer validate.py를 GitHub Actions에서 직접 호출한다.

---

## Claude 사용 가이드

```
"RTX 5090 PC 디바이스 추가해줘"
→ add_entry.py --type device --dry-run 실행 후 확인 요청

"qwen3.5:9b 지워도 돼?"
→ consumer validate.py --find-refs qwen3.5:9b 실행 → 영향 범위 보고

"계약 규칙이 뭐야?"
→ agent-setup-copilot/governance/GOVERNANCE.md 참조 안내
```
