# Relations Reference

> Machine-readable source: [`../relations.yaml`](../relations.yaml)
> Version: 0.0.1 — foundational data only

Relations describe **how entities connect to each other** in the ontology.
Most relations are derivable from the data; a few are stored as explicit instances.

---

## Relation Category Taxonomy

```mermaid
flowchart TB
    subgraph CAT["Relation Categories"]
        COMP["compatibility<br/>Can X work with Y?"]
        EQUIV["equivalence<br/>X ≈ Y in capability"]
        TRANS["transition<br/>When/how to move from X to Y"]
        CAP["capability<br/>X can handle Y"]
        REQ["requirement<br/>Y needs X to function"]
        REC["recommendation<br/>X is well-suited for Y"]
    end
```

---

## All Relation Types

```mermaid
flowchart LR
    D["device"]
    M["model"]
    F["framework"]
    UC["use_case"]
    API["api_service"]
    RT["runtime"]
    TIER["device_tier"]

    D   -->|"runs<br/>[compatibility]"| M
    F   -->|"uses<br/>[compatibility]"| RT
    API -->|"equivalent_to<br/>[equivalence]"| M
    API -->|"transitions_to<br/>[transition]"| D
    D   -->|"upgrades_to<br/>[transition]"| D
    M   -->|"enables<br/>[capability]"| UC
    D   -->|"supports<br/>[capability]"| UC
    UC  -->|"requires<br/>[requirement]"| TIER
    F   -->|"suits<br/>[recommendation]"| UC
    M   -->|"sweet_spot_for<br/>[recommendation]"| TIER

    style D   fill:#dbeafe,stroke:#93c5fd
    style M   fill:#dcfce7,stroke:#86efac
    style F   fill:#ede9fe,stroke:#c4b5fd
    style UC  fill:#fef9c3,stroke:#fde047
    style API fill:#ffe4e6,stroke:#fda4af
```

---

## Derivable vs Explicit

| Relation | Derivable? | Source |
|----------|-----------|--------|
| `device_runs_model` | ✅ auto | `device.memory_gb >= model.min_memory_gb` |
| `framework_uses_runtime` | ✅ stored | `framework.runtime_support[]` |
| `api_equivalent_local` | ✅ stored | `api_service.local_alternative` |
| `api_transitions_to_device` | ✅ auto + instances | derivation + `relations.yaml` instances |
| `device_upgrades_to` | 📋 instances | `relations.yaml` upgrade_paths |
| `model_enables_use_case` | ✅ auto | `model.quality` + `model.tool_calling` |
| `device_supports_use_case` | ✅ auto | `device.memory_gb` + `use_case.min_memory_gb` |
| `use_case_requires_tier` | ✅ auto | `use_case.min_memory_gb` mapping |
| `framework_suits_use_case` | ✅ stored | `framework.best_for[]` |
| `model_sweet_spot_for_tier` | ✅ stored | `model.sweet_spot` |

---

## Device Upgrade Paths (explicit instances)

```mermaid
flowchart LR
    subgraph MAC["MacBook"]
        MA8["Air 8GB"] --> MA16["Air/Pro 16GB"] --> MP32["Pro 32GB+"]
    end

    subgraph MINI["Mac Mini"]
        MM16["Mini 16GB"] --> MM32["Mini M4 32GB"] --> MP48["Mini Pro 48GB"]
    end

    subgraph PC["PC"]
        PN["No GPU"] --> R60["RTX 4060<br/>8GB"] --> R90["RTX 4090<br/>24GB"]
    end

    style MA8  fill:#f0f9ff,stroke:#bae6fd
    style MA16 fill:#dbeafe,stroke:#93c5fd
    style MP32 fill:#3b82f6,color:#fff,stroke:#1d4ed8
    style MM16 fill:#f0f9ff,stroke:#bae6fd
    style MM32 fill:#dbeafe,stroke:#93c5fd
    style MP48 fill:#3b82f6,color:#fff,stroke:#1d4ed8
    style PN   fill:#f0f9ff,stroke:#bae6fd
    style R60  fill:#dbeafe,stroke:#93c5fd
    style R90  fill:#3b82f6,color:#fff,stroke:#1d4ed8
```

---

## API → Local Transition Paths (explicit instances)

```mermaid
flowchart LR
    subgraph STD["Standard Quality"]
        A1["gpt-4o-mini<br/>gemini-2-flash<br/>claude-haiku-4-5"]
    end

    subgraph PRO["Pro Quality"]
        A2["gpt-4o<br/>gemini-2-pro<br/>claude-sonnet-4-6"]
    end

    subgraph LOCAL_STD["Local Standard"]
        M1["qwen3.5:9b"]
        D1["Mac Mini 16GB<br/>(min)"]
        D2["Mac Mini M4 32GB<br/>(recommended)"]
    end

    subgraph LOCAL_PRO["Local Pro"]
        M2["qwen3.5:35b-a3b"]
        D3["Mac Mini M4 32GB<br/>(min)"]
        D4["Mac Mini Pro 48GB<br/>(recommended)"]
    end

    STD -->|"local_alternative"| M1
    STD -->|"min device"| D1
    STD -->|"recommended"| D2

    PRO -->|"local_alternative"| M2
    PRO -->|"min device"| D3
    PRO -->|"recommended"| D4

    style STD fill:#fef9c3,stroke:#fde047
    style PRO fill:#ffe4e6,stroke:#fda4af
    style LOCAL_STD fill:#dbeafe,stroke:#93c5fd
    style LOCAL_PRO fill:#dbeafe,stroke:#93c5fd
```

---

## Usage-Based Transition Flow

When the user provides their usage data, the copilot uses relations to reason:

```mermaid
flowchart TD
    U["User provides usage_input<br/>(api_service, tokens/day or monthly cost)"]

    U --> COST["Calculate monthly_api_cost<br/>(cost_estimation formulas)"]

    COST --> EQ["api_equivalent_local relation<br/>→ target local model"]

    EQ --> COMPAT["device_runs_model relation<br/>→ minimum device"]

    COMPAT --> BREAK["Compare costs<br/>monthly_api_cost vs device/24"]

    BREAK --> Q{monthly_api_cost<br/>> device/24?}

    Q -->|"Yes"| PAYBACK["Calculate payback period<br/>device_price / (api_cost - device_cost)"]
    Q -->|"No"| STAY["Stay on API<br/>Revisit when usage grows"]

    PAYBACK --> REC["Recommend transition<br/>via api_to_local_paths instances"]

    style U    fill:#fef9c3,stroke:#fde047
    style REC  fill:#dbeafe,stroke:#93c5fd
    style STAY fill:#dcfce7,stroke:#86efac
```
