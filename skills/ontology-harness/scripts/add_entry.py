#!/usr/bin/env python3
"""
ontology-harness: 가이드 기여 도구

governance(스키마 계약)는 소비자 레포가 소유한다:
  agent-setup-copilot/governance/

이 스크립트는 항목을 추가하고 최종 검증을 consumer validate.py에 위임한다.

사용:
  python3 scripts/add_entry.py --type device
  python3 scripts/add_entry.py --type model
  python3 scripts/add_entry.py --type framework
  python3 scripts/add_entry.py --type use_case
  python3 scripts/add_entry.py --type device --dry-run
  python3 scripts/add_entry.py --validate-only  # 검증만 (consumer에 위임)
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).parent.parent.parent  # local-agent-ontology/
ONTOLOGY_PATH = ROOT / "ontology.yaml"

# consumer governance 위치
CONSUMER_VALIDATE_URL = (
    "https://raw.githubusercontent.com/WMJOON/"
    "agent-setup-copilot/main/governance/scripts/validate.py"
)
CONSUMER_GOVERNANCE_URL = (
    "https://github.com/WMJOON/agent-setup-copilot/blob/main/governance/GOVERNANCE.md"
)

ID_PATTERN = re.compile(r"^[a-z0-9_.:-]+$")

# ── 계약 (consumer GOVERNANCE.md와 동기화 유지) ──────────────

REQUIRED_FIELDS: dict[str, list[str]] = {
    "device": ["id", "label", "type", "memory_gb", "tier", "max_model"],
    "model":  ["id", "label", "params_b", "type", "min_memory_gb", "quality"],
    "framework": ["id", "label", "complexity", "ollama_support"],
    "use_case":  ["id", "label", "description", "keywords", "min_memory_gb"],
}

FIELD_HINTS: dict[str, list[tuple[str, bool, str]]] = {
    "device": [
        ("id",                   True,  "소문자+언더스코어 (예: mac_mini_m4_32gb)"),
        ("label",                True,  "표시 이름 (예: Mac Mini M4 32GB)"),
        ("type",                 True,  "macbook / mac-mini / mac-studio / pc / other"),
        ("chip",                 False, "칩 이름 (예: M4, M4 Pro)"),
        ("memory_gb",            True,  "통합/시스템 메모리 GB (정수)"),
        ("memory_bandwidth_gbs", False, "메모리 대역폭 GB/s"),
        ("gpu_vram_gb",          True,  "GPU VRAM GB (없으면 0)"),
        ("portability",          False, "portable / stationary"),
        ("always_on",            False, "상시 운영? true / false"),
        ("price_range",          False, "가격 범위 (예: 120만원~)"),
        ("tier",                 True,  "light / standard / standard-plus / pro"),
        ("max_model",            True,  "쾌적하게 돌릴 최대 모델 ID (예: qwen3.5:9b)"),
        ("note",                 False, "한 줄 설명"),
        ("supported_use_cases",  False, "지원 use_case ID 목록 (콤마 구분, 모두면 all)"),
        ("unsupported_use_cases",False, "미지원 use_case ID 목록 (콤마 구분)"),
    ],
    "model": [
        ("id",              True,  "ollama 모델 ID (예: qwen3.5:9b, llama4:17b)"),
        ("label",           True,  "표시 이름"),
        ("params_b",        True,  "전체 파라미터 수 B (숫자)"),
        ("active_params_b", False, "MoE 활성 파라미터 B (MoE일 때만)"),
        ("type",            True,  "dense / MoE"),
        ("min_memory_gb",   True,  "최소 메모리 GB (정수)"),
        ("quality",         True,  "light / standard / standard-plus / pro"),
        ("tool_calling",    False, "tool calling 지원? true / false"),
        ("speed_note",      False, "속도 참고 (예: ~25 t/s on M4 32GB)"),
        ("sweet_spot",      False, "가성비 최적? true / false"),
        ("note",            False, "한 줄 설명"),
    ],
    "framework": [
        ("id",             True,  "소문자 ID (예: smolagents, crewai)"),
        ("label",          True,  "표시 이름"),
        ("complexity",     True,  "low / medium / high"),
        ("multiagent",     False, "멀티에이전트 지원? true / false"),
        ("mcp_support",    False, "MCP 지원? true / false"),
        ("ollama_support", True,  "Ollama 연동 지원? true / false"),
        ("install",        False, "설치 명령어"),
        ("best_for",       False, "적합 use_case ID 목록 (콤마 구분)"),
        ("note",           False, "한 줄 설명"),
    ],
    "use_case": [
        ("id",                     True,  "소문자+언더스코어 (예: voice_assistant)"),
        ("label",                  True,  "표시 이름"),
        ("description",            True,  "한 줄 설명"),
        ("keywords",               True,  "키워드 목록 (콤마 구분)"),
        ("min_memory_gb",          True,  "최소 메모리 GB (정수)"),
        ("needs_always_on",        False, "상시 실행 필요? true / false"),
        ("requires_gpu",           False, "GPU 필수? true / false"),
        ("recommended_models",     False, "추천 모델 ID 목록 (콤마 구분)"),
        ("recommended_frameworks", False, "추천 프레임워크 ID 목록 (콤마 구분)"),
    ],
}

SECTION_MAP = {
    "device": "devices", "model": "models",
    "framework": "frameworks", "use_case": "use_cases",
}


# ── consumer validate 위임 ──────────────────────────────────

def run_consumer_validate(strict: bool = False) -> bool:
    """consumer validate.py를 fetch해서 실행한다."""
    print("\n🔗 consumer governance 검증 위임...")
    print(f"   Source: {CONSUMER_VALIDATE_URL}\n")

    try:
        resp = httpx.get(CONSUMER_VALIDATE_URL, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"⚠ consumer validate.py fetch 실패: {e}")
        print("  인터넷 연결 확인 후 직접 실행:")
        print(f"  python agent-setup-copilot/governance/scripts/validate.py "
              f"--ontology {ONTOLOGY_PATH}")
        return True  # fetch 실패는 블로킹하지 않음

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(resp.text)
        tmp = f.name

    cmd = [sys.executable, tmp, "--ontology", str(ONTOLOGY_PATH)]
    if strict:
        cmd.append("--strict")

    result = subprocess.run(cmd)
    Path(tmp).unlink(missing_ok=True)
    return result.returncode == 0


# ── 헬퍼 ──────────────────────────────────────────────────

def load_ontology() -> dict:
    with open(ONTOLOGY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_ontology(data: dict) -> None:
    with open(ONTOLOGY_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def ask(field: str, required: bool, hint: str) -> str:
    suffix = " [필수]" if required else " [선택, Enter 스킵]"
    while True:
        val = input(f"\n  {field}{suffix}\n  {hint}\n  > ").strip()
        if val or not required:
            return val
        print("  ⚠ 필수 항목입니다.")


def coerce(field: str, raw: str):
    if not raw:
        return None
    bool_f = {"always_on", "tool_calling", "sweet_spot", "multiagent",
               "mcp_support", "ollama_support", "needs_always_on", "requires_gpu"}
    int_f  = {"memory_gb", "gpu_vram_gb", "min_memory_gb"}
    float_f = {"params_b", "active_params_b", "memory_bandwidth_gbs"}
    list_f  = {"keywords", "recommended_models", "recommended_frameworks",
               "best_for", "supported_use_cases", "unsupported_use_cases"}
    if field in bool_f:   return raw.lower() in {"true", "yes", "y", "1"}
    if field in int_f:    return int(raw)
    if field in float_f:  return float(raw)
    if field in list_f:
        return "all" if raw.strip().lower() == "all" \
               else [v.strip() for v in raw.split(",") if v.strip()]
    return raw


def validate_id(entry_id: str, existing: set) -> list[str]:
    errs = []
    if not ID_PATTERN.match(entry_id):
        errs.append(f"ID '{entry_id}' 에 허용되지 않는 문자 (허용: a-z 0-9 _ . : -)")
    if entry_id in existing:
        errs.append(f"ID '{entry_id}' 중복")
    return errs


# ── 메인 ──────────────────────────────────────────────────

def collect_entry(entry_type: str, ontology: dict) -> dict:
    section = SECTION_MAP[entry_type]
    existing = {item["id"] for item in ontology.get(section, []) if "id" in item}

    print(f"\n📝 {entry_type} 항목 추가")
    print(f"   계약 참조: {CONSUMER_GOVERNANCE_URL}\n{'─'*50}")

    entry: dict = {}
    for field, required, hint in FIELD_HINTS[entry_type]:
        raw = ask(field, required, hint)
        val = coerce(field, raw)
        if val is None:
            continue

        if field == "id":
            while True:
                errs = validate_id(str(val), existing)
                if not errs:
                    break
                for e in errs:
                    print(f"  ✗ {e}")
                raw = ask(field, required, hint)
                val = coerce(field, raw)

        entry[field] = val
    return entry


def main():
    parser = argparse.ArgumentParser(description="ontology-harness 가이드 기여 도구")
    parser.add_argument("--type", choices=list(FIELD_HINTS.keys()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-only", action="store_true",
                        help="항목 추가 없이 consumer validate만 실행")
    args = parser.parse_args()

    if args.validate_only:
        ok = run_consumer_validate(strict=True)
        sys.exit(0 if ok else 1)

    ontology = load_ontology()

    # 타입 선택
    entry_type = args.type
    if not entry_type:
        choices = list(FIELD_HINTS.keys())
        print("\n추가할 항목 타입:")
        for i, c in enumerate(choices, 1):
            print(f"  {i}. {c}")
        while True:
            s = input("  번호: ").strip()
            if s.isdigit() and 1 <= int(s) <= len(choices):
                entry_type = choices[int(s) - 1]
                break

    entry = collect_entry(entry_type, ontology)

    # 미리보기
    print("\n── 생성될 YAML ──────────────────────────────────")
    print(yaml.dump([entry], allow_unicode=True, default_flow_style=False), end="")
    print("─────────────────────────────────────────────────")

    if args.dry_run:
        print("ℹ dry-run — ontology.yaml 수정하지 않음")
        return

    confirm = input("\n✅ ontology.yaml에 추가하시겠습니까? [y/N]: ").strip().lower()
    if confirm not in {"y", "yes"}:
        print("취소됨")
        return

    section = SECTION_MAP[entry_type]
    ontology.setdefault(section, []).append(entry)
    save_ontology(ontology)
    print(f"\n✅ {section}에 '{entry.get('id')}' 추가 완료")

    ok = run_consumer_validate(strict=True)
    if not ok:
        print("❌ 검증 실패. ontology.yaml을 확인하거나 consumer governance 참조:")
        print(f"   {CONSUMER_GOVERNANCE_URL}")
        sys.exit(1)
    print("✅ PR 준비 완료.")


if __name__ == "__main__":
    main()
