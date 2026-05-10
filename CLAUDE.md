# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Source-of-Truth YAML for the [agent-setup-copilot](https://github.com/WMJOON/agent-setup-copilot) recommendation engine. All knowledge lives here as structured data; all logic lives in the consumer repo. Editing this repo never requires touching consumer code.

## Commands

```bash
# Phase F — Structural verification (harness-owned, runs locally)
python3 skills/ontology-harness/scripts/local_validate.py --instances-dir instances/
python3 skills/ontology-harness/scripts/local_validate.py --instances-dir instances/ --strict

# Phase E — Contract validation (consumer-owned, requires copilot repo cloned side-by-side)
python path/to/agent-setup-copilot/governance/scripts/validate.py \
  --instances-dir instances/ --strict

# Guided entry addition (interactive; runs Phase F automatically before inserting)
python3 skills/ontology-harness/scripts/add_entry.py --type device
python3 skills/ontology-harness/scripts/add_entry.py --type model
python3 skills/ontology-harness/scripts/add_entry.py --type framework
python3 skills/ontology-harness/scripts/add_entry.py --type use_case
python3 skills/ontology-harness/scripts/add_entry.py --type device --dry-run

# Validate only (fetch and run consumer validate.py, no insertion)
python3 skills/ontology-harness/scripts/add_entry.py --validate-only
```

CI runs consumer `validate.py` (fetched from GitHub) on every push/PR touching `ontology.yaml`. The `instances/` directory is validated only by the local harness unless the consumer repo is available.

## Architecture

### Two-layer separation

```
concepts/     ← Schema definitions — what fields mean and how they relate
instances/    ← Actual data — devices, models, frameworks, profiles, relations
```

`concepts/` is read-only reference. All edits happen in `instances/`.

### Key instance files and their dependencies

| File | Role | References |
|------|------|------------|
| `use_case.yaml` | Goals users want to accomplish | — |
| `device.yaml` | Complete machines | `models` (via `max_model`) |
| `model.yaml` | Ollama-pullable LLMs | — |
| `framework.yaml` | Agent/automation/UI/IDE/RAG tools | `use_cases` (via `best_for`) |
| `repo.yaml` | GitHub repos for frameworks | `frameworks` (via `framework_ref`) |
| `setup_profile.yaml` | Concrete hardware+model+framework combos | `devices`, `models`, `frameworks`, `repos`, `use_cases` |
| `relation.yaml` | Upgrade paths, API→local transitions, per-framework fit ratings, per-profile fit ratings | all of the above |

### Three consistency contracts to maintain

When adding or editing a `framework` entry, keep these three in sync:

1. **`framework.yaml` → `best_for`**: list of `use_case.id`s this framework is suited for
2. **`relation.yaml` → `framework_use_case_fits.<id>.strong_fit`**: per-framework fit ratings with reasons
3. **`relation.yaml` → `profile_fit`**: per-profile + per-use_case fit entries for every `setup_profile.yaml` entry that uses this framework

`best_for` and `framework_use_case_fits` must agree. `profile_fit` must cover every `use_case` declared in the profile's `use_cases` list.

### `relation.yaml` structure

The file has several top-level blocks under `instances:`:
- `upgrade_paths` — device upgrade chains (macbook / mac_mini / pc)
- `api_to_local_paths` — cloud API → local model migration paths
- `framework_use_case_fits` — keyed by `framework.id`, contains `strong_fit` / `weak_fit` lists
- `profile_fit` — flat list of `{profile, fit, use_case, reason}` entries
- `use_case_adjacency` — semantic relations between use cases

### ID naming rules

All `id` fields must match `^[a-z][a-z0-9_.:-]*$`. The harness (`local_validate.py`) enforces this and will reject violations at Phase F.

### Schema contract ownership

Field contracts (required fields, enum values, cross-reference types) are owned by the **consumer repo** (`agent-setup-copilot/governance/schema.json`). Do not add fields outside the schema without a separate PR to the consumer repo. The local harness only checks structural minimums (`id`, `label`) and cross-reference existence.
