---
name: ontology-harness
description: >
  Contribution harness for agent-setup-ontology.
  Guides adding devices, models, frameworks, use cases, and other entries to the ontology YAML files.
  Runs local Verification (Phase F) before delegating Validation to the consumer repo (agent-setup-copilot/governance/).
  Triggers: "validate ontology", "add a device", "add a model", "add a framework",
  "add a use case", "pre-PR validation", "cross-reference check",
  "check ontology contract", "ontology contribution", "remove an entry".
---

# ontology-harness

`agent-setup-ontology` contribution harness.
**The schema contract is owned by the consumer repo**, but this harness self-owns structural Verification.

```
Verification (Phase F — harness owned):
  scripts/local_validate.py
  ├── ID 중복 체크
  ├── 스키마 형태 체크 (최소 필드)
  ├── 명명 규칙 체크 (snake_case)
  └── 교차 참조 존재성 체크

Validation (Phase E — consumer owned):
  agent-setup-copilot/governance/
  ├── GOVERNANCE.md     ← Contract document (policy)
  ├── schema.json       ← Formal schema (Source of Truth)
  └── scripts/
      └── validate.py   ← Official validator

기여 플로우:
  1. add_entry.py — 항목 수집
  2. local_validate.py — Verification (harness self-check)
  3. ontology에 삽입
  4. consumer validate.py — Validation (계약 준수)
  5. CI에서도 동일 순서
```

---

## Ontology Directory Structure (3-layer)

```
concepts/               ← Layer-stratified concept definitions (schemas)
  fact/                 ← Measurable / source-backed field definitions
  semantic/             ← Reusable interpretations derived from Fact
  decision/             ← Context-conditional patterns (prefer/avoid/trade-off)
  use_case.yaml
  cost_estimation.yaml
  usage_input.yaml
  relation.yaml

instances/              ← Instance data (actual devices, models, frameworks, …)
  fact/                 ← raw_facts + normalized_facts + evidence_refs
  semantic/             ← derived_from + interprets + meaning
  decision/             ← incorporates + applies_when + outcome
  device.yaml / model.yaml / framework.yaml / …

rubrics/                ← Rubric definitions for normalized Fact classes
rollups/                ← Materialized view cache (convenience layer, not canonical source)
```

When adding a new entry:
- **Fact layer**: measurable spec or source-backed attribute → `instances/fact/`
- **Semantic layer**: reusable interpretation derived from facts → `instances/semantic/`
- **Decision layer**: context-conditional rule (prefer/avoid/trade-off) → `instances/decision/`
- **Top-level instance** (device/model/etc.): `instances/<type>.yaml`

---

## Contract reference

Full schema contract:
```
https://github.com/WMJOON/agent-setup-copilot/blob/main/governance/GOVERNANCE.md
```

To change the contract, open a PR on `agent-setup-copilot`.
Do not modify the contract directly in this repo.

---

## Scripts

```
scripts/
├── add_entry.py       ← Guided contribution (Guide: feedforward)
│                        Phase F Verification → insert → Phase E Validation
└── local_validate.py  ← Verification (Sensor: feedback, harness-owned)
                         4 checks: ID dup, schema shape, naming, cross-ref existence
```

---

## Workflow A — Guided contribution (add)

```bash
pip install pyyaml httpx

# Specify entry type
python3 scripts/add_entry.py --type device
python3 scripts/add_entry.py --type model
python3 scripts/add_entry.py --type framework
python3 scripts/add_entry.py --type use_case

# Dry-run (preview without modifying ontology.yaml)
python3 scripts/add_entry.py --type device --dry-run
```

Addition flow:
```
1. Confirm type
2. Collect required fields (per consumer GOVERNANCE.md contract)
3. Instant check: ID duplicates + naming conventions
4. YAML block preview
5. Confirm → insert into ontology.yaml
6. Final validation via consumer validate.py
```

---

## Workflow B — Local Verification only (Phase F)

```bash
# instances/ 디렉토리 전체 검증
python3 scripts/local_validate.py --instances-dir instances/

# 단일 파일 검증
python3 scripts/local_validate.py --ontology ontology.yaml

# strict 모드 (warning도 오류 처리)
python3 scripts/local_validate.py --instances-dir instances/ --strict
```

## Workflow C — Validation delegation (Phase E)

Run consumer validate.py directly.

```bash
# When consumer repo is available locally
python path/to/agent-setup-copilot/governance/scripts/validate.py \
  --ontology ontology.yaml --strict

# Fetch and run consumer validate.py temporarily
python3 scripts/add_entry.py --validate-only
```

---

## CI integration

See `.github/workflows/validate.yml`.
GitHub Actions calls consumer validate.py directly.

---

## Usage examples

```
"Add RTX 5090 PC as a device"
→ Run add_entry.py --type device --dry-run, then request confirmation

"Can I remove qwen3.5:9b?"
→ Run consumer validate.py --find-refs qwen3.5:9b → report impact scope

"What are the contract rules?"
→ Refer to agent-setup-copilot/governance/GOVERNANCE.md
```
