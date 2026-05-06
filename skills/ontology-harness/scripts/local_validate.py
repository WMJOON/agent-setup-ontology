#!/usr/bin/env python3
"""
ontology-harness: Phase F — Verification (harness self-owned)

이 스크립트는 harness 자신의 구조적 정합성을 검증한다.
consumer 계약 준수(Validation)는 별도 — agent-setup-copilot/governance/validate.py 담당.

4가지 체크만 수행 (tight scope):
  1. ID 중복  — 동일 섹션 내 id 값 중복
  2. 스키마 형태 — 최소 필수 필드 존재 (id, label)
  3. 명명 규칙  — id가 ^[a-z][a-z0-9_.:-]*$ 패턴
  4. 교차 참조 존재성 — 참조된 ID가 해당 파일에 실제로 존재하는지
     (어떤 타입이 어떤 타입을 참조할 수 있는지 = 계약 → Phase E 담당)

사용:
  # per-entity 디렉토리 검증 (기본)
  python3 scripts/local_validate.py --instances-dir instances/

  # 단일 YAML 파일 검증
  python3 scripts/local_validate.py --ontology ontology.yaml

  # 항목 하나만 확인 (add_entry.py 내부 호출용)
  from local_validate import verify_entry
  errors, warnings = verify_entry("device", entry, instances_dir=Path("instances/"))
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# ── 패턴 ──────────────────────────────────────────────────────

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_.:-]*$")

# 최소 필수 필드 (consumer 계약보다 더 느슨한 structural minimum)
STRUCTURAL_MINIMUM = ("id", "label")

# 섹션 이름 → 파일명 매핑 (per-entity 모드)
SECTION_TO_FILE: dict[str, str] = {
    "use_cases":    "use_case.yaml",
    "devices":      "device.yaml",
    "models":       "model.yaml",
    "frameworks":   "framework.yaml",
    "api_services": "api_service.yaml",
    "components":   "component.yaml",
    "repos":        "repo.yaml",
    "setup_profiles": "setup_profile.yaml",
}

FILE_TO_SECTION: dict[str, str] = {v: k for k, v in SECTION_TO_FILE.items()}

# 교차 참조 필드 → 대상 섹션 (존재성 확인용)
CROSS_REF_FIELDS: dict[str, str] = {
    "max_model":               "models",
    "recommended_models":      "models",
    "recommended_frameworks":  "frameworks",
    "local_alternative":       "models",
    "framework_ref":           "frameworks",
    "devices":                 "devices",   # setup_profile
}

# ── 데이터 로딩 ───────────────────────────────────────────────

def _read_yaml(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    return yaml.safe_load(content) or {}


def load_instances_dir(instances_dir: Path) -> dict[str, list[dict]]:
    """instances/ 디렉토리에서 섹션별 엔티티 목록 로드."""
    all_data: dict[str, list[dict]] = {}
    for fname, section in FILE_TO_SECTION.items():
        fpath = instances_dir / fname
        if fpath.exists():
            raw = _read_yaml(fpath)
            items = raw.get(section, [])
            if items:
                all_data[section] = items
    return all_data


def load_single_yaml(ontology_path: Path) -> dict[str, list[dict]]:
    """단일 ontology.yaml에서 섹션별 엔티티 목록 로드."""
    raw = _read_yaml(ontology_path)
    result: dict[str, list[dict]] = {}
    for section in SECTION_TO_FILE:
        items = raw.get(section, [])
        if items:
            result[section] = items
    return result


# ── 4가지 Verification 체크 ───────────────────────────────────

def check_id_duplicate(
    entry_id: str,
    section: str,
    all_data: dict[str, list[dict]],
) -> list[str]:
    """체크 1: 동일 섹션 내 ID 중복."""
    existing = {e.get("id") for e in all_data.get(section, [])}
    if entry_id in existing:
        return [f"[ID_DUPLICATE] '{entry_id}' already exists in '{section}'"]
    return []


def check_schema_shape(
    entry: dict,
    section: str | None = None,
) -> list[str]:
    """체크 2: 최소 필수 필드 존재 (id, label)."""
    errors = []
    for field in STRUCTURAL_MINIMUM:
        if field not in entry or entry[field] is None or entry[field] == "":
            errors.append(
                f"[SCHEMA_SHAPE] Missing required field '{field}'"
                + (f" in section '{section}'" if section else "")
            )
    return errors


def check_naming_convention(entry_id: str) -> list[str]:
    """체크 3: ID 명명 규칙 — ^[a-z][a-z0-9_.:-]*$"""
    if not ID_PATTERN.match(entry_id):
        return [
            f"[NAMING] ID '{entry_id}' violates naming convention. "
            "Use lowercase, digits, underscores, dots, colons, or hyphens. "
            "Must start with a letter."
        ]
    return []


def check_cross_ref_existence(
    entry: dict,
    all_data: dict[str, list[dict]],
    section: str | None = None,
) -> list[str]:
    """체크 4: 교차 참조 존재성 — 참조 ID가 대상 섹션에 실제로 존재하는지.

    Scope: 존재성만 확인 (structural).
    계약(어떤 타입이 어떤 타입을 참조할 수 있는지)은 Phase E 담당.
    """
    warnings = []
    for field, target_section in CROSS_REF_FIELDS.items():
        value = entry.get(field)
        if value is None:
            continue

        target_ids = {e.get("id") for e in all_data.get(target_section, [])}
        if not target_ids:
            # 대상 섹션 데이터 없음 → 검증 불가, skip
            continue

        if isinstance(value, list):
            for ref_id in value:
                if isinstance(ref_id, str) and ref_id not in target_ids:
                    warnings.append(
                        f"[CROSS_REF] field='{field}' references '{ref_id}' "
                        f"but not found in '{target_section}'"
                    )
        elif isinstance(value, str) and value not in ("all", ""):
            if value not in target_ids:
                warnings.append(
                    f"[CROSS_REF] field='{field}' references '{value}' "
                    f"but not found in '{target_section}'"
                )
    return warnings


# ── 통합 Verification ─────────────────────────────────────────

def verify_entry(
    entry_type: str,
    entry: dict,
    all_data: dict[str, list[dict]] | None = None,
    instances_dir: Path | None = None,
) -> tuple[list[str], list[str]]:
    """
    단일 entry에 대한 전체 Verification 실행. add_entry.py 내부 호출용.

    Returns:
        (errors, warnings)
        errors   — 즉시 거부 (insert 전에 해결 필요)
        warnings — 경고 (insert는 가능하나 확인 권장)
    """
    # 섹션 이름 결정
    type_to_section = {
        "device": "devices", "model": "models",
        "framework": "frameworks", "use_case": "use_cases",
        "api_service": "api_services", "component": "components",
        "repo": "repos", "setup_profile": "setup_profiles",
    }
    section = type_to_section.get(entry_type, f"{entry_type}s")

    # 데이터 로드 (제공되지 않은 경우)
    if all_data is None:
        if instances_dir and instances_dir.exists():
            all_data = load_instances_dir(instances_dir)
        else:
            all_data = {}

    entry_id = str(entry.get("id", ""))
    errors: list[str] = []
    warnings: list[str] = []

    # 체크 1: ID 중복
    errors.extend(check_id_duplicate(entry_id, section, all_data))

    # 체크 2: 스키마 형태
    errors.extend(check_schema_shape(entry, section))

    # 체크 3: 명명 규칙
    if entry_id:
        errors.extend(check_naming_convention(entry_id))

    # 체크 4: 교차 참조 존재성
    warnings.extend(check_cross_ref_existence(entry, all_data, section))

    return errors, warnings


def verify_all(
    all_data: dict[str, list[dict]],
) -> tuple[list[str], list[str]]:
    """전체 데이터셋 Verification. --instances-dir / --ontology 모드용."""
    all_errors: list[str] = []
    all_warnings: list[str] = []

    for section, items in all_data.items():
        seen_ids: set[str] = set()
        for entry in items:
            entry_id = str(entry.get("id", ""))
            prefix = f"[{section}:{entry_id}]"

            # 체크 2: 스키마 형태
            errs = check_schema_shape(entry, section)
            all_errors.extend(f"{prefix} {e}" for e in errs)

            # 체크 3: 명명 규칙
            if entry_id:
                errs = check_naming_convention(entry_id)
                all_errors.extend(f"{prefix} {e}" for e in errs)

            # 체크 1: ID 중복 (섹션 내 전체 스캔)
            if entry_id in seen_ids:
                all_errors.append(
                    f"{prefix} [ID_DUPLICATE] '{entry_id}' duplicated in '{section}'"
                )
            else:
                seen_ids.add(entry_id)

            # 체크 4: 교차 참조 존재성
            warns = check_cross_ref_existence(entry, all_data, section)
            all_warnings.extend(f"{prefix} {w}" for w in warns)

    return all_errors, all_warnings


# ── CLI ───────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ontology-harness Phase F — Verification (structural, harness-owned)"
    )
    parser.add_argument("--instances-dir", type=Path,
                        help="Per-entity YAML 디렉토리 (e.g. instances/)")
    parser.add_argument("--ontology", type=Path,
                        help="단일 ontology.yaml 파일")
    parser.add_argument("--strict", action="store_true",
                        help="경고도 오류로 처리 (exit 1)")
    args = parser.parse_args()

    if not args.instances_dir and not args.ontology:
        # 기본: 스크립트 위치 기준 repo root / instances/ 탐색
        # scripts/ → ontology-harness/ → skills/ → repo_root/
        default = Path(__file__).parent.parent.parent.parent / "instances"
        if default.exists():
            args.instances_dir = default
        else:
            parser.print_help()
            sys.exit(1)

    # 데이터 로드
    if args.instances_dir:
        if not args.instances_dir.exists():
            print(f"ERROR: instances-dir not found: {args.instances_dir}", file=sys.stderr)
            sys.exit(1)
        all_data = load_instances_dir(args.instances_dir)
        source = str(args.instances_dir)
    else:
        if not args.ontology.exists():
            print(f"ERROR: ontology file not found: {args.ontology}", file=sys.stderr)
            sys.exit(1)
        all_data = load_single_yaml(args.ontology)
        source = str(args.ontology)

    total = sum(len(v) for v in all_data.values())
    print(f"\n🔍 Verification (Phase F) — {source}")
    print(f"   Sections: {len(all_data)}  |  Entries: {total}\n")

    errors, warnings = verify_all(all_data)

    if warnings:
        print(f"⚠  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"   {w}")

    if errors:
        print(f"\n✗  Errors ({len(errors)}):")
        for e in errors:
            print(f"   {e}")
        print(f"\n❌ Verification FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)

    if args.strict and warnings:
        print(f"\n❌ Verification FAILED (--strict) — {len(warnings)} warning(s) treated as errors")
        sys.exit(1)

    print(f"✅ Verification PASSED — 0 errors, {len(warnings)} warning(s)")
    if not warnings:
        print("   All entries are structurally consistent.")


if __name__ == "__main__":
    main()
