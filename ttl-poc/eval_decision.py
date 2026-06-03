#!/usr/bin/env python3
"""
POC: Decision layer 평가 — SHACL(required) + trade-off 경고(avoid)

흐름:
  1. _inferred/inferred.jsonl (reason 산출, device→추론 semantic class)
     → device.inferred.ttl (각 device가 추론 type 보유)
  2. decision.shapes.ttl (context별 required SHACL) 로 pyshacl 검증
     → context별 conform device = required 충족 (prefer 후보)
  3. semantic_labels.yaml 의 use_case_label_requirements 에서 avoid label 로드
     → avoid label 보유 device = trade-off 경고 (hard exclusion 아님 — UD-0006)
  4. context별 종합 출력

design-constraints.md(UD-0006) 준수: avoid는 배제가 아니라 trade-off로 surface.
"""
import json
from pathlib import Path
import yaml
from rdflib import Graph
from pyshacl import validate

NS = "https://agent-setup.local/ontology/asetup#"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INFERRED = HERE / "_inferred" / "inferred.jsonl"
SHAPES = HERE / "decision.shapes.ttl"
LABELS = ROOT / "instances" / "semantic_labels.yaml"
DEV_TTL = HERE / "_work" / "device.inferred.ttl"

# POC 대상 context (추론 가능 라벨로만 구성)
POC_CONTEXTS = {"always_on_server", "fine_tuning"}


def local(s):
    return str(s).split("#")[-1].split(".")[-1].split("/")[-1]


def build_inferred_ttl():
    """inferred.jsonl → device.inferred.ttl (device가 all_types를 rdf:type 보유)"""
    lines = [f"@prefix : <{NS}> .",
             "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .", ""]
    dev_types = {}
    for line in INFERRED.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        dev = local(r.get("iri") or r.get("id"))
        types = [local(t) for t in (r.get("all_types") or [])]
        if "Device" not in types:
            types.append("Device")
        dev_types[dev] = types
        type_str = ", ".join(f":{t}" for t in types)
        lines.append(f":{dev} a {type_str} .")
    DEV_TTL.write_text("\n".join(lines) + "\n")
    return dev_types


def shacl_required(dev_types):
    """context shape별 conform(required 충족) device 집합 — violation 파싱"""
    data = Graph().parse(str(DEV_TTL), format="turtle")
    shapes = Graph().parse(str(SHAPES), format="turtle")
    _, report_graph, _ = validate(data, shacl_graph=shapes, inference="none")

    # shape label(context) ↔ 위반 device 수집
    from rdflib import RDF, URIRef
    SH = "http://www.w3.org/ns/shacl#"
    violated = {}  # context_label -> set(device)
    for result in report_graph.subjects(RDF.type, URIRef(SH + "ValidationResult")):
        focus = report_graph.value(result, URIRef(SH + "focusNode"))
        src_shape = report_graph.value(result, URIRef(SH + "sourceShape"))
        # sourceShape는 property shape (blank) → 그 부모 NodeShape의 label 찾기
        ctx = None
        for ns_ in shapes.subjects(URIRef("http://www.w3.org/2000/01/rdf-schema#label"), None):
            for _, _, o in shapes.triples((ns_, URIRef(SH + "property"), None)):
                if o == src_shape:
                    ctx = str(shapes.value(ns_, URIRef("http://www.w3.org/2000/01/rdf-schema#label")))
        if ctx:
            violated.setdefault(ctx, set()).add(local(focus))

    all_devs = set(dev_types)
    # context별 required 충족 = 전체 - 위반
    fit = {}
    # shape label 목록
    for ns_ in shapes.subjects(URIRef(SH + "targetClass"), None):
        lbl = shapes.value(ns_, URIRef("http://www.w3.org/2000/01/rdf-schema#label"))
        if lbl:
            c = str(lbl)
            fit[c] = sorted(all_devs - violated.get(c, set()))
    return fit


def load_avoid():
    data = yaml.safe_load(LABELS.read_text())
    out = {}
    for req in data.get("use_case_label_requirements", []):
        out[req["context"]] = {"required": req.get("required", []), "avoid": req.get("avoid", [])}
    return out


def main():
    dev_types = build_inferred_ttl()
    fit = shacl_required(dev_types)
    reqs = load_avoid()

    print("=" * 64)
    print("Decision Layer POC — SHACL(required) + trade-off(avoid)")
    print("=" * 64)
    for ctx in sorted(POC_CONTEXTS):
        spec = reqs.get(ctx, {})
        prefer = fit.get(ctx, [])
        avoid_labels = set(spec.get("avoid", []))
        print(f"\n● context: {ctx}")
        print(f"   required={spec.get('required')}  avoid={spec.get('avoid')}")
        print(f"   [SHACL conform — required 충족] {len(prefer)}개:")
        for d in prefer:
            warn = avoid_labels & set(dev_types.get(d, []))
            if warn:
                print(f"      ⚠ {d:30} (trade-off: {', '.join(sorted(warn))} 보유)")
            else:
                print(f"      ✓ {d}")
        # required는 충족하나 avoid도 가진 device는 위에 ⚠로 표시됨

    # ── Cross-context trade-off 매트릭스 ──────────────────────────────────
    # avoid 교집합이 ∅이라(required⊥avoid) avoid-경고는 발동하지 않음.
    # 진짜 의사결정 trade-off는 "한 기기를 사면 다른 context를 포기"하는 데 있다.
    print("─" * 64)
    print("Cross-context trade-off (한 기기의 context별 적합성)")
    print("─" * 64)
    ctxs = sorted(POC_CONTEXTS)
    fitset = {c: set(fit.get(c, [])) for c in ctxs}
    header = "device".ljust(30) + "  " + "  ".join(c[:14].center(14) for c in ctxs)
    print(header)
    for d in sorted(dev_types):
        cells = []
        for c in ctxs:
            cells.append("✓".center(14) if d in fitset[c] else "·".center(14))
        # trade-off = 일부 context만 적합
        n_fit = sum(1 for c in ctxs if d in fitset[c])
        mark = " ⇄" if 0 < n_fit < len(ctxs) else ""
        print(d.ljust(30) + "  " + "  ".join(cells) + mark)
    print("\n  ⇄ = 일부 context만 적합 (선택 시 나머지 용도 포기 = trade-off)")
    print()


if __name__ == "__main__":
    main()
