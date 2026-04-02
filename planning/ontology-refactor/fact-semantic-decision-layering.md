# Fact / Semantic / Decision Layering

## Status
Planning document — not yet canonical ontology structure.

## Purpose

이 문서는 `agent-setup-ontology`를 단일 정보 레이어에서 벗어나,
**fact / semantic / decision** 3층 구조로 재편하기 위한 설계 초안이다.

핵심 목적은 다음과 같다.

1. **객관 정보와 추천 판단을 분리**한다.
2. Copilot가 더 실질적인 의사결정 보조를 할 수 있도록 한다.
3. Ontology가 사례 나열이나 추천 문장으로 오염되지 않도록 한다.
4. Semantic layer를 통해 reusable interpretation을 만들고, Decision layer에서 사용자 맥락에 맞는 판단을 생성하게 한다.

---

## Problem Statement

현재 ontology는 대체로 다음을 한 층에서 함께 다루고 있다.

- 장비/모델/프레임워크의 사실 정보
- 실사용 관점의 해석
- 추천/비추천/트레이드오프 판단

이 구조는 다음 문제를 만든다.

### 1. 객관성과 판단이 섞인다
예:
- `noise_profile: low` 는 fact다.
- `quiet_always_on_friendly` 는 semantic interpretation이다.
- `recommended_for_low_maintenance_research` 는 decision이다.

이 셋을 같은 층에 두면 ontology가 혼탁해진다.

### 2. Copilot가 설명 가능한 추천을 만들기 어렵다
좋은 추천은 다음 구조를 따라야 한다.

> 선택 이유 = 사실 정보 + 의미 해석 + 사용자 제약

하지만 현재는 이 세 층이 분리되어 있지 않아, 추천 근거가 납작해지거나 일관성을 잃을 수 있다.

### 3. 대안 비교의 실질성이 약해진다
예를 들어 Mac mini와 OCuLink mini PC + RTX 3090은 단순 device 나열로는 충분하지 않다.
의사결정에 필요한 것은 실제로는 다음과 같은 해석/판단이다.

- low operational friction
- high local inference headroom
- troubleshooting sensitivity
- quiet always-on suitability
- maintenance burden trade-off

이들은 단순 사실 레이어를 넘어선다.

---

## Core Principle

> **Fact는 기반이다.**
> **Semantic은 Fact의 해석이다.**
> **Decision은 Semantic을 사용자 맥락에 적용한 판단이다.**

레이어 의존 방향은 다음과 같다.

```text
Fact → Semantic → Decision
```

즉:
- Semantic은 Fact 없이 존재하지 않는다.
- Decision은 Semantic 없이 안정적으로 설명되지 않는다.
- Copilot는 가능하면 Fact를 직접 추천으로 바꾸지 말고, Semantic을 경유한 뒤 Decision을 적용해야 한다.

---

## Layer Definitions

## 1. Fact Layer

### Definition
검증 가능하고 비교적 안정적인 객관 정보 층.

### Role
- 장비, 모델, 프레임워크, setup profile의 실제 속성 제공
- 추천 없이 판단의 재료를 제공
- source-backed 구조를 우선함

### Typical Contents
- device specs
- RAM / VRAM
- GPU vendor
- OS family
- expansion support
- pricing model
- deployment surface
- setup requirements
- certification / traceability / constraints
- power / noise / thermals (가능하면 class 또는 근거 기반)

### Must Not Contain
- “가성비 좋다”
- “초보자에게 좋다”
- “리서치에 추천”
- “관리 편하다”

이런 문장은 Fact layer에 두지 않는다.

### Example
```yaml
noise_profile: low
pricing_model: pay_as_you_go
gpu_expandability: low
supports_oculink: true
```

---

## 2. Semantic Layer

### Definition
Fact를 사람이 의사결정에 활용할 수 있도록 번역한 의미 해석 층.

### Role
- raw fact를 reusable interpretation으로 변환
- 직접 추천하지 않고 offering/setup의 성격을 표현
- 여러 fact를 묶어 하나의 의미 단위 concept를 형성

### Typical Contents
- low_operational_friction
- quiet_always_on_friendly
- high_local_inference_headroom
- troubleshooting_sensitive
- high_upgrade_flexibility
- stable_daily_driver
- research_batch_friendly
- mobile_unfriendly

### Must Not Contain
- “당신은 이걸 사라”
- “이 예산이면 A 추천”
- “초보자면 B 추천”

이것은 Decision layer의 일이다.

### Generation Rule
Semantic concept는 가능하면 복수 fact의 조합으로 도출한다.

### Example
```yaml
semantic_id: quiet_always_on_friendly
requires:
  noise_profile: low
  power_efficiency: high
  always_on_suitability: high
```

---

## 3. Decision Layer

### Definition
Semantic concept를 사용자 목표, 예산, 제약, 성향에 매핑하는 의사결정 층.

### Role
- recommendation
- prioritization
- exclusion
- trade-off explanation
- persona/context fit

### Typical Contents
- recommended_for_low_maintenance_research
- best_value_for_mass_research
- avoid_if_noise_sensitive
- choose_if_gpu_experiments_are_primary
- not_ideal_for_nontechnical_users

### Characteristics
Decision은 가장 context-sensitive하다.
같은 semantic profile이라도 사용자 goal이나 constraint가 달라지면 결론도 달라진다.

### Must Not Contain
- source-free factual claims
- semantic-free recommendation
- hard recommendation without rationale

---

## Why This Matters for Copilot

Copilot는 단순 fact lookup assistant가 아니라, 실제 추천을 수행하는 advisory system이다.
그렇다면 추천은 다음 흐름을 따라야 한다.

```text
1. 사용자 goal / constraint 파악
2. Fact layer에서 후보 수집
3. Semantic layer에서 후보 해석
4. Decision layer에서 우선순위 / 배제 / trade-off 판단
5. 자연어 추천 생성
```

핵심 규칙:

> Copilot는 Fact만으로 추천하지 않는다.
> Semantic 해석을 거친 뒤 Decision rule을 적용한다.

이 구조를 사용하면 다음이 가능해진다.

- 추천 근거 설명 가능성 증가
- trade-off 표현 개선
- 같은 fact를 다른 사용자에게 다르게 추천 가능
- ontology 오염 방지

---

## Example: Mac mini vs OCuLink Mini PC + RTX 3090

## Fact

### Mac mini
```yaml
noise_profile: low
power_efficiency: high
gpu_expandability: low
maintenance_burden: low
always_on_suitability: high
```

### OCuLink Mini PC + RTX 3090
```yaml
noise_profile: medium_high
power_efficiency: medium_low
gpu_expandability: high
maintenance_burden: high
local_inference_headroom: high
```

## Semantic

### Mac mini
- quiet_always_on_friendly
- low_operational_friction
- stable_daily_driver
- limited_gpu_growth_path

### OCuLink Mini PC + RTX 3090
- high_local_inference_headroom
- high_upgrade_flexibility
- troubleshooting_sensitive
- performance_first_profile

## Decision

### If goal = ontology-heavy mass research + low maintenance preference
- prefer: Mac mini

### If goal = local GPU-heavy experimentation + high tolerance for setup complexity
- prefer: OCuLink Mini PC + RTX 3090

이 예시는 왜 fact와 decision 사이에 semantic이 반드시 필요한지를 보여준다.

---

## Proposed Directory Structure

```text
agent-setup-ontology/
  concepts/
    fact/
    semantic/
    decision/
  instances/
    fact/
    semantic/
    decision/
  planning/
    ontology-refactor/
      fact-semantic-decision-layering.md
```

---

## Layer Rules

## Fact Layer Rules
- measurable / observable / source-backed 속성을 우선한다.
- recommendation language를 넣지 않는다.
- persona fit을 넣지 않는다.
- 가능하면 provenance를 명시한다.

## Semantic Layer Rules
- reusable interpretation만 넣는다.
- 단일 사례 전용 문구는 피한다.
- 여러 fact 조합으로 도출되는 개념을 우선한다.
- 직접 추천 문장은 넣지 않는다.

## Decision Layer Rules
- 사용자 목표/제약을 전제한다.
- recommendation, exclusion, trade-off를 허용한다.
- rationale 없이 결론만 두지 않는다.
- 가능한 경우 semantic concept를 근거로 표현한다.

---

## Migration Strategy

### Phase 1. Audit
- 기존 concepts/instances 중 판단 문장이 fact 레이어에 섞여 있는지 점검
- setup_profile, device, model, use_case, cost_estimation을 우선 점검 대상에 둔다

### Phase 2. Extract Semantics
- Mac mini / OCuLink / cloud deployment처럼 실질 비교가 필요한 케이스에서 semantic concept를 먼저 추출
- 예: low_operational_friction, troubleshooting_sensitive

### Phase 3. Introduce Decision Rules
- 사용자 목적별 decision concept 또는 rule을 정의
- 예: best_value_for_mass_research, avoid_if_noise_sensitive

### Phase 4. Copilot Integration
- copilot PROPOSE 단계에서 Fact → Semantic → Decision 흐름을 사용하도록 정렬
- recommendation rationale을 semantic concept 기반으로 생성

---

## Immediate Next Work

1. `concepts/fact/`, `concepts/semantic/`, `concepts/decision/` 구조 초안 만들기
2. Mac mini vs OCuLink 케이스를 첫 migration example로 사용
3. Copilot proposal format에 “왜 이걸 추천하는지”를 semantic concept 기반으로 추가
4. setup_profile와 device ontology에서 판단 문장을 분리

---

## Summary

이 refactor의 핵심은 단순하다.

- **Fact** = 사실
- **Semantic** = 의미
- **Decision** = 판단

그리고 항상:

> **판단은 사실 위에 직접 올리지 말고, 의미 해석을 거쳐 올린다.**

이 구조는 ontology의 객관성을 유지하면서도,
Copilot가 훨씬 실질적인 의사결정 보조를 하게 만드는 기반이 된다.
