# Copilot Projection Contract

> 목적: `agent-setup-ontology`의 구조화된 개념/인스턴스 데이터를
> `agent-setup-copilot`의 상담·추천·추론 런타임에 일관되게 사영(projection)하기 위한 계약 초안.
>
> 핵심 원칙:
> - **governance의 소유자는 `agent-setup-copilot`** 이다.
> - `agent-setup-ontology`는 **data provider / SoT** 이다.
> - projection은 ontology를 copilot의 **decision surface** 로 내리는 번역 계층이다.

---

## 1. 역할 분리

### 1.1 Contract owner — `agent-setup-copilot`

`agent-setup-copilot/governance/` 가 다음을 소유한다.

- required fields
- enum contract
- cross-reference contract
- validator
- state machine에서 기대하는 입력 구조
- copilot이 신뢰하는 recommendation primitive

즉, **copilot이 소비 가능한 세계의 문법은 consumer가 정의**한다.

### 1.2 Data provider — `agent-setup-ontology`

`agent-setup-ontology` 는 다음을 제공한다.

- concepts/ = semantic definitions
- instances/ = concrete recommendation data
- relation data = recommendation path / compatibility / upgrade path
- setup_profile / cost_estimation / usage_input = copilot이 reasoning에 쓰는 재료

즉, **ontology는 사실·정의·관계의 저장소**다.

### 1.3 Projection layer

projection의 역할은 다음과 같다.

1. ontology 엔티티를 copilot 내부 판단 단위로 변환
2. copilot 상태기계(INTAKE/GATE/PROPOSE)가 요구하는 입력 슬롯으로 정렬
3. 추천, 제외, 비교, cost analysis 출력을 만들기 위한 계산 표면 제공

정리하면:

- ontology = 명사 사전
- copilot = 동사 엔진
- projection = 명사 → 판단 노드로의 변환 규칙

---

## 2. Projection 대상

projection은 크게 4개 층으로 일어난다.

### P1. Intake Projection
사용자 발화 → ontology query primitive 로 변환

### P2. Eligibility Projection
ontology instance → 후보/제약/호환성 판단 재료로 변환

### P3. Recommendation Projection
후보 집합 → 옵션 A/B/C 또는 비교표로 변환

### P4. Explanation Projection
선정 이유 / 제외 이유 / trade-off 를 자연어 rationale로 변환

---

## 3. Governance-aligned source map

| Ontology source | Owner | Copilot usage | Projection role |
|---|---|---|---|
| `concepts/use_case.yaml` | ontology | use-case 의미 해석 | intent normalization |
| `instances/use_case.yaml` | ontology | goal 후보 | 목표 매핑 |
| `instances/device.yaml` | ontology | constraint 기반 후보 장비 | feasibility filter |
| `instances/model.yaml` | ontology | 모델 추천/메모리 적합도 | capability scoring |
| `instances/framework.yaml` | ontology | framework 추천 | stack composition |
| `instances/api_service.yaml` | ontology | API↔local 비교 | transition analysis |
| `instances/component.yaml` | ontology | PC build 조합 | component recommendation |
| `instances/repo.yaml` | ontology | 설치/quickstart 연결 | actionable output |
| `instances/setup_profile.yaml` | ontology | curated 추천안 | option synthesis |
| `instances/cost_estimation.yaml` | ontology | 월간 비용/전환 시점 | economic reasoning |
| `instances/relation.yaml` | ontology | 경로/호환/업그레이드 | path reasoning |
| `governance/schema.json` | copilot | 구조 검증 | contract boundary |
| `governance/GOVERNANCE.md` | copilot | 의미 있는 필수/참조 계약 | projection safety rail |
| `skills/.../SKILL.md` | copilot | state machine / proposal 규칙 | runtime behavior |

---

## 4. Runtime state ↔ ontology projection

`agent-setup-copilot`은 상태기계 기반이므로, projection contract는 상태별 입력/출력 책임을 명시해야 한다.

## 4.1 DETECT

입력:
- 사용자 첫 발화

출력:
- `user_archetype`: Explorer / Optimizer / Builder / Decider
- `answer_style`: simple / standard / technical
- `goal_hypothesis`: ontology `use_case.id` 후보 1~3개
- `deployment_target_hypothesis`: local / aws / runpod / azure / undecided

projection 규칙:
- 자연어 키워드 → `instances/use_case.yaml.keywords` 매핑
- 장비 언급 → `instances/device.yaml.id` 후보 추출
- 클라우드 키워드 → deployment target 추론

### Projection primitive

```json
{
  "goal_candidates": ["web_automation", "coding_assistant"],
  "constraint_candidates": ["mac_mini_m4_32gb"],
  "deployment_target": "local",
  "answer_style": "simple"
}
```

---

## 4.2 INTAKE

목표:
사용자 슬롯을 ontology-friendly 구조로 정규화한다.

필수 슬롯:
- `goal`
- `constraint`
- `tech_level`
- `success`
- `deployment_target`

projection 규칙:

### goal
- 사용자 의도 → `use_case.id`
- 하나로 확정 안 되면 primary + secondary 후보 유지 가능

예:
- “OpenClaw 돌리고 싶다” → `web_automation`
- “코드 도와주는 로컬 에이전트” → `coding_assistant` 또는 인접 use_case 후보

### constraint
constraint는 ontology 질의에 바로 넣을 수 있게 canonicalized 해야 한다.

구조:

```json
{
  "device": "mac_mini_m4_32gb",
  "budget": null,
  "hard": ["always_on"],
  "soft": ["prefer_simple_setup"]
}
```

### tech_level
ontology 직접 필드는 아니지만 proposal tone과 complexity 허용 범위를 제어한다.

매핑 원칙:
- beginner → low complexity profile 우선
- intermediate → medium 허용
- advanced → high complexity 허용

### success
추천 출력의 기준 함수로 사용.

예:
- “오늘 바로 시작” → installability 우선
- “장기적으로 최고 성능” → performance 우선
- “월 비용 줄이기” → transition/cost 우선

---

## 4.3 GATE

GATE는 ontology를 직접 호출하지 않지만,
projection completeness를 검증하는 내부 관문이다.

GATE 진입 기준:
- `goal` 확보
- `constraint` 확보

Projection contract 관점에서의 의미:
- 추천 엔진이 최소한 어떤 `use_case`를 최적화해야 하는지 알아야 함
- feasibility filter가 어떤 장비/예산 제약 위에서 돌아야 하는지 알아야 함

---

## 4.4 PROPOSE

여기가 projection의 핵심이다.

ontology → recommendation surface 변환이 여기서 일어난다.

### Step 1. Candidate set construction

입력:
- goal
- constraint
- deployment_target
- tech_level
- success

사용 ontology:
- use_case
- device
- model
- framework
- component
- api_service
- repo
- setup_profile
- relation
- cost_estimation

출력:

```json
{
  "candidate_devices": ["mac_mini_m4_32gb", "mac_studio_m4_max_64gb"],
  "candidate_models": ["qwen3.5:9b", "qwen3.5:35b-a3b"],
  "candidate_frameworks": ["openclaw", "smolagents"],
  "candidate_profiles": ["setup-mac-mini-openclaw"]
}
```

### Step 2. Constraint filtering

hard constraint 위반 항목 제거.

예:
- `needs_always_on = true` 인데 portable-only device 추천 금지
- `budget < threshold` 인데 해당 장비군 제외
- `negative = docker` 인데 docker 필수 repo/setup 제외
- `deployment_target = local` 인데 cloud-only 경로 제외

### Step 3. Scoring

추천 점수는 ontology value + runtime intent를 결합해서 계산한다.

권장 score 관점:

```text
score(option) =
  goal_fit
+ constraint_fit
+ complexity_fit
+ cost_fit
+ deployment_fit
+ profile_bonus
- hard_violation(inf)
- soft_penalty
```

설명:
- `goal_fit`: use_case와의 적합도
- `constraint_fit`: 메모리/always_on/privacy/budget 부합도
- `complexity_fit`: tech_level과 complexity의 정렬도
- `cost_fit`: success가 cost 절감일 때 중요
- `deployment_fit`: local/aws/runpod/azure 목표와의 정렬
- `profile_bonus`: curated setup_profile이 있을 때 가산점

### Step 4. Option synthesis

최종 출력은 단일 엔티티 추천이 아니라 **작동 가능한 조합**이어야 한다.

옵션 단위:

```json
{
  "device": "mac_mini_m4_32gb",
  "model": "qwen3.5:35b-a3b",
  "framework": "openclaw",
  "repo": "repo-openclaw",
  "setup_profile": "setup-mac-mini-openclaw",
  "why": [
    "always-on 조건 충족",
    "web_automation use_case 적합",
    "32GB에서 가장 균형 좋은 모델"
  ],
  "excluded": [
    "qwen3.5:72b - 메모리 제약으로 제외"
  ]
}
```

---

## 5. Entity-specific projection rules

## 5.1 use_case → goal primitive

`use_case`는 copilot에서 가장 중요한 projection anchor다.

역할:
- 사용자 목표를 ontology space에 투영하는 기준
- recommended_models / recommended_frameworks의 출발점

규칙:
- user intent는 반드시 하나 이상의 `use_case.id`로 normalize 시도
- 모호할 경우 `goal_candidates[]` 유지 후 PROPOSE에서 축소
- copilot state machine의 `goal` 슬롯은 자유 텍스트가 아니라 가능한 한 `use_case.id`를 가져야 함

---

## 5.2 device / component → feasibility primitive

역할:
- 지금 가진 장비로 가능한지
- 뭘 사야 되는지
- custom PC면 component 조합이 필요한지

규칙:
- 보유 장비가 있으면 `device.id` direct match 우선
- PC build intent면 `component`를 조합 후보로 사용
- `device.max_model`은 상한선 추정의 핵심 primitive
- `memory_gb`, `gpu_vram_gb`, `tier`, `always_on`, `portability`는 제약 필터 핵심

---

## 5.3 model → capability primitive

역할:
- 품질 수준
- tool calling 가능 여부
- 최소 메모리 요구량
- local alternative 매핑

규칙:
- `recommended_models`가 있으면 우선 후보
- `device.max_model`을 넘는 모델은 기본 제외
- `quality`, `tool_calling`, `min_memory_gb`는 핵심 gating field
- `sweet_spot` 같은 선택 속성이 있으면 동급 후보 중 선호 점수에 반영 가능

---

## 5.4 framework / repo → actionability primitive

역할:
- 추천이 실제 설치/실행 가능한 경로가 되게 함

규칙:
- framework는 추상 추천이 아니라 repo와 함께 제시하는 것을 기본으로 함
- framework 단독 추천보다 `framework + repo + install + quickstart` 조합을 우선
- `local_capable`, `runtime_support`, `complexity`, `best_for`가 선택 핵심

---

## 5.5 setup_profile → curated recommendation primitive

역할:
- 이미 검증된 조합을 상위 레벨 추천 옵션으로 승격

규칙:
- 가능한 경우 device/model/framework/repo를 즉석 조합하기보다 `setup_profile` 우선
- profile이 있으면 추천 이유 설명이 쉬워지고 설치 단계도 바로 제시 가능
- multi-device role mapping은 setup_profile이 최적 관리 지점

즉,
- atomic entities = 추천 재료
- setup_profile = 추천 완성품

---

## 5.6 api_service / cost_estimation → transition primitive

역할:
- cloud API와 local 전환 판단
- break-even month 계산
- usage growth 반영

규칙:
- Optimizer 유형에서는 반드시 우선적으로 고려
- `monthly_cost_usd`가 있으면 transition 계산 직접 연결
- `local_alternative`는 API ↔ local bridge field
- `cost_estimation`은 proposal의 숫자 근거를 제공

---

## 5.7 relation → path reasoning primitive

역할:
- upgrade path
- local_alternative path
- framework ↔ use_case ↔ setup_profile 연결
- exclusion / compatibility / migration reasoning

규칙:
- relation은 단순 참고가 아니라 DEO resolver의 path graph 입력으로 취급
- negative constraint가 있는 경우 relation graph에서 허용 경로만 통과
- reasoning trace는 relation path 기반으로 생성 가능해야 함

---

## 6. Projection contract outputs

projection layer는 copilot runtime에 최소 아래 구조를 안정적으로 제공해야 한다.

```json
{
  "intake_normalized": {
    "goal": "web_automation",
    "constraint": {
      "device": "mac_mini_m4_32gb",
      "hard": ["always_on"],
      "soft": ["prefer_simple_setup"]
    },
    "tech_level": "beginner",
    "success": "start_today",
    "deployment_target": "local"
  },
  "candidates": {
    "devices": ["mac_mini_m4_32gb"],
    "models": ["qwen3.5:9b", "qwen3.5:35b-a3b"],
    "frameworks": ["openclaw"],
    "repos": ["repo-openclaw"],
    "setup_profiles": ["setup-mac-mini-openclaw"]
  },
  "recommendations": [
    {
      "rank": 1,
      "setup_profile": "setup-mac-mini-openclaw",
      "score": 0.93,
      "why": [
        "goal 적합도 높음",
        "always-on 적합",
        "설치 난이도 낮음"
      ],
      "excluded": [
        "고사양 PC 빌드 - 예산/복잡도 과다"
      ]
    }
  ]
}
```

---

## 7. Governance safety rules for projection

### G1. Consumer contract wins
ontology에 값이 있어도 governance에 없는 구조는 copilot이 신뢰하지 않는다.

### G2. Projection must be validation-clean
projection 대상으로 쓰이는 ontology snapshot은 반드시 `governance/scripts/validate.py` 통과 상태여야 한다.

### G3. No silent semantic widening
새 field를 ontology에 넣었다고 copilot이 자동으로 의미를 확장하면 안 된다.
새 의미를 쓰려면 governance + skill 쪽 변경이 먼저다.

### G4. Explanation must cite constraints
copilot 추천은 항상 다음 3가지를 설명 가능해야 한다.
- 왜 선택됐는가
- 왜 제외됐는가
- 어떤 constraint가 영향을 줬는가

### G5. setup_profile preferred over ad-hoc composition
동등한 품질이면 curated profile을 우선한다.

---

## 8. Immediate implementation plan

### Phase A — projection contract 확정
- 이 문서를 기반으로 consumer/ontology 책임 분리 확정
- 누가 어떤 파일을 소유하는지 고정

### Phase B — loader output 정규화
`loader.py`가 copilot에서 바로 쓰기 좋은 통합 JSON shape를 제공하도록 점검

권장 shape:
- `concepts`
- `instances`
- `indexes.by_id`
- `indexes.by_use_case`
- `indexes.by_framework`
- `relations.graph`

### Phase C — state machine binding table 작성
SKILL.md의 상태 슬롯들이 ontology 필드와 어떻게 연결되는지 표준화

### Phase D — rationale template 추가
추천/비추천/대안 설명 템플릿을 relation + constraint 기반으로 일관화

### Phase E — validation in projection path
copilot 실행 전에 ontology snapshot validation 여부를 확인하거나,
loader에서 schema mismatch를 경고하도록 개선

---

## 9. Short conclusion

이 계약의 핵심은 단순하다.

- **governance는 copilot이 소유한다**
- **ontology는 데이터 SoT다**
- **projection은 ontology를 copilot state machine의 판단면으로 변환하는 번역 규칙이다**

따라서 앞으로의 설계 방향은:

> ontology를 더 많이 쌓는 것보다,
> copilot이 그 ontology를 어떻게 안정적으로 읽고 추천으로 바꾸는지
> projection contract를 선명하게 만드는 데 있다.
