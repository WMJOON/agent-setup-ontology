---
name: ontology-harness
description: >
  Contribution harness for agent-setup-ontology.
  Guides adding devices, models, frameworks, use cases, and other entries to the ontology YAML files.
  Delegates schema validation to the consumer repo (agent-setup-copilot/governance/).
  Triggers: "validate ontology", "add a device", "add a model", "add a framework",
  "add a use case", "pre-PR validation", "cross-reference check",
  "check ontology contract", "ontology contribution", "remove an entry".
---

# ontology-harness

`agent-setup-ontology` contribution harness.
**The schema contract is owned by the consumer repo.** This skill delegates to that contract.

```
Governance owner:
  agent-setup-copilot/governance/
  ├── GOVERNANCE.md     ← Contract document (policy)
  ├── schema.json       ← Formal schema (Source of Truth)
  └── scripts/
      └── validate.py   ← Official validator

This skill's role:
  1. Contributor adds entry to ontology.yaml via add_entry.py
  2. Validation is delegated to consumer validate.py (fetch or local)
  3. CI calls consumer validate.py directly
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
└── add_entry.py     ← Guided contribution (add entry + delegate to consumer validate)
```

> `validate.py` is not in this repo. Validation is delegated to consumer governance.

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

## Workflow B — Validation delegation

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
