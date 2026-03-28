# Schema Reference

> **Structural contract (required fields, types, enums)**
> is owned by [`agent-setup-copilot/governance/`](https://github.com/WMJOON/agent-setup-copilot/tree/main/governance).
>
> **Semantic definitions (what values mean)**
> are in [`concepts.yaml`](../concepts.yaml) in this repo.

---

## Overview

`ontology.yaml` defines six entity types:

```
ontology.yaml
├── use_cases[]     What goals users want to accomplish
├── devices[]       Complete machines (Mac, pre-built PC, laptops)
├── components[]    PC hardware parts (GPU cards, RAM kits) for custom builds
├── models[]        Ollama-pullable LLMs
├── frameworks[]    Tools for building, running, or interacting with agents
└── api_services[]  Cloud LLM APIs — starting point before going local
```

**devices vs components:**
Mac devices are complete, fixed-spec products.
PC users choose components (GPU + RAM) to build a custom setup.
The copilot recommends either a complete device or a component combination
depending on the user's platform preference.

Entities are linked by cross-references:

```mermaid
flowchart LR
    D["devices"]
    UC["use_cases"]
    M["models"]
    F["frameworks"]
    API["api_services"]

    D   -->|"max_model"| M
    D   -->|"supported_use_cases[]"| UC
    UC  -->|"recommended_models[]"| M
    UC  -->|"recommended_frameworks[]"| F
    API -->|"local_alternative"| M
```

---

## Entity: `use_case`

A goal the user wants to accomplish with a local AI agent.

| Field | Required | Type | Constraints |
|-------|----------|------|-------------|
| `id` | ✅ | string | `[a-z0-9_.:‑]+` |
| `label` | ✅ | string | Human-readable name |
| `description` | ✅ | string | One-line summary |
| `keywords` | ✅ | string[] | ≥1 item. Used for intent matching |
| `min_memory_gb` | ✅ | integer | ≥0 |
| `needs_always_on` | — | boolean | True → prefer stationary device |
| `requires_gpu` | — | boolean | True → discrete GPU strongly preferred |
| `recommended_models` | — | string[] | References `models[*].id` |
| `recommended_frameworks` | — | string[] | References `frameworks[*].id` |

**Example:**

```yaml
- id: web_automation
  label: "Web Automation"
  description: "Autonomous browser control, scraping, form filling"
  keywords: [OpenClaw, browser, scraping, automation, web]
  min_memory_gb: 16
  needs_always_on: false
  recommended_models: [qwen3.5:9b, qwen3.5:35b-a3b]
  recommended_frameworks: [openclaw, smolagents]
```

---

## Entity: `device`

A physical machine capable of running a local LLM via Ollama.

| Field | Required | Type | Constraints |
|-------|----------|------|-------------|
| `id` | ✅ | string | `[a-z0-9_.:‑]+` |
| `label` | ✅ | string | |
| `type` | ✅ | enum | `macbook` \| `mac-mini` \| `mac-studio` \| `pc` \| `other` |
| `memory_gb` | ✅ | integer | ≥1 |
| `tier` | ✅ | enum | `light` \| `standard` \| `standard-plus` \| `pro` |
| `max_model` | ✅ | string | References `models[*].id` |
| `chip` | — | string | e.g. `M4`, `M4 Pro`, `Intel i9` |
| `memory_bandwidth_gbs` | — | number | Peak bandwidth in GB/s |
| `gpu_vram_gb` | — | integer | 0 if no discrete GPU |
| `portability` | — | enum | `portable` \| `stationary` |
| `always_on` | — | boolean | |
| `price_range` | — | string | Approximate cost string |
| `note` | — | string | One-line description |
| `best_for` | — | string | Short sentence on primary use |
| `supported_use_cases` | — | string[] \| `"all"` | References `use_cases[*].id`, or literal `"all"` |
| `unsupported_use_cases` | — | string[] | References `use_cases[*].id` |

**`tier` quick reference** (→ see `concepts.yaml` for full definitions):

| Tier | Memory | Representative model |
|------|--------|---------------------|
| `light` | ≤8 GB | qwen3.5:4b |
| `standard` | 16 GB | qwen3.5:9b |
| `standard-plus` | 32 GB (base chip) | qwen3.5:35b-a3b |
| `pro` | 32 GB+ high-BW, or 24 GB+ GPU | qwen3.5:27b / 32b |

**Example:**

```yaml
- id: mac_mini_m4_32gb
  label: "Mac Mini M4 32GB"
  type: mac-mini
  chip: M4 (base)
  memory_gb: 32
  memory_bandwidth_gbs: 120
  gpu_vram_gb: 0
  portability: stationary
  always_on: true
  price_range: "~$750"
  tier: standard-plus
  max_model: qwen3.5:35b-a3b
  best_for: "Best price-to-capability always-on AI server"
  supported_use_cases: all
  unsupported_use_cases: [fine_tuning]
```

---

## Entity: `model`

An Ollama-pullable LLM. The `id` is the exact `ollama pull` tag.

| Field | Required | Type | Constraints |
|-------|----------|------|-------------|
| `id` | ✅ | string | Exact Ollama tag, e.g. `qwen3.5:9b` |
| `label` | ✅ | string | |
| `params_b` | ✅ | number | Total parameters in billions |
| `type` | ✅ | enum | `dense` \| `MoE` |
| `min_memory_gb` | ✅ | integer | Minimum RAM to run at practical speed |
| `quality` | ✅ | enum | `light` \| `standard` \| `standard-plus` \| `pro` |
| `tool_calling` | ✅ | boolean | Reliable structured tool/function call support |
| `active_params_b` | — | number | MoE only: active params per forward pass |
| `speed_note` | — | string | Representative speed on reference hardware |
| `sweet_spot` | — | boolean | Best quality-to-resource ratio in its tier |
| `note` | — | string | One-line description |

**`quality` quick reference** (→ see `concepts.yaml` for full definitions):

| Quality | Scale | Typical use |
|---------|-------|------------|
| `light` | 1–4B | Autocomplete, simple Q&A |
| `standard` | 7–9B | Most single-agent tasks |
| `standard-plus` | ~14B | Code review, nuanced reasoning |
| `pro` | 27B+ | LLM-as-Judge, multi-agent |

**Example:**

```yaml
- id: qwen3.5:35b-a3b
  label: "qwen3.5:35b-a3b"
  params_b: 35
  active_params_b: 3
  type: MoE
  min_memory_gb: 32
  quality: pro
  tool_calling: true
  speed_note: "~18-25 t/s on Mac Mini M4 32GB"
  sweet_spot: true
  note: "MoE sweet spot: 35B quality, 3B active params. Best pick for 32GB devices."
```

---

## Entity: `framework`

A tool for building, running, or interacting with a local AI agent.

| Field | Required | Type | Constraints |
|-------|----------|------|-------------|
| `id` | ✅ | string | `[a-z0-9_.:‑]+` |
| `label` | ✅ | string | |
| `kind` | ✅ | enum | `agent` \| `automation` \| `ui` \| `ide` \| `rag` |
| `complexity` | ✅ | enum | `low` \| `medium` \| `high` |
| `local_capable` | ✅ | boolean | Can run without any API key using Ollama |
| `runtime_support` | ✅ | string[] | ≥1 item from allowed set (see below) |
| `multiagent` | — | boolean | Supports multi-agent collaboration |
| `mcp_support` | — | boolean | Supports Model Context Protocol |
| `install` | — | string | Installation command or URL |
| `best_for` | — | string[] | References `use_cases[*].id` |
| `note` | — | string | One-line description |

**`kind` quick reference** (→ see `concepts.yaml` for full definitions):

| Kind | Role | Examples |
|------|------|---------|
| `agent` | Orchestrates tools + memory + reasoning | smolagents, crewai, langgraph |
| `automation` | LLM-powered desktop/browser automation | openclaw |
| `ui` | Chat front-end, no coding | open-webui, anythingllm |
| `ide` | Editor inline copilot | continue |
| `rag` | Document retrieval + Q&A | llamaindex |

**`runtime_support` allowed values:**

| Value | Meaning |
|-------|---------|
| `ollama` | Local Ollama — no API key, fully private |
| `openai` | OpenAI API |
| `anthropic` | Anthropic API |
| `huggingface` | HuggingFace Inference / Transformers |
| `litellm` | Universal proxy (100+ providers) |
| `any` | Any OpenAI-compatible endpoint |

**Example:**

```yaml
- id: openclaw
  label: "OpenClaw"
  kind: automation
  complexity: medium
  local_capable: true
  runtime_support: [ollama, openai, anthropic]
  multiagent: false
  mcp_support: false
  install: "https://github.com/openclaw/openclaw"
  best_for: [web_automation]
  note: "Autonomous browser, file, and code execution. LLM-powered desktop automation."
```

---

## Entity: `component`

An individual hardware part for PC builds. Prices are not hardcoded —
use `price_search_query` with a web search tool for current pricing.

| Field | Required | Type | Constraints |
|-------|----------|------|-------------|
| `id` | ✅ | string | `[a-z0-9_.:‑]+` |
| `label` | ✅ | string | |
| `component_type` | ✅ | enum | `gpu` \| `cpu` \| `memory` |
| `inference_tier` | ✅ | enum | `light` \| `standard` \| `standard-plus` \| `pro` |
| `price_search_query` | ✅ | string | Web search query for current price |
| `vram_gb` | — | integer | GPU only: VRAM in GB |
| `memory_bandwidth_gbs` | — | number | GPU only: bandwidth in GB/s |
| `tdp_w` | — | integer | GPU: thermal design power in watts |
| `architecture` | — | string | GPU: chip architecture name |
| `capacity_gb` | — | integer | Memory only: total capacity |
| `generation` | — | string | Memory only: DDR4 / DDR5 |
| `llm_perf_note` | — | string | Representative inference speed note |

**GPU `inference_tier` by VRAM:**

| VRAM | Tier | Representative max model |
|------|------|--------------------------|
| 8 GB | `standard` | qwen3.5:9b (Q4) |
| 12 GB | `standard` | qwen3.5:9b fast |
| 16 GB | `standard-plus` | qwen3.5:14b (Q4) |
| 24 GB | `pro` | qwen3.5:27b (Q4) |
| 32 GB | `pro` | qwen3.5:32b (Q4) |

**Example:**

```yaml
- id: rtx-4090
  label: "NVIDIA GeForce RTX 4090"
  component_type: gpu
  vram_gb: 24
  memory_bandwidth_gbs: 1008
  tdp_w: 450
  architecture: ada-lovelace
  inference_tier: pro
  llm_perf_note: "~40-50 t/s for 27B Q4. Runs 32B dense in VRAM."
  price_search_query: "NVIDIA RTX 4090 24GB GPU price"
```

---

## Entity: `api_service`

A cloud LLM API as a cost-effective starting point before investing in local hardware.
See [`cost-guide.md`](./cost-guide.md) for break-even calculation.

| Field | Required | Type | Constraints |
|-------|----------|------|-------------|
| `id` | ✅ | string | `[a-z0-9_.:‑]+` |
| `label` | ✅ | string | |
| `provider` | ✅ | enum | `anthropic` \| `openai` \| `google` \| `mistral` \| `cohere` \| `other` |
| `quality` | ✅ | enum | Same as models: `light` \| `standard` \| `standard-plus` \| `pro` |
| `tool_calling` | ✅ | boolean | Supports structured tool/function calls |
| `pricing` | ✅ | object | `input_per_1m`, `output_per_1m` (USD per 1M tokens) |
| `context_window_k` | — | integer | Max context in K tokens |
| `local_alternative` | — | string | References `models[*].id` — comparable local model |
| `note` | — | string | One-line description |

**Example:**

```yaml
- id: claude-haiku-4-5
  label: "Claude Haiku 4.5"
  provider: anthropic
  quality: standard
  tool_calling: true
  context_window_k: 200
  pricing:
    input_per_1m: 0.80
    output_per_1m: 4.00
    currency: USD
    source: "https://www.anthropic.com/pricing"
  local_alternative: "qwen3.5:9b"
  note: "Fastest Anthropic model. Best cost-per-task for simple agents."
```

---

## Cross-Reference Diagram

```mermaid
flowchart TD
    subgraph UC["use_cases"]
        UC_rm["recommended_models[]"]
        UC_rf["recommended_frameworks[]"]
    end

    subgraph D["devices"]
        D_mm["max_model"]
        D_suc["supported_use_cases[]"]
    end

    subgraph M["models"]
        M_id["id ◄"]
    end

    subgraph F["frameworks"]
        F_id["id ◄"]
    end

    subgraph API["api_services"]
        API_la["local_alternative"]
    end

    D_mm  -->|"references"| M_id
    D_suc -->|"references"| UC
    UC_rm -->|"references"| M_id
    UC_rf -->|"references"| F_id
    API_la -->|"references"| M_id
```

All cross-references are validated by
[`agent-setup-copilot/governance/scripts/validate.py`](https://github.com/WMJOON/agent-setup-copilot/blob/main/governance/scripts/validate.py).
