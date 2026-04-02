# Changelog
All notable changes to this project will be documented in this file.

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
