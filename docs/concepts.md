# Concept Guide

> This document explains **what ontology values mean** — the semantic layer
> on top of the structural schema.
>
> Machine-readable version: [`../concepts.yaml`](../concepts.yaml)
> Structural contract: [`agent-setup-copilot/governance/GOVERNANCE.md`](https://github.com/WMJOON/agent-setup-copilot/blob/main/governance/GOVERNANCE.md)

---

## Why concepts matter

The schema tells you `tier` must be one of `light | standard | standard-plus | pro`.
The concept tells you **what that actually means in practice**:

> `standard-plus` = 32 GB memory with a base chip.
> Runs MoE models like qwen3.5:35b-a3b at 18-25 t/s.
> Covers all single-agent use cases. Best price-to-capability sweet spot in 2026.

Without concepts, contributors could add `tier: pro` to an 8 GB device, or
`quality: standard` to a 32B model, and the schema validator would not catch it.
Concepts are the guide that makes contributions consistent.

---

## Device Concepts

### `tier` — Practical Capability Bracket

Tier answers: **"What class of agent workloads can this device handle reliably?"**

```mermaid
flowchart LR
    L["<b>light</b><br/>≤8 GB<br/>4B models<br/>Simple Q&A"]
    S["<b>standard</b><br/>16 GB<br/>9B models<br/>Daily agent"]
    SP["<b>standard-plus</b><br/>32 GB base chip<br/>35B MoE<br/>Full single-agent"]
    P["<b>pro</b><br/>32 GB+ hi-BW<br/>or 24 GB+ GPU<br/>Multi-agent / Judge"]

    L --> S --> SP --> P

    style L fill:#f0f9ff,stroke:#bae6fd
    style S fill:#dbeafe,stroke:#93c5fd
    style SP fill:#bfdbfe,stroke:#60a5fa
    style P fill:#3b82f6,color:#fff,stroke:#1d4ed8
```

| Tier | Memory | Bandwidth | Max practical model | Use case coverage |
|------|--------|-----------|--------------------|--------------------|
| `light` | ≤8 GB | any | 4B class | Autocomplete, simple tasks |
| `standard` | 16 GB | any | 9B class | Most single-agent tasks |
| `standard-plus` | 32 GB | ≤150 GB/s | MoE 35B class | Full single-agent |
| `pro` | 32 GB+ | ≥273 GB/s, or GPU | 27B+ dense | Multi-agent, Judge, fine-tune |

### `type` — Form Factor

| Type | Key characteristic |
|------|--------------------|
| `macbook` | Portable. Fan-throttling risk on sustained inference. |
| `mac-mini` | Stationary, quiet. Ideal always-on server. |
| `mac-studio` | Highest bandwidth Apple Silicon. |
| `pc` | Discrete GPU available. Best for fine-tuning (CUDA). |

### `max_model`

The Ollama model that runs at **interactive speeds** (≥10 t/s) on this device
using Q4_K_M quantization. Not the absolute maximum — the practical ceiling.

---

## Model Concepts

### `quality` — Output Capability Bracket

Quality is calibrated to **agent use cases**, not just benchmark scores.
A model that scores well on MMLU but fails at structured tool calls is not `standard`.

```mermaid
flowchart LR
    L["<b>light</b><br/>1–4B<br/>Fast<br/>Simple Q&A"]
    S["<b>standard</b><br/>7–9B<br/>Sweet spot<br/>Most agent tasks"]
    SP["<b>standard-plus</b><br/>~14B<br/>Better reasoning<br/>Code review"]
    P["<b>pro</b><br/>27B+<br/>Judge-grade<br/>Complex agents"]

    L --> S --> SP --> P

    style L fill:#f0fdf4,stroke:#bbf7d0
    style S fill:#dcfce7,stroke:#86efac
    style SP fill:#86efac,stroke:#4ade80
    style P fill:#16a34a,color:#fff,stroke:#15803d
```

| Quality | Parameter range | Characteristic |
|---------|----------------|---------------|
| `light` | 1–4B | Fast. Limited multi-step reasoning. |
| `standard` | 7–9B | Reliable tool calling. Most agent tasks. |
| `standard-plus` | ~14B | Noticeably better code and reasoning. |
| `pro` | 27B+ or MoE equiv. | LLM-as-Judge quality. Complex agents. |

### `type` — Architecture

| Type | Memory usage | Speed characteristic |
|------|-------------|---------------------|
| `dense` | Proportional to params | Limited by memory bandwidth |
| `MoE` | Full model in RAM, only fraction active | Runs at active-param speed, not total-param speed |

**MoE example**: `qwen3.5:35b-a3b` has 35B total params but activates only 3B per token.
It fits in 32 GB (like a 35B model) but runs at ~20 t/s (like a 9B model).

### `tool_calling`

**Required `true` for agent use.** Frameworks like smolagents, crewai, and openclaw
depend on structured function calls. A model with `tool_calling: false` should
only be recommended for `ui` or `ide` kind frameworks.

### `sweet_spot`

Marks the best quality-to-resource ratio in a tier.
When multiple models fit a device, the copilot recommends `sweet_spot: true` first.

---

## Framework Concepts

### `kind` — Framework Role

```mermaid
flowchart TB
    subgraph AGENT["agent — Build it"]
        A1["smolagents"]
        A2["crewai"]
        A3["langgraph"]
        A4["qwen-agent"]
    end

    subgraph AUTO["automation — Point it"]
        B1["openclaw"]
    end

    subgraph UI["ui — Just chat"]
        C1["open-webui"]
        C2["anythingllm"]
    end

    subgraph IDE["ide — Type less"]
        D1["continue"]
    end

    subgraph RAG["rag — Search docs"]
        E1["llamaindex"]
    end

    style AGENT fill:#dbeafe,stroke:#93c5fd
    style AUTO  fill:#fef9c3,stroke:#fde047
    style UI    fill:#dcfce7,stroke:#86efac
    style IDE   fill:#ede9fe,stroke:#c4b5fd
    style RAG   fill:#ffe4e6,stroke:#fda4af
```

| Kind | You write code? | Primary output | When to recommend |
|------|----------------|---------------|------------------|
| `agent` | Yes | Custom agent behavior | User wants to build something |
| `automation` | Minimal | Automated tasks | User wants "do this for me" |
| `ui` | No | Chat interface | User wants a local ChatGPT |
| `ide` | No (plugin) | Code completions | User wants Copilot replacement |
| `rag` | Yes | Document Q&A | User has many documents to search |

### `local_capable`

**The most important field for privacy-conscious users.**

`true` → works entirely on-device with Ollama. No data leaves the machine.
`false` → requires a cloud API key, even if using a local model for inference.

### `runtime_support`

Which LLM backends the framework connects to. Used to filter frameworks
that are compatible with the user's setup (Ollama only vs API available).

| Value | Setup required |
|-------|---------------|
| `ollama` | `ollama serve` running locally |
| `openai` | `OPENAI_API_KEY` env var |
| `anthropic` | `ANTHROPIC_API_KEY` env var |
| `huggingface` | `HF_TOKEN` or local Transformers install |
| `litellm` | `pip install litellm` + any provider key |
| `any` | Any OpenAI-compatible URL (includes Ollama's `/v1` endpoint) |

### `complexity`

| Level | Lines to first working agent | Who it's for |
|-------|------------------------------|-------------|
| `low` | <10 | Anyone. Copy-paste and run. |
| `medium` | ~30–50 | Developers comfortable with config files. |
| `high` | 50+ | Developers familiar with graphs or state machines. |

---

## Use Case Concepts

### Use case taxonomy

```mermaid
flowchart TB
    subgraph AUTO["automation"]
        wa["web_automation"]
        fa["file_automation"]
        st["schedule_task"]
    end

    subgraph DEV["development"]
        cg["code_generation"]
        cr["code_review"]
        lc["local_copilot"]
    end

    subgraph RES["research"]
        wr["web_research"]
        dr["document_rag"]
        dp["deep_research"]
    end

    subgraph PER["personal"]
        qa["general_qa"]
        wa2["writing_assistant"]
    end

    subgraph AIDEV["ai_dev"]
        am["agent_monitoring"]
        ma["multi_agent"]
        ft["fine_tuning"]
    end

    style AUTO  fill:#fef9c3,stroke:#fde047
    style DEV   fill:#dbeafe,stroke:#93c5fd
    style RES   fill:#dcfce7,stroke:#86efac
    style PER   fill:#ede9fe,stroke:#c4b5fd
    style AIDEV fill:#ffe4e6,stroke:#fda4af
```

### `keywords`

Words and phrases in natural user messages that signal this use case.
Include product names (`OpenClaw` → `web_automation`), synonyms,
and action verbs (`scrape`, `crawl`, `automate`).

### `min_memory_gb`

**Not** the minimum to technically run — the minimum to be **useful**.
A 9B model running at 2 t/s due to swap is not useful for web_automation.
The threshold is where the recommended model runs at ≥10 t/s interactive speed.

---

## Concept Relationships

```mermaid
flowchart TB
    CY["<b>concepts.yaml</b><br/>semantic meanings"]

    subgraph ENTITIES["ontology.yaml entities"]
        UC["use_cases<br/>.keywords<br/>.min_memory_gb"]
        D["devices<br/>.tier / .type"]
        M["models<br/>.quality / .type"]
        F["frameworks<br/>.kind / .local_capable<br/>.runtime_support"]
    end

    CY -->|"explains"| UC
    CY -->|"explains"| D
    CY -->|"explains"| M
    CY -->|"explains"| F

    style CY fill:#fef9c3,stroke:#f59e0b,stroke-width:2px
    style ENTITIES fill:#f8fafc,stroke:#e2e8f0
```
