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
ontology.yaml       ← Instance data (devices, models, frameworks, API services, ...)
concepts.yaml       ← Semantic definitions (what field values mean)
relations.yaml      ← Relation types and curated transition/upgrade paths
docs/
  schema.md         ← Full field reference with examples
  concepts.md       ← Human-readable concept guide
  cost-guide.md     ← API vs local cost analysis and break-even calculator
  relations.md      ← Relation taxonomy and path diagrams
```

---

## Contributing

Add a device, model, or framework by editing `ontology.yaml` — no code knowledge needed.

→ [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Schema contract

Structural rules (required fields, types, enums) are owned by the consumer repo:
[agent-setup-copilot/governance/](https://github.com/WMJOON/agent-setup-copilot/tree/main/governance)

PRs to this repo are validated by CI using the consumer's `validate.py`.

---

## License

MIT
