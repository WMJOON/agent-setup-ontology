# 기여 가이드

`ontology.yaml` 파일만 수정하면 됩니다. 코드 지식은 필요 없습니다.

---

## 새 디바이스 추가

`ontology.yaml`의 `devices:` 섹션에 아래 형식으로 추가하세요.

```yaml
- id: mac_studio_64gb          # 고유 ID (소문자+언더스코어)
  label: "Mac Studio M4 Max 64GB"
  type: mac-studio              # macbook / mac-mini / mac-studio / pc / ai-supercomputer / other
  chip: M4 Max
  memory_gb: 64
  memory_bandwidth_gbs: 410
  gpu_vram_gb: 0
  portability: stationary       # portable / stationary
  always_on: true
  price_range: "400만원~"
  tier: pro                     # light / standard / standard-plus / pro
  max_model: qwen3.5:72b
  note: "Mac 최상위 로컬 AI 서버"
  supported_use_cases: all
  unsupported_use_cases: []
```

**필수 필드:** `id`, `label`, `type`, `memory_gb`, `tier`, `max_model`

---

## 새 모델 추가

`ontology.yaml`의 `models:` 섹션에 추가하세요.

```yaml
- id: llama4:17b
  label: "llama4:17b"
  params_b: 17
  type: MoE                     # dense / MoE
  active_params_b: 5            # MoE일 때만
  min_memory_gb: 16
  quality: standard-plus        # light / standard / standard-plus / pro
  tool_calling: true
  speed_note: "~20 t/s (M-series 16GB)"
  note: "Meta Llama 4 MoE"
```

---

## 새 프레임워크 추가

`ontology.yaml`의 `frameworks:` 섹션에 추가하세요.

```yaml
- id: pocketflow
  label: "PocketFlow"
  complexity: low               # low / medium / high
  multiagent: false
  mcp_support: false
  ollama_support: true
  install: "pip install pocketflow"
  best_for: [code_generation, file_automation]
  note: "100줄 미니멀 Agent 프레임워크"
```

---

## 새 사용 목적 추가

`ontology.yaml`의 `use_cases:` 섹션에 추가하세요.

```yaml
- id: voice_assistant
  label: "음성 비서"
  description: "로컬 STT + LLM + TTS 파이프라인"
  keywords: [음성, 목소리, STT, TTS, 스피커]
  min_memory_gb: 16
  needs_always_on: true
  recommended_models: [qwen3.5:9b]
  recommended_frameworks: [smolagents]
```

---

## PR 체크리스트

- [ ] `id`가 기존 항목과 중복되지 않는가
- [ ] `label`이 사용자가 이해하기 쉬운 이름인가
- [ ] 출처(공식 스펙 페이지, 벤치마크 링크)를 PR 설명에 포함했는가
- [ ] 스키마 검증 통과 (consumer governance validate 사용):
  ```bash
  # agent-setup-copilot 레포를 로컬에 클론한 경우 (per-entity 디렉토리 방식)
  python path/to/agent-setup-copilot/governance/scripts/validate.py \
    --instances-dir instances/ --strict

  # 또는 CI가 자동으로 실행 (PR 시 .github/workflows/validate.yml)
  ```
