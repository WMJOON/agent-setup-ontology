# Model Taxonomy Plan

현재 `agent-setup-ontology`의 모델 분류는 주로 다음 축으로 이루어진다.

- `quality`: light / standard / standard-plus / pro
- `type`: dense / MoE / reasoning
- `tool_calling`: true / false

이 구조는 추천 엔진의 1차 선택에는 유효하지만,
모델 종류가 늘어날수록 **실제 역할(role)** 을 설명하기에는 부족하다.

예를 들어 아래 모델들은 quality/type만으로는 잘 안 갈린다.

- Qwen3 / Llama / Granite → 범용 chat/agent
- Codestral / StarCoder2 / Qwen-Coder → coding 특화
- DeepSeek-R1 → reasoning 특화
- qwen3-embedding / embeddinggemma → embedding 전용
- Llama 4 / Gemma multimodal variants → multimodal/vision
- Whisper / faster-whisper 계열 → speech/transcription

따라서 장기적으로는 model taxonomy를 **역할 기반**으로 확장하는 것이 필요하다.

---

## 1. 추천 taxonomy 축

### 1.1 Primary capability class

모델이 주로 어떤 역할로 쓰이는지 나타내는 상위 분류.

권장 값:
- `general`
- `coding`
- `reasoning`
- `embedding`
- `multimodal`
- `speech`

설명:
- `general`: 범용 chat/assistant/agent 모델
- `coding`: 코드 생성·리뷰·IDE 보조 중심 모델
- `reasoning`: 긴 CoT / judge / 분석 중심 모델
- `embedding`: retrieval/vectorization 전용 모델
- `multimodal`: 텍스트 + 이미지 입력 모델
- `speech`: transcription / speech understanding 계열

---

### 1.2 Interaction profile

에이전트/운영 관점에서 모델이 어떤 상호작용 특성을 가지는지.

권장 값:
- `tool_agentic`
- `chat_only`
- `batch_reasoner`
- `retrieval_backend`
- `vision_agentic`
- `speech_pipeline`

예:
- Qwen 9B → `tool_agentic`
- Gemma 27B → `chat_only`
- DeepSeek-R1 32B → `batch_reasoner`
- qwen3-embedding → `retrieval_backend`

---

### 1.3 Modality flags

권장 필드:
- `text_in: true/false`
- `text_out: true/false`
- `vision_in: true/false`
- `audio_in: true/false`
- `embedding_out: true/false`

이건 특히 multimodal / embedding / speech 모델이 들어오면 필요해진다.

---

## 2. Schema migration stance

중요:
현재 `agent-setup-copilot/governance/schema.json`을 깨지 말아야 한다.

따라서 바로 정식 required field로 넣기보다,
우선은 아래 순서를 권장한다.

### Phase A — concept-level taxonomy only
- `concepts/model.yaml`에 taxonomy 개념 추가
- 아직 instances/model.yaml에 필수 적용하지 않음

### Phase B — optional metadata fields
- instances/model.yaml에 optional 필드로 서서히 도입
- validator 허용 범위 확인 후 진행

### Phase C — governance promotion
- 실제로 copilot가 적극 활용하게 되면 governance에 정식 필드 승격

즉 지금 단계에서는:
> schema를 깨지 않는 개념 설계가 우선

---

## 3. Immediate practical mapping

현재 모델들을 taxonomy 관점에서 보면 대략 다음과 같다.

### general
- qwen3.5:4b / 9b / 14b / 35b-a3b / 27b / 32b / 72b
- llama3.1:8b / llama3.2:3b / llama3.3:70b
- mistral:7b
- granite3.1-dense:8b
- granite3.1-moe:3b

### coding
- qwen2.5-coder:14b
- codestral:22b
- starcoder2:3b / 7b / 15b (추가 시)
- phi4:14b (coding-leaning hybrid)

### reasoning
- deepseek-r1:8b
- deepseek-r1:32b
- gpt-oss (추가 시, 로컬 open-weight reasoning 포지션)
- glm-5 (추가 시, 하이엔드 reasoning/agentic 포지션)

### embedding
- qwen3-embedding
- embeddinggemma

### multimodal
- llama4 / llama4:scout
- gemma multimodal variants
- qwen3.5 multimodal variants

### speech
- whisper / faster-whisper 계열
- (엄밀히는 LLM이 아니라 speech model stack에 가까움)

---

## 4. Why this matters

이 taxonomy가 있으면 copilot이 이런 식으로 더 잘 설명할 수 있다.

- "이건 범용 assistant 모델이고"
- "이건 coding 특화라 코드 작업에 우세하고"
- "이건 embedding 전용이라 generation 대신 retrieval backbone으로 써야 하고"
- "이건 reasoning 모델이라 agent loop엔 느리지만 judge 용도로 좋다"

즉,
quality/type만으론 안 되는 **역할 설명**이 가능해진다.

---

## 5. Recommendation

다음 단계는 이렇게 가는 것이 가장 안전하다.

1. `concepts/model.yaml`에 taxonomy 축 추가
2. 새 모델 추가할 때 taxonomy 관점으로 shortlist 설계
3. validator 영향 없는 선에서 optional metadata 실험
4. 실제 유용성이 확인되면 governance 승격

이렇게 하면 model coverage를 넓히면서도 ontology가 난잡해지지 않는다.

---

## 6. Immediate shortlist for ontology expansion

### Tier 1 — practical additions now
- `starcoder2:3b`
- `starcoder2:7b`
- `starcoder2:15b`
- `mistral-small`
- `qwen3-embedding`
- `embeddinggemma`

이유:
- coding / mid-size general / embedding 축을 즉시 보강함
- Ollama 실사용성과 ontology 설명력이 모두 높음

### Tier 2 — add later with stronger taxonomy support
- `llama4`
- `llama4:scout`
- `glm-5`
- `gpt-oss`

이유:
- multimodal / frontier reasoning / agentic 고급 축 보강 가치가 있음
- 하지만 현 ontology의 deterministic recommendation layer에는 다소 무거운 후보들임
