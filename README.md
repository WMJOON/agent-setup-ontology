# agent-setup-ontology

**Local AI Agent Setup Ontology — Community SOT**

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

The knowledge base for [agent-setup-copilot](https://github.com/WMJOON/agent-setup-copilot).
Defines devices, models, frameworks, API services, components, repos, and setup profiles
as structured YAML — the Source of Truth for local AI agent recommendations.

---

## Files

```
rubrics/                ← Rubric definitions for normalized Fact classes
                           (noise-class, power-efficiency-class, maintenance-burden-class, …)

concepts/               ← Layer-stratified concept definitions
  fact/                 ← Fact layer: measurable / source-backed schemas
    devices/
    models/
    setups/
  semantic/             ← Semantic layer: reusable interpretations derived from Fact
    devices/
    models/
    setups/
  decision/             ← Decision layer: context-conditional patterns (prefer/avoid/trade-off)
    devices/
    models/
    setups/
  use_case.yaml
  cost_estimation.yaml  ← schema/formulas only; data values in instances/cost_estimation.yaml
  usage_input.yaml      ← user input schema; inference_rules live in agent-setup-copilot SKILL.md
  relation.yaml         ← relation categories + type definitions

instances/              ← Instance data (actual devices, models, frameworks, ...)
  fact/                 ← Fact instances: raw_facts + normalized_facts + evidence_refs
  semantic/             ← Semantic instances: derived_from + interprets + meaning
  decision/             ← Decision instances: incorporates + applies_when + outcome
  use_case.yaml
  device.yaml
  model.yaml
  framework.yaml
  api_service.yaml
  component.yaml
  repo.yaml
  setup_profile.yaml
  cost_estimation.yaml  ← token usage profiles, break-even thresholds, electricity estimates
  relation.yaml         ← upgrade_paths, api_to_local_paths, framework_use_cases, ...

rollups/                ← Materialized view cache (convenience layer, not canonical source)
  semantic/             ← frequently-used semantic bundle cache
  decision/             ← frequently-used decision shortlist cache

docs/
  schema.md             ← Full field reference with examples (including layer schemas)
  concepts.md           ← Human-readable concept guide
  cost-guide.md         ← API vs local cost analysis and break-even calculator
  relations.md          ← Relation taxonomy and path diagrams
```

---

## Contributing

Add a device, model, or framework by editing the relevant file in `instances/` — no code knowledge needed.

→ [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Schema contract

Structural rules (required fields, types, enums) are currently owned by the consumer repo:
[agent-setup-copilot/governance/](https://github.com/WMJOON/agent-setup-copilot/tree/main/governance)

PRs to this repo are validated by CI using the consumer's `validate.py`.

**Versioning direction:** As this ontology matures and additional consumers emerge,
the schema contract will be versioned here (`schema_version` in each YAML file)
and the governance rules migrated to a shared contract definition.
This keeps the SOT self-contained and enables independent consumers to pin
to specific schema versions without coupling to a single consumer's validation logic.

---

## Design principles

- **Knowledge ≠ execution** — YAML here, logic in the consumer. Updating a model or device
  requires no code change in any consumer application.
- **Git as audit trail** — every recommendation rule change is a PR with a diff, reviewer,
  and merge history. No wiki drift.
- **Use-case first** — entries are organized around what users want to accomplish, not
  around hardware specs or model names.
- **Derivation over duplication** — relationships that can be computed from existing fields
  are documented as derivation rules in `relations.yaml`, not hard-coded as data.
  Explicit instances are reserved for cases where derivation is insufficient.
- **Fact / Semantic / Decision separation** — layer purity is enforced by linting.
  See [docs/schema.md § Ontology Layer Structure](docs/schema.md#ontology-layer-structure)
  for field definitions, YAML schemas, and validation rules.

---

## License

MIT
