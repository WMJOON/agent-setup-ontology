#!/usr/bin/env python3
"""
migrate_device_components.py
============================
Migrates instances/device.yaml from flat-field format to component-reference format.

What it does:
  1. For each device, resolves memory_gb + gpu_vram_gb into component IDs from component.yaml.
  2. Adds memory_components / gpu_components reference fields to each device.
  3. Removes flat fields: memory_gb, gpu_vram_gb, chip (where superseded by component refs).
  4. Writes updated device.yaml in-place (original preserved as device.yaml.bak).

Apple Silicon note:
  Apple unified memory is NOT discrete GPU VRAM — it is both CPU and GPU memory.
  These devices keep memory_gb as the unified_memory_gb field (renamed, not removed).
  No gpu_component is added for Apple devices.

Usage:
  python3 scripts/migrate_device_components.py --dry-run   # preview, no changes
  python3 scripts/migrate_device_components.py             # apply migration
  python3 scripts/migrate_device_components.py --check     # validate refs after migration
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    from ruamel.yaml import YAML  # preserves comments + order
    _yaml = YAML()
    _yaml.preserve_quotes = True
    _yaml.default_flow_style = False
    _yaml.indent(mapping=2, sequence=4, offset=2)
    _USE_RUAMEL = True
except ImportError:
    import yaml as _pyyaml
    _USE_RUAMEL = False
    print("Warning: ruamel.yaml not found. Install it for comment/order preservation:")
    print("  pip install ruamel.yaml")
    print("Falling back to PyYAML (comments and field order may be lost).\n")


REPO_ROOT = Path(__file__).parent.parent
DEVICE_FILE  = REPO_ROOT / "instances" / "device.yaml"
COMPONENT_FILE = REPO_ROOT / "instances" / "component.yaml"

# Unified memory architectures: effective VRAM == system RAM (Apple Silicon + GB10)
UNIFIED_MEMORY_TYPES = {"macbook", "mac-mini", "mac-studio", "ai-supercomputer"}


# ── YAML I/O ──────────────────────────────────────────────────────────────────

def _load(path: Path) -> dict:
    if _USE_RUAMEL:
        return _yaml.load(path)
    with open(path, encoding="utf-8") as f:
        return _pyyaml.safe_load(f)


def _dump(data: dict, path: Path) -> None:
    if _USE_RUAMEL:
        with open(path, "w", encoding="utf-8") as f:
            _yaml.dump(data, f)
    else:
        with open(path, "w", encoding="utf-8") as f:
            _pyyaml.dump(data, f, allow_unicode=True, default_flow_style=False,
                         sort_keys=False)


# ── Component lookup helpers ──────────────────────────────────────────────────

def _build_component_index(components: list[dict]) -> dict[str, dict]:
    """Returns {id: component_dict}."""
    return {c["id"]: c for c in components if "id" in c}


def _find_ram_component(memory_gb: int, comp_index: dict[str, dict]) -> str | None:
    """Find best matching RAM component ID for a given capacity."""
    candidates = [
        c for c in comp_index.values()
        if c.get("component_type") == "memory"
        and c.get("capacity_gb") == memory_gb
    ]
    return candidates[0]["id"] if candidates else None


def _find_gpu_component_by_vram(vram_gb: int, comp_index: dict[str, dict]) -> list[str]:
    """Find GPU component IDs matching a given VRAM size."""
    return [
        c["id"] for c in comp_index.values()
        if c.get("component_type") == "gpu"
        and c.get("vram_gb") == vram_gb
    ]


# ── Migration logic ───────────────────────────────────────────────────────────

def migrate_device(device: dict, comp_index: dict[str, dict], dry_run: bool) -> dict:
    """
    Mutates (or previews mutation of) a single device entry.
    Returns a dict of {field: (old_value, new_value)} for reporting.
    """
    changes: dict[str, tuple] = {}
    dev_type = device.get("type", "")
    is_unified = dev_type in UNIFIED_MEMORY_TYPES

    # ── Unified memory devices (Apple Silicon + DGX Spark GB10) ─────────────
    if is_unified:
        # Rename memory_gb → unified_memory_gb (do NOT remove — it's functionally VRAM)
        if "memory_gb" in device and "unified_memory_gb" not in device:
            changes["unified_memory_gb"] = (None, device["memory_gb"])
            changes["memory_gb"] = (device["memory_gb"], "__remove__")
        # gpu_vram_gb is always 0 for Apple — remove it
        if "gpu_vram_gb" in device:
            changes["gpu_vram_gb"] = (device["gpu_vram_gb"], "__remove__")
        # chip → keep as-is (useful for display)

    # ── PC / SFF devices ─────────────────────────────────────────────────────
    else:
        memory_gb  = device.get("memory_gb", 0)
        gpu_vram_gb = device.get("gpu_vram_gb", 0)

        # RAM component (if not already set)
        if "ram_component" not in device and memory_gb > 0:
            ram_id = _find_ram_component(memory_gb, comp_index)
            if ram_id:
                changes["ram_component"] = (None, ram_id)
            else:
                print(f"  [WARN] No RAM component found for {memory_gb}GB "
                      f"(device: {device.get('id')})")

        # GPU component (if not already set)
        if "gpu_component" not in device and gpu_vram_gb > 0:
            gpu_ids = _find_gpu_component_by_vram(gpu_vram_gb, comp_index)
            if len(gpu_ids) == 1:
                changes["gpu_component"] = (None, gpu_ids[0])
            elif len(gpu_ids) > 1:
                print(f"  [WARN] Multiple GPU components with {gpu_vram_gb}GB VRAM for "
                      f"device {device.get('id')}: {gpu_ids} — skipping auto-assign")
            else:
                print(f"  [WARN] No GPU component found for {gpu_vram_gb}GB VRAM "
                      f"(device: {device.get('id')})")

        # Remove flat fields that are now represented by component refs
        if "ram_component" in device or "ram_component" in {k for k, (_, v) in changes.items() if v != "__remove__"}:
            if "memory_gb" in device:
                changes["memory_gb"] = (device["memory_gb"], "__remove__")
        if "gpu_component" in device or "gpu_component" in {k for k, (_, v) in changes.items() if v != "__remove__"}:
            if "gpu_vram_gb" in device:
                changes["gpu_vram_gb"] = (device["gpu_vram_gb"], "__remove__")

    if not dry_run:
        for field_name, (old_val, new_val) in changes.items():
            if new_val == "__remove__":
                device.pop(field_name, None)
            else:
                device[field_name] = new_val

    return changes


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate device.yaml to component-reference format.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    parser.add_argument("--check", action="store_true",
                        help="Validate component refs in current device.yaml (post-migration).")
    args = parser.parse_args()

    comp_data = _load(COMPONENT_FILE)
    components = comp_data.get("components", [])
    comp_index = _build_component_index(components)

    device_data = _load(DEVICE_FILE)
    devices = device_data.get("devices", [])

    if args.check:
        _validate_refs(devices, comp_index)
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Migrating {len(devices)} devices...\n")

    total_changes = 0
    for dev in devices:
        dev_id = dev.get("id", "?")
        changes = migrate_device(dev, comp_index, dry_run=args.dry_run)
        if changes:
            total_changes += len(changes)
            print(f"  {dev_id}:")
            for field_name, (old, new) in changes.items():
                if new == "__remove__":
                    print(f"    - remove {field_name} (was: {old})")
                elif old is None:
                    print(f"    + add    {field_name} = {new}")
                else:
                    print(f"    ~ change {field_name}: {old} → {new}")

    print(f"\nTotal field changes: {total_changes}")

    if args.dry_run:
        print("\n[DRY RUN] No files written. Run without --dry-run to apply.")
        return

    # Backup + write
    bak = DEVICE_FILE.with_suffix(".yaml.bak")
    shutil.copy2(DEVICE_FILE, bak)
    print(f"\nBackup written to: {bak}")

    device_data["version"] = "0.0.6"
    _dump(device_data, DEVICE_FILE)
    print(f"Updated: {DEVICE_FILE}")

    # Post-migration validation
    _validate_refs(_load(DEVICE_FILE).get("devices", []), comp_index)


def _validate_refs(devices: list[dict], comp_index: dict[str, dict]) -> None:
    print("\nValidating component references...")
    errors = 0
    for dev in devices:
        dev_id = dev.get("id", "?")
        for ref_field in ("gpu_component", "ram_component"):
            ref_id = dev.get(ref_field)
            if ref_id and ref_id not in comp_index:
                print(f"  [ERROR] {dev_id}.{ref_field} = '{ref_id}' not found in component.yaml")
                errors += 1
    if errors == 0:
        print("  All component references are valid.")
    else:
        print(f"  {errors} broken reference(s) found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
