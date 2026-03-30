# Relation Normalization Plan

`agent-setup-ontology/instances/relation.yaml`가 풍부해지고 있지만,
현재는 category별 의미는 좋고 실제 배치는 점점 혼합되고 있다.
이 문서는 relation 구조를 copilot이 더 잘 소비하도록 정규화하는 계획이다.

---

## 1. 현재 상태 요약

현재 `relation.yaml`에는 대략 다음 종류가 공존한다.

- `upgrade_paths`
- `api_to_local_paths`
- `framework_use_cases`
- `model_use_case_notes`
- `setup_profile_notes`
- `use_case_adjacency`

문제는 이들이 모두 유효한 정보이지만,
**형태(shape)가 제각각이라 loader/deo_resolver가 일반화해서 쓰기 어렵다**는 점이다.

예를 들어:
- `framework_use_cases`는 `framework_id -> strong_fit[]/weak_fit[]`
- `setup_profile_notes`는 list 기반
- `use_case_adjacency`는 graph edge list 기반

즉, 의미는 좋지만 계산 표면은 불균일하다.

---

## 2. 정규화 목표

정규화의 목표는 세 가지다.

1. **사람이 읽기 쉬울 것**
2. **copilot이 일관된 방식으로 점수화할 수 있을 것**
3. **governance를 건드리지 않고 relation layer만 확장 가능할 것**

---

## 3. 추천 정규화 방향

## 3.1 Canonical edge list 도입

장기적으로는 relation.yaml 안에 아래와 같은 canonical edge list를 두는 것이 좋다.

```yaml
canonical_edges:
  - source_type: framework
    source_id: openclaw
    target_type: use_case
    target_id: personal_assistant
    relation: strong_fit
    weight: 1.0
    reason: "Messaging integrations + tool execution make it a natural always-on personal assistant."

  - source_type: setup_profile
    source_id: setup-obsidian-rag-desk
    target_type: use_case
    target_id: obsidian_rag
    relation: strong_fit
    weight: 1.0
    reason: "Best fit when the primary corpus is an Obsidian vault and retrieval quality matters."

  - source_type: use_case
    source_id: web_automation
    target_type: use_case
    target_id: browser_operator
    relation: specialization
    weight: 0.8
    reason: "Browser operator is a narrower, more interactive form of web automation."
```

장점:
- 모든 relation을 같은 방식으로 순회 가능
- scorer에서 edge weight를 바로 반영 가능
- reasoning trace 생성이 쉬움

---

## 3.2 Transitional compatibility 유지

기존 구조를 즉시 버릴 필요는 없다.

권장 순서:
1. 기존 relation 섹션 유지
2. loader에서 canonical index를 파생 생성
3. 나중에 relation source도 edge list 중심으로 이행

즉,
- source YAML은 당분간 사람이 읽기 좋은 형태 유지
- loader가 machine-friendly index를 생성

이게 현실적이다.

---

## 4. 섹션별 정규화 방안

## 4.1 framework_use_cases

현재:
- framework별 strong_fit / weak_fit

권장:
- loader가 아래 두 인덱스로 파생

```yaml
indexes:
  framework_to_use_case:
    openclaw:
      strong_fit: [web_automation, personal_assistant, browser_operator]
      weak_fit: [document_rag, multi_agent, local_rag_server]

  use_case_to_framework:
    personal_assistant:
      strong_fit: [openclaw, n8n]
      weak_fit: [claude-code]
```

---

## 4.2 setup_profile_notes

현재:
- profile 중심 list

권장:
- profile→use_case 뿐 아니라 use_case→profile 역인덱스 생성
- copilot 추천에서 이 역방향 인덱스가 매우 중요함

---

## 4.3 use_case_adjacency

현재:
- use_case 간 관계를 잘 표현하고 있음

권장:
- relation type을 제한된 enum처럼 운영
  - `specialization`
  - `generalization`
  - `deployment_variant`
  - `capability_upgrade`
  - `operationalization`
  - `adjacent`

이렇게 하면 copilot이
- "더 구체적인 버전"
- "배포형 변형"
- "상위 개념"
같은 설명을 일관되게 만들 수 있음.

---

## 4.4 model_use_case_notes

이건 매우 유용하다.
다만 framework/profile relation처럼 동일한 scoring API로 묶이게 해야 한다.

권장 표준:
- `fit: strong|standard|weak|none`
- loader가 score로 환산
  - strong = +1.0
  - standard = +0.5
  - weak = -0.2
  - none = -1.0

---

## 5. Loader responsibility

relation 정규화의 핵심은 source YAML보다 **loader의 파생 인덱스 생성 책임**에 있다.

loader는 relation.yaml을 읽은 뒤 아래를 만들면 좋다:

```yaml
relation_indexes:
  framework_to_use_case: ...
  use_case_to_framework: ...
  profile_to_use_case: ...
  use_case_to_profile: ...
  model_to_use_case: ...
  use_case_to_model: ...
  use_case_graph: ...
```

이렇게 되면 resolver는 YAML 원형을 몰라도 된다.

---

## 6. Resolver responsibility

resolver는 정규화된 relation index를 이용해:

- 점수 보정(score boost / penalty)
- 제외 사유 설명
- 인접 use_case fallback
- curated profile 우선 추천

을 수행해야 한다.

즉 relation은 설명 자료가 아니라 **점수화 재료**여야 한다.

---

## 7. Short recommendation

지금 가장 현실적인 방향은 이거다:

1. `relation.yaml` source는 큰 틀 유지
2. loader가 canonical relation indexes를 파생 생성
3. deo_resolver가 그 indexes를 사용해 score 조정
4. 장기적으로 canonical edge list source 도입 검토

이 경로가 가장 안전하고, 기존 데이터도 안 버리고, copilot 품질도 바로 올라간다.
