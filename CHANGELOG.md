# Changelog
All notable changes to this project will be documented in this file.

## [0.0.8] - 2026-04-02
### Added
- `docs/ontology-layer-schemas.md`: 3-layer architecture visualization (Fact/Semantic/Decision) aligned with `advisory-decision-support-policy` Non-Substitution Principle. Includes policy compliance checklist.
- `concepts/user_context.yaml`: USER_CONTEXT entity definition (scale, budget_usd, privacy_requirement, technical_skill, maintenance_tolerance).
- `concepts/component.yaml`: `network_component` and `price_search_query` added to typed component schemas.
- `concepts/framework.yaml`: `runtime_engine` schema added.
- `planning/ontology-refactor/fact-semantic-decision-layering.md`: design rationale for 3-layer refactor.

### Changed
- `concepts/component.yaml` (v0.2.0): decomposed monolithic schema into typed subtypes (`os_platform`, `memory_component`, `gpu_component`). Removed legacy `component` stub. Fixed `accelerator_type` enum: `dedicated_gpu` → `discrete`.
- `concepts/device.yaml` (v0.2.0): replaced inline hardware fields with component reference lists (`memory_components`, `gpu_components`, `os_platform`). Bumped version.
- `concepts/framework.yaml` (v0.2.0): decomposed into typed subtypes (`framework_base`, `agent_orchestrator`, `automation_tool`, `ui_client`, `rag_engine`).
- `concepts/model.yaml`: added Fact Layer fields `min_memory_gb`, `quantization_level`, `context_length_k`.
- `docs/ontology-layer-schemas.md`: fixed `MEMORY_COMPONENT.bandwidth_gbs` type `int` → `float`; added `GPU_COMPONENT.tdp_w`.

### Fixed
- `concepts/usage_input.yaml`: YAML parse error in `examples` sequences — quoted scalar + trailing arrow token pattern rejected by PyYAML.

## [0.0.7] - 2026-04-02
### Added
- `instances/semantic_labels.yaml`: formal semantic label definitions (Always_On_Friendly, Team_Scale_Bottleneck, High_Security_Compliance, Maintenance_Free, Cost_Effective, GPU_Native, Data_Isolation_Compliant) with `use_case_label_requirements` mapping.
- `instances/component.yaml`: added `rtx-3090` (24GB Ampere, 936 GB/s) entry to fix broken reference from `minipc_oculink_rtx3090_24gb`.
- `scripts/migrate_device_components.py`: migration script with dry-run, apply, and --check modes; ruamel.yaml preferred with PyYAML fallback.

### Changed
- `instances/device.yaml` (v0.0.6): completed component-reference migration.
  - Apple Silicon + DGX Spark devices: `memory_gb` → `unified_memory_gb`; removed `gpu_vram_gb`.
  - PC/SFF devices: flat `memory_gb`/`gpu_vram_gb` fields replaced with `ram_component` / `gpu_component` references.

## [0.0.6] - 2026-04-02
### Added
- `docs/schema.md`: new "Ontology Layer Structure" section — per-layer required/optional field tables, YAML examples (Fact/Semantic/Decision), linking mechanics, and validation rules.
- `ontology-harness` SKILL.md: "Ontology Directory Structure (3-layer)" section guiding contributors on which layer to add entries to.

### Changed
- Introduced Fact/Semantic/Decision 3-layer directory structure across `concepts/` and `instances/`.
- Added `rubrics/` directory for normalized Fact class definitions.
- Added `rollups/` as a materialized view cache (semantic and decision shortlist bundles).
- Translated `ontology-harness` SKILL.md to English (description triggers + full body).
- Translated Korean rollups comments in `README.md` to English.

## [0.0.5] - 2026-04-01
### Added
- OCuLink-based Mini PC devices (Minisforum + RTX 3090/4090) to `device.yaml`.
- SFF eGPU setup profile (`setup-minipc-oculink-rtx3090`) for mass research pipelines to `setup_profile.yaml`.

### Changed
- Bumped version to 0.2.0.
- Generalized use-case wording in notes (removed specific "Ontology" mentions where inappropriate) to support broader research domains.
