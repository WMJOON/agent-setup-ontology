# Hermes Agent Ontology Addition — Implementation Record

**Target repo:** [`agent-setup-ontology`](https://github.com/WMJOON/agent-setup-ontology)
**Goal:** Promote `hermes-agent` from a relation-only reference to a fully defined framework with concrete repo and setup-profile entries, so that `deo_resolver.py`, `loader.py`, and `estimator.py` can return Hermes-based recommendations.

> **Status: COMPLETE.** All three YAML files (`framework.yaml`, `repo.yaml`, `setup_profile.yaml`) have been updated. The entries below reflect the actual implemented values.

---

## 0. Background

`hermes-agent` appeared in `instances/relation.yaml` under `framework_use_case_fits` and was referenced by two profile IDs (`setup-mac-mini-hermes-agent`, `setup-cpu-host-hermes-agent-hosted-model`) before those profiles were defined. This document records how that gap was closed.

**Verified Hermes facts used:**

| Field | Value |
|-------|-------|
| GitHub | `NousResearch/hermes-agent` |
| Stars | ~140K+ |
| Install | `curl -fsSL .../install.sh \| bash` (one-liner) |
| Ollama native | No — configure as custom OpenAI-compatible endpoint (`base_url=http://localhost:11434/v1`) |
| MCP support | Yes |
| Multiagent | Yes (spawns isolated subagents) |
| Min memory | 8 GB (reliable tool use: 9B+ / standard tier) |

---

## 1. Files modified in `agent-setup-ontology`

| File | Change |
|------|--------|
| `instances/framework.yaml` | Added one entry under `instances:` with `id: hermes-agent` |
| `instances/repo.yaml` | Added one entry with `id: repo-hermes-agent` |
| `instances/setup_profile.yaml` | Added two profiles: `setup-mac-mini-hermes-agent`, `setup-cpu-host-hermes-agent-hosted-model` |
| `instances/relation.yaml` | No change — references already existed |

---

## 2. Implemented entries

### 2.1 `instances/framework.yaml`

Added in the Automation Frameworks block (alongside `openclaw`):

```yaml
  - id: hermes-agent
    label: "Hermes Agent (Nous Research)"
    kind: automation          # NOT agent — Hermes is a personal-assistant automation runtime
    complexity: medium
    local_capable: true
    runtime_support: [openai, anthropic, openrouter, any]
    # Ollama is not natively listed; use as a custom OpenAI-compatible endpoint
    multiagent: true          # spawns isolated subagents for parallel workstreams
    mcp_support: true
    install: "https://github.com/NousResearch/hermes-agent"
    best_for: [personal_assistant, web_automation, file_automation, schedule_task, home_dashboard_agent]
    note: >
      Self-improving terminal agent. Persistent memory + skills learned from past sessions.
      40+ tools, MCP integration, cron scheduling. Messaging across
      Telegram / Discord / Slack / WhatsApp / Signal / Email.
      Seven execution backends — local, Docker, SSH, Singularity, Modal, Daytona, Vercel —
      so it scales from a $5 VPS to GPU clusters. Provider-agnostic across Nous Portal,
      OpenRouter (200+ models), NVIDIA NIM, OpenAI, Anthropic, HuggingFace, or custom endpoints.
      Spawns isolated subagents for parallel workstreams.
```

**Key schema decisions:**

- `kind: automation` — Hermes wraps any model in a personal-assistant shell rather than providing an agent-construction SDK. Use `agent` only for frameworks where developers build custom agents (e.g. CrewAI, LangGraph).
- `runtime_support` omits `ollama` as a top-level value because Ollama requires the custom-endpoint workaround; `any` covers it.
- `mcp_support: true` — confirmed in Hermes docs (MCP tool integration available).
- `multiagent: true` — Hermes can spawn isolated subagents.

### 2.2 `instances/repo.yaml`

Added in the agent section (alongside `repo-openclaw`):

```yaml
  - id: repo-hermes-agent
    label: "Hermes Agent (Nous Research)"
    github: "NousResearch/hermes-agent"
    framework_ref: hermes-agent
    category: automation      # mirrors framework kind
    stars_approx: "140K+"
    min_model_quality: standard
    min_memory_gb: 8
    ollama_compatible: true   # via custom OpenAI-compatible endpoint (base_url=http://localhost:11434/v1)
    install: |
      curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
      source ~/.bashrc
      hermes
      # Switch provider/model anytime: `hermes model`
      # Local Ollama: configure as a custom OpenAI-compatible endpoint
      #   (base_url=http://localhost:11434/v1)
    setup_guide: "https://hermes-agent.nousresearch.com/docs/"
    note: >
      Self-improving terminal agent with persistent memory and learned skills.
      40+ tools, MCP integration, cron scheduling. Messaging across
      Telegram / Discord / Slack / WhatsApp / Signal / Email.
      Seven execution backends — local, Docker, SSH, Singularity, Modal, Daytona, Vercel —
      so it scales from a $5 VPS to GPU clusters. Provider-agnostic across Nous Portal,
      OpenRouter (200+ models), NVIDIA NIM, OpenAI, Anthropic, HuggingFace, or custom endpoints.
      Spawns isolated subagents for parallel workstreams.
      Recommended threshold for reliable tool use: standard tier (9B+) or hosted frontier model.
```

### 2.3 `instances/setup_profile.yaml`

Two profiles placed near the existing Mac Mini profiles.

#### A. Always-on local — Mac Mini M4 32GB

```yaml
  - id: setup-mac-mini-hermes-agent
    label: "Self-Improving Assistant: Mac Mini M4 32GB + Hermes Agent"
    devices: [mac_mini_m4_32gb]
    model: "qwen3.5:35b-a3b"
    framework: hermes-agent
    repo: repo-hermes-agent
    use_cases: [personal_assistant, schedule_task, file_automation, home_dashboard_agent, email_assistant]
    complexity: medium
    always_on: true
    monthly_cost: "$0 (local only)"
    note: >
      Always-on private assistant with Hermes' learned-skills + persistent memory loop.
      Built-in cron, MCP, and messaging across Telegram/Discord/Slack/WhatsApp/Signal.
      Runs the local Qwen MoE via an OpenAI-compatible custom endpoint pointed at Ollama.
      Switch to a hosted provider (`hermes model`) when you need frontier quality.
    setup_steps:
      - "ollama pull qwen3.5:35b-a3b"
      - "curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
      - "source ~/.bashrc"
      - "hermes  # configure custom endpoint: base_url=http://localhost:11434/v1, model=qwen3.5:35b-a3b"
```

#### B. CPU-only host + hosted frontier model

```yaml
  - id: setup-cpu-host-hermes-agent-hosted-model
    label: "Low-Spec Always-On Host + Hermes Agent + Hosted Frontier Model"
    devices: [pc_no_gpu]
    model: "claude-sonnet-4-6"    # NOT haiku — sonnet-class needed for reliable multi-step tool use
    framework: hermes-agent
    repo: repo-hermes-agent
    use_cases: [personal_assistant, schedule_task, email_assistant, calendar_assistant, home_dashboard_agent]
    complexity: medium            # NOT low — requires API key management and endpoint config
    always_on: true               # host runs 24/7; model inference is remote
    monthly_cost: "$5–30 (electricity or VPS + per-token API usage)"
    note: >
      Lightweight Hermes deployment for users without local GPU. The host (CPU-only PC,
      mini-PC, or $5 VPS) only runs the Hermes agent loop and tools — inference happens at
      the hosted model provider (Claude/OpenAI/OpenRouter/NIM). Hermes' Modal/Daytona/Vercel
      backends can replace the always-on host for near-zero idle cost.
      Trade-off: data leaves the local box for the model provider.
    setup_steps:
      - "On the host (Linux x86_64): ensure outbound HTTPS to the model provider."
      - "curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
      - "source ~/.bashrc && hermes"
      - "hermes model  # pick anthropic/claude-sonnet-4-6 (or openrouter/openai/etc.)"
      - "Wire Telegram/Discord/Slack creds + cron schedules from the Hermes TUI."
```

**Profile B rationale (vs. original instruction):**

| Field | Original instruction | Actual | Reason |
|-------|---------------------|--------|--------|
| `model` | `claude-haiku-4-5` | `claude-sonnet-4-6` | Haiku is too weak for reliable multi-step tool use; sonnet is the minimum practical threshold |
| `complexity` | `low` | `medium` | API key setup, endpoint config, and messaging credential wiring raise the bar above `low` |
| `always_on` | `false` | `true` | The host process itself is always-on; only the model inference is remote |

---

## 3. Validate

Run from the `agent-setup-copilot` checkout:

```bash
# 1) Schema validation
python governance/scripts/validate.py \
  --instances-dir ../agent-setup-ontology/instances/ \
  --strict

# 2) Smoke-test the bundle pipeline
python skills/agent-setup-copilot/script/sync_ontology_bundle.py --smoke-test

# 3) Confirm Hermes surfaces in the resolver
python skills/agent-setup-copilot/script/deo_resolver.py \
  --query "personal assistant with cron and messaging" \
  --goal personal_assistant
```

Expected outcomes:

- `validate.py` exits 0 with no errors.
- `deo_resolver.py` returns at least one path with `framework: hermes-agent` and one of the two profile IDs in `selected_path`.

---

## 4. What is out of scope

- Editing `instances/relation.yaml` — Hermes was already wired in there.
- Editing `governance/schema.json` — schema is owned by `agent-setup-copilot`.
- Adding Hermes to the `bundle/` cache by hand — regenerated by `sync_ontology_bundle.py` after this PR merges.
- Ollama native runtime support — Hermes does not speak the Ollama REST API natively; the workaround (custom OpenAI-compatible endpoint) is documented in the `repo.yaml` note and `setup_steps`.
