# Cost Guide — API vs Local

> This guide helps you estimate your LLM costs and decide
> when it makes sense to transition from cloud APIs to a local setup.

---

## The Journey

Most users start with a cloud API (no hardware cost, instant setup)
and move toward local models as their usage grows.

```mermaid
flowchart LR
    A["Start<br/>Cloud API<br/>Pay per token"]
    B["Growing usage<br/>Monthly bill rises<br/>Privacy concerns"]
    C["Break-even point<br/>API cost ≈ device cost"]
    D["Local setup<br/>One-time hardware<br/>Zero per-token cost"]

    A -->|"usage grows"| B
    B -->|"cost crosses threshold"| C
    C -->|"invest in hardware"| D

    style A fill:#dcfce7,stroke:#86efac
    style B fill:#fef9c3,stroke:#fde047
    style C fill:#ffe4e6,stroke:#fda4af
    style D fill:#dbeafe,stroke:#93c5fd
```

---

## API Service Tiers

```mermaid
flowchart TB
    subgraph CHEAP["Budget (< $1 / 1M input tokens)"]
        G1["Gemini 2.0 Flash<br/>$0.10 in / $0.40 out"]
        O1["GPT-4o mini<br/>$0.15 in / $0.60 out"]
        A1["Claude Haiku 4.5<br/>$0.80 in / $4.00 out"]
    end

    subgraph MID["Mid-range ($1–3 / 1M input tokens)"]
        G2["Gemini 2.0 Pro<br/>$1.25 in / $5.00 out"]
        O2["GPT-4o<br/>$2.50 in / $10.00 out"]
        A2["Claude Sonnet 4.6<br/>$3.00 in / $15.00 out"]
    end

    style CHEAP fill:#dcfce7,stroke:#86efac
    style MID   fill:#fef9c3,stroke:#fde047
```

---

## Estimating Your Monthly Cost

### Token usage by use case

| Use case | Tokens / day (typical) | Tokens / day (heavy) |
|----------|------------------------|----------------------|
| `general_qa` | 20K | 100K |
| `code_generation` | 80K | 300K |
| `web_automation` | 150K | 500K |
| `document_rag` | 100K | 400K |
| `web_research` | 200K | 600K |
| `agent_monitoring` | 300K | 1M+ |
| `multi_agent` | 500K | 2M+ |

> Tokens = input + output. Agent tasks tend to be input-heavy (tool call context).
> Assume ~60% input / 40% output for agent workloads.

### Monthly cost formula

```
monthly_tokens = tokens_per_day × 30
input_tokens   = monthly_tokens × 0.60
output_tokens  = monthly_tokens × 0.40

monthly_cost   = (input_tokens / 1,000,000 × input_price)
               + (output_tokens / 1,000,000 × output_price)
```

### Example: code_generation, typical usage (80K tokens/day)

| API | Monthly cost |
|-----|-------------|
| Gemini 2.0 Flash | $0.14 + $0.38 = **$0.52** |
| GPT-4o mini | $0.22 + $0.58 = **$0.79** |
| Claude Haiku 4.5 | $1.15 + $3.84 = **$4.99** |
| GPT-4o | $3.60 + $9.60 = **$13.20** |
| Claude Sonnet 4.6 | $4.32 + $14.40 = **$18.72** |

### Example: agent_monitoring, heavy usage (1M tokens/day)

| API | Monthly cost |
|-----|-------------|
| Gemini 2.0 Flash | **$54** |
| GPT-4o mini | **$99** |
| Claude Haiku 4.5 | **$624** |
| GPT-4o | **$1,650** |
| Claude Sonnet 4.6 | **$2,340** |

At this scale, local hardware pays for itself within weeks.

---

## Break-Even Calculator

### Device monthly cost (2-year amortization)

| Device | Price | Monthly cost |
|--------|-------|-------------|
| Mac Mini M4 16GB | ~$600 | **$25** |
| Mac Mini M4 32GB | ~$750 | **$31** |
| Mac Mini M4 Pro 24GB | ~$1,300 | **$54** |
| PC + RTX 4060 8GB | ~$400 (GPU only) | **$17** |
| PC + RTX 4090 24GB | ~$2,000 (GPU only) | **$83** |

> Electricity: ~$2–5/month for Mac Mini, ~$10–20/month for high-end PC.

### Break-even point

```mermaid
flowchart TD
    Q1{"Monthly API cost<br/>> device monthly cost?"}

    Q1 -->|"No — stay on API"| STAY["Keep using API<br/>Lower friction, no hardware"]
    Q1 -->|"Yes — consider local"| CHECK{"Privacy or<br/>latency concerns?"}

    CHECK -->|"Yes"| LOCAL["Go local now<br/>Even before break-even"]
    CHECK -->|"No"| CALC["Calculate payback period<br/>price / (api_cost - device_cost)"]

    CALC -->|"< 6 months"| BUY["Strong case to buy hardware"]
    CALC -->|"6–18 months"| MAYBE["Consider it — depends on use case growth"]
    CALC -->|"> 18 months"| WAIT["Stay on API for now<br/>Revisit if usage grows"]

    style LOCAL fill:#dbeafe,stroke:#93c5fd
    style BUY   fill:#dbeafe,stroke:#93c5fd
    style STAY  fill:#dcfce7,stroke:#86efac
    style WAIT  fill:#dcfce7,stroke:#86efac
```

---

## Local vs API: Quality Mapping

Each API service maps to a comparable local model.
Quality is equivalent for most agent tasks; the main difference is speed and privacy.

```mermaid
flowchart LR
    subgraph API["Cloud API"]
        A1["Gemini 2.0 Flash<br/>GPT-4o mini"]
        A2["Claude Haiku 4.5"]
        A3["Gemini 2.0 Pro<br/>GPT-4o<br/>Claude Sonnet 4.6"]
    end

    subgraph LOCAL["Local Model (Ollama)"]
        L1["qwen3.5:9b<br/>standard quality"]
        L2["qwen3.5:14b<br/>standard-plus quality"]
        L3["qwen3.5:27b<br/>qwen3.5:35b-a3b<br/>pro quality"]
    end

    A1 <-->|"comparable"| L1
    A2 <-->|"comparable"| L2
    A3 <-->|"comparable"| L3

    style API   fill:#fef9c3,stroke:#fde047
    style LOCAL fill:#dbeafe,stroke:#93c5fd
```

---

## Recommended Starting Path

```mermaid
flowchart TD
    START["New to local AI agents"]

    START --> Q1{"Have a GPU or<br/>Apple Silicon Mac?"}

    Q1 -->|"Yes (≥16 GB)"| DIRECT["Start local directly<br/>ollama pull qwen3.5:9b"]
    Q1 -->|"No / Unsure"| API["Start with API<br/>Gemini Flash or GPT-4o mini<br/>(cheapest capable options)"]

    API --> TRACK["Track monthly spend<br/>for 1–2 months"]
    TRACK --> Q2{"Monthly spend<br/>> $30?"}

    Q2 -->|"No"| CONTINUE["Continue on API<br/>Usage doesn't justify hardware"]
    Q2 -->|"Yes"| HARDWARE["Plan hardware purchase<br/>See device recommendations"]

    HARDWARE --> DEVICE["Use copilot to pick device<br/>based on your use cases"]

    style DIRECT   fill:#dbeafe,stroke:#93c5fd
    style HARDWARE fill:#dbeafe,stroke:#93c5fd
    style CONTINUE fill:#dcfce7,stroke:#86efac
```

---

## Tips

- **Start cheap**: Gemini 2.0 Flash is the lowest cost entry point with good quality.
- **Track tokens**: Most API dashboards show daily token usage. Check after 1 week.
- **Agent tasks cost more**: Tool calls add input tokens. Expect 2-5× more tokens than simple chat.
- **Privacy threshold**: If you're processing sensitive data, local setup is worth it regardless of cost.
- **MoE advantage**: Local MoE models (qwen3.5:35b-a3b) punch above their weight — `pro` quality at `standard` running cost.
