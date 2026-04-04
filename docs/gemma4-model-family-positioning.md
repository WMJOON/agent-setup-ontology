# Gemma 4 Model Family Positioning

## 목적

이 문서는 Gemma 4 모델 패밀리의 공개 정보를 바탕으로,
`agent-setup-ontology`에서 Gemma 4 계열을 어떤 semantic layer와 taxonomy로 해석할지 정리하기 위한 positioning note이다.

이 문서는 곧바로 instance를 확정하기보다,
모델 family의 구조·특징·활용 포지션을 정리해 이후 ontology 반영 기준으로 삼는 데 목적이 있다.

---

## 1. 핵심 관찰

공개 자료 기준으로 Gemma 4는 단일 모델이 아니라,
**edge / on-device / local workstation / larger local reasoning**까지 포괄하는 family 구조를 가진다.

확인된 주요 라인업은 다음과 같다.

- Gemma-4-E2B
- Gemma-4-E4B
- Gemma-4-26B-A4B
- Gemma-4-31B
- (Thinking / IT variation 표기는 benchmark/serving 표현에서 함께 나타남)

현재 관점에서 중요한 것은 단순 param 수보다,
각 모델이 **어떤 deployment surface와 semantic role**을 갖는가이다.

---

## 2. 파라미터 / 아키텍처 / 컨텍스트 요약

### Gemma-4-E2B
- Dense Transformer
- 5.1B with embeddings / 2.3B effective
- 128K context
- sliding window 512
- modalities: text, audio, vision, video
- on-device / edge / phone급 inference 지향

### Gemma-4-E4B
- Dense Transformer
- 7.9B with embeddings / 4.5B effective
- 128K context
- sliding window 512
- modalities: text, audio, vision, video
- laptop / lightweight local multimodal 지향

### Gemma-4-26B-A4B
- MoE (128 experts)
- 26B total / 3.8B active
- 256K context
- text + image
- speed / quality trade-off가 좋은 workstation-grade choice

### Gemma-4-31B
- Dense Transformer
- 31B total
- 256K context
- text + image
- family 내 최고 성능 지향

---

## 3. semantic layer에서 중요한 특징

Gemma 4는 단순히 “Gemma 3보다 큰 후속 모델”이 아니라,
semantic layer에서 다음 특징이 중요하다.

### 3.1. Edge / on-device 친화성
특히 E2B / E4B는 mobile / laptop / edge deployment를 직접 겨냥한다.
즉 semantic layer에서는 다음 label로 읽을 수 있다.
- edge_friendly
- low_memory_friendly
- always_on_candidate
- lightweight_multimodal_candidate

### 3.2. Multimodal 기본 전제
E2B / E4B는 text만이 아니라 audio / vision / video를 다룰 수 있는 family라는 점이 중요하다.
즉 기존 local LLM ontology에서 text-only general model과는 구분되는 semantic 해석이 필요하다.

후보 semantic label:
- multimodal_ready
- speech_aware
- vision_aware

### 3.3. Intelligence-per-parameter 지향
공식 설명에서도 intelligence-per-parameter가 핵심 포지셔닝으로 보인다.
즉 semantic 해석상 “작은 모델이지만 agentic workflow에 실용적일 수 있다”는 방향이 강하다.

후보 semantic label:
- compact_high_capability
- smart-tool_suitable
- local_prototyping_friendly

### 3.4. Tool use / agentic workflow 적합성 가능성
공식 소개에서는 function calling과 agentic workflows를 직접 언급한다.
다만 ontology instance에 `tool_calling: true/false`를 넣기 전에는
실제 local runtime/serving 환경(Ollama, llama.cpp, vLLM, wrapper stack)에서의 안정성을 별도 검증해야 한다.

즉 semantic layer에서는 일단:
- agentic_workflow_candidate
- tool_use_candidate
로 보되,
instance field 확정은 추후 검증 기반으로 하는 것이 안전하다.

### 3.5. MoE / dense family 혼합
26B-A4B는 MoE적 장점을 가지므로,
단순 26B dense로 취급하면 ontology 해석이 부정확해질 수 있다.
이 모델은 semantic layer에서:
- workstation_sweet_spot_candidate
- speed_quality_balanced
- medium_high_memory_efficient
같은 label이 유효하다.

---

## 4. agent-setup-copilot 관점에서의 초기 해석

### E2B / E4B
초기 해석상 가장 흥미로운 포지션은 여기다.

이 계열은:
- smart tools
- lightweight semantic filtering
- always-on local helper
- multimodal edge assistant
- on-device ingestion / labeling
같은 use case에 잘 맞을 가능성이 크다.

특히 `smart-crawl-lite` 같은 초경량 evidence ingestion tool에서는,
최종 reasoning model보다 **semantic micro-task layer**에 더 적합해 보인다.

### 26B-A4B
이 계열은 Gemma 4 family 안에서 local workstation sweet spot 후보로 보인다.
MoE 구조 덕분에 active parameter가 작아,
quality 대비 속도/메모리 균형이 강점이 될 가능성이 있다.

### 31B
최고 성능 지향이지만,
agent-setup-copilot 관점에서는 일반 사용자 추천 기본값보다
고급 workstation / evaluation / multimodal reasoning 용도의 상위 옵션으로 보는 편이 적절하다.

---

## 5. ontology 반영 제안

### concepts/model.yaml 관점
Gemma 4 family는 다음 taxonomy extension 논의에 유리하다.
- primary_capability_class: general / multimodal / speech-adjacent
- interaction_profile: tool_agentic / vision_agentic / speech_pipeline candidate
- modality_flags: text_in / text_out / vision_in / audio_in

### instances/model.yaml 관점
현재는 다음 순서가 바람직하다.

1. Gemma 4 family positioning을 note로 먼저 기록
2. 실제 local runtime 태그 / quantization / tool calling 안정성 확인
3. E2B / E4B / 26B-A4B / 31B를 instance로 점진 추가
4. tool_calling field는 검증 후 확정

---

## 6. 주의점

- benchmark 표현의 “Thinking / IT” variation을 바로 별도 instance로 분리할지 여부는 신중해야 한다
- official marketing language와 실제 local inference usability는 다를 수 있다
- multimodal capability가 있어도 local stack에서 완전하게 지원되는지 별도 확인이 필요하다
- smart tools용으로 적합하다는 판단은 final recommendation layer 적합성과 동일하지 않다

---

## 7. 임시 결론

Gemma 4 family는 ontology 관점에서 단순 model refresh가 아니라,
**edge-friendly multimodal family + local workstation reasoning family**로 읽는 것이 더 적절하다.

특히 semantic layer에서는:
- E2B / E4B = lightweight multimodal / smart-tool candidate
- 26B-A4B = local workstation sweet-spot candidate
- 31B = highest-capability local option

으로 위치시키는 것이 합리적이다.

---

## 참고 메모

참고 출처:
- Google DeepMind Gemma 4 page
- Gemma 4 model family overview articles / local deployment summaries
- Unsloth Gemma 4 local run guide

후속 작업:
- `instances/model.yaml` 반영 여부 결정
- Gemma 4 E2B / E4B의 smart-tool suitability note 추가
- tool_calling / multimodal / local runtime compatibility 검증
