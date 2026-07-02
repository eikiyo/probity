# Probity — Benchmark Results

**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a human-validated answer extracted from the source document. They are reported separately and never averaged — a model can be perfectly consistent and consistently wrong.

Models span a size ladder (1B → 12B local + a hosted model) to test whether wobble falls as capability rises. Local via Ollama (zero egress); hosted = deepseek-v4-flash.

---

## Test 1.3.2 — Preferred-stock liquidation participation

**Corpus:** 18 real SEC-filed charter clauses, human-validated answers (6 part / 7 non-part / 5 capped). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **72%** | 89% | 33% | 18/18 | 312/360 (87%) |
| `deepseek-v4-flash` | hosted | **11%** | 98% | 67% | 18/18 | 342/360 (95%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **non-part · part · capped** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | part | non-part | capped |
|---|---|---|---|
| `gemma3:1b` | 0/6 | 6/7 | 0/5 |
| `deepseek-v4-flash` | 1/6 | 6/7 | 5/5 |
| `google/gemma-4-31b-it` | 2/6 | 6/7 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| EndoStim, Inc. | non-participating | medium | 1B |
| Pfenex Inc. | participating | hard | 1B |
| Sonos Inc | non-participating | easy | 1B |
| Enservco Corp | non-participating | easy | 1B |
| BioAccelerate Holdings | non-participating | hard | 1B |
| Entercom Communication | non-participating | hard | 1B |
| scPharmaceuticals Inc. | participating | medium | 1B |
| Akouos, Inc. | participating | medium | 1B |
| Jazz Semiconductor Inc | capped | medium | hosted |
| The Medicines Co (Remp | capped | medium | 1B |
| Fitbit Inc | capped | hard | 1B |
| Workday, Inc. | capped | medium | 1B |
| Entellus Medical Inc | participating | easy | 1B, hosted |
| Internet Security Syst | participating | easy | 1B |

## What this shows

- **Participating preferred is the universal blind spot.** Even the best models get only 1-2 of 5
  participating clauses right; the small models get 0. The "preference AND THEN also share with the
  common" structure is systematically misread as capped or non-participating.
- **Small models can't classify the hard classes at all** (1B: 0/5 participating, 0/5 capped) -
  they collapse everything to non-participating.

---

## Test 2.1.4 — SAFE valuation cap: pre-money vs post-money

**Corpus:** 16 real SEC-filed YC SAFE provisions, human-validated answers (10 post / 6 pre). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **6%** | 99% | 62% | 16/16 | 189/320 (59%) |
| `deepseek-v4-flash` | hosted | **19%** | 99% | 100% | 16/16 | 320/320 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **post · pre** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | post | pre |
|---|---|---|
| `gemma3:1b` | 10/10 | 0/6 |
| `deepseek-v4-flash` | 10/10 | 6/6 |
| `google/gemma-4-31b-it` | 10/10 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Neo Aeronautics, Inc.  | pre-money | easy | hosted |
| Rentberry Inc.  (CIK 0 | pre-money | easy | hosted |
| Complete Solaria, Inc. | pre-money | easy | hosted |
| IDEANOMICS, INC.  (IDE | pre-money | easy | 1B |

## What this shows

- **Accuracy does not imply trustworthiness — the cleanest case yet.** deepseek-v4-flash answers
  every one of the 16 SAFEs correctly (100% accuracy) yet still **wobbles on 19% of them** across 20
  identical runs. A model you would call "100% accurate" from a single pass changes its answer on
  ~1 in 5 items when you actually repeat the question. Wobble catches what an accuracy score hides.
- **Low wobble can mask low accuracy.** gemma3:1b looks stable (6% wobble) but is only 62% accurate -
  it confidently and *repeatably* gives the wrong pre/post classification. Consistency without
  accuracy is its own trap; this is why the two numbers are never averaged.

---

## Test 1.4.2 — Preferred dividends: cumulative vs non-cumulative

**Corpus:** 16 real SEC-filed preferred-stock charter dividend clauses, human-validated answers (8 cumulative / 8 non-cum). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 88% | 16/16 | 320/320 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 14/16 | 186/320 (58%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **cumulative · non-cum** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | cumulative | non-cum |
|---|---|---|
| `gemma3:1b` | 7/8 | 7/8 |
| `deepseek-v4-flash` | 8/8 | 8/8 |
| `google/gemma-4-31b-it` | 8/8 | 8/8 |
| `mistralai/mistral-large-2512` | 8/8 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ENTERCOM COMMUNICATION | cumulative | easy | 1B |
| BIOACCELERATE HOLDINGS | cumulative | easy | 1B |
| FS Credit Opportunitie | cumulative | hard | 1B |
| IMPEL NEUROPHARMA INC | non-cumulative | easy | 1B |
| Teladoc, Inc. | non-cumulative | easy | 1B |
| Akouos, Inc. | non-cumulative | medium | mistral-large-or |
| Eiger BioPharmaceutica | non-cumulative | medium | 1B, mistral-large-or |
| scPharmaceuticals Inc. | non-cumulative | easy | 1B |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger

**Corpus:** 13 real SEC-filed equity-award / employment agreements, human-validated answers (6 single / 7 double). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 97% | 85% | 13/13 | 259/260 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 10/13 | 163/260 (63%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **single · double** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | single | double |
|---|---|---|
| `gemma3:1b` | 4/6 | 7/7 |
| `deepseek-v4-flash` | 6/6 | 7/7 |
| `google/gemma-4-31b-it` | 6/6 | 7/7 |
| `mistralai/mistral-large-2512` | 4/4 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GIBRALTAR INDUSTRIES,  | double-trigger | hard | 1B |
| Vulcan Materials CO | double-trigger | hard | 1B, mistral-large-or |
| Nimble Storage Inc | single-trigger | medium | 1B |
| LogicMark, Inc. | single-trigger | easy | 1B, mistral-large-or |
| COMSCORE, INC. | single-trigger | hard | 1B |
| REVVITY, INC. | single-trigger | easy | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–46% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked

**Corpus:** 11 real SEC-filed multi-series preferred charters, human-validated answers (6 pari-passu / 5 stacked). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **45%** | 97% | 45% | 11/11 | 215/220 (98%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 75% | 8/11 | 116/220 (53%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pari-passu · stacked** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pari-passu | stacked |
|---|---|---|
| `gemma3:1b` | 0/6 | 5/5 |
| `deepseek-v4-flash` | 4/6 | 5/5 |
| `google/gemma-4-31b-it` | 4/6 | 5/5 |
| `mistralai/mistral-large-2512` | 3/5 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| IESI CORP | stacked | medium | mistral-large-or |
| Banks.com, Inc. | stacked | medium | 1B |
| Teladoc, Inc. | stacked | easy | 1B |
| AMERICAN POWER GROUP C | stacked | easy | mistral-large-or |
| VioQuest Pharmaceutica | pari-passu | easy | 1B |
| RIGHT START INC /CA | pari-passu | medium | 1B |
| PRECOM TECHNOLOGY INC | pari-passu | hard | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–45% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 82% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.1 — Risk flag: off-market liquidation preference (>1x)

**Corpus:** 10 real SEC-filed preferred-stock liquidation clauses, human-validated answers (5 off-market(>1x) / 5 standard(1x)). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 95% | 40% | 10/10 | 197/200 (98%) |
| `deepseek-v4-flash` | hosted | **10%** | 99% | 90% | 10/10 | 200/200 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 88% | 8/10 | 110/200 (55%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **off-market(>1x) · standard(1x)** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | off-market(>1x) | standard(1x) |
|---|---|---|
| `gemma3:1b` | 3/5 | 1/5 |
| `deepseek-v4-flash` | 5/5 | 4/5 |
| `google/gemma-4-31b-it` | 5/5 | 5/5 |
| `mistralai/mistral-large-2512` | 5/5 | 2/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MELINTA THERAPEUTICS,  | yes | easy | 1B |
| Lulu's Fashion Lounge  | yes | hard | 1B |
| Akouos, Inc. | no | easy | mistral-large-or |
| Workday, Inc. | no | hard | 1B, hosted |
| ENDOSTIM, INC. | no | easy | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.7 — Redemption rights: redeemable vs non-redeemable

**Corpus:** 10 real SEC-filed preferred-stock charter redemption clauses, human-validated answers (5 redeemable / 5 non-redeem). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 97% | 50% | 10/10 | 200/200 (100%) |
| `deepseek-v4-flash` | hosted | **10%** | 96% | 100% | 10/10 | 200/200 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 10/10 | 116/200 (58%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **redeemable · non-redeem** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | redeemable | non-redeem |
|---|---|---|
| `gemma3:1b` | 0/5 | 5/5 |
| `deepseek-v4-flash` | 5/5 | 5/5 |
| `google/gemma-4-31b-it` | 5/5 | 5/5 |
| `mistralai/mistral-large-2512` | 5/5 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Lulu's Fashion Lounge  | yes | medium | 1B |
| Tenable Holdings, Inc. | yes | medium | 1B |
| Pfenex Inc. | yes | hard | hosted |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

---

## Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)

**Corpus:** 12 real SEC-filed stockholder/transfer agreements, human-validated answers (6 drag(obligated) / 6 co-sale(right)). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 99% | 42% | 12/12 | 238/240 (99%) |
| `deepseek-v4-flash` | hosted | **8%** | 97% | 100% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 91% | 11/12 | 144/240 (60%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **drag(obligated) · co-sale(right)** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | drag(obligated) | co-sale(right) |
|---|---|---|
| `gemma3:1b` | 4/6 | 1/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |
| `google/gemma-4-31b-it` | 6/6 | 6/6 |
| `mistralai/mistral-large-2512` | 5/6 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| TRUMP ENTERTAINMENT RE | yes | easy | 1B, hosted |
| LOEWS CINEPLEX ENTERTA | yes | medium | 1B |
| ACCELERON PHARMA INC | no | easy | mistral-large-or |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

---

## Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent

**Corpus:** 12 real SEC-filed stockholder/transfer documents, human-validated answers (6 rofr/cosale / 6 absent/other-right). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 98% | 67% | 12/12 | 238/240 (99%) |
| `deepseek-v4-flash` | hosted | **17%** | 94% | 92% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **rofr/cosale · absent/other-right** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | rofr/cosale | absent/other-right |
|---|---|---|
| `gemma3:1b` | 6/6 | 2/6 |
| `deepseek-v4-flash` | 6/6 | 5/6 |
| `google/gemma-4-31b-it` | 6/6 | 4/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MotivNation | no | hard | 1B, hosted |
| EntreMetrix | no | hard | 1B, hosted |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 83% accuracy).

---

## Test 5.4 — Pro-rata right on future financings: granted vs not

**Corpus:** 12 real SEC-filed SAFEs, side letters and investors' rights agreements, human-validated answers (6 pro-rata / 6 absent/waived). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 96% | 100% | 12/12 | 165/240 (69%) |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **8%** | 96% | 100% | 11/12 | 152/240 (63%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pro-rata · absent/waived** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pro-rata | absent/waived |
|---|---|---|
| `gemma3:1b` | 6/6 | 6/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |
| `google/gemma-4-31b-it` | 6/6 | 6/6 |
| `mistralai/mistral-large-2512` | 6/6 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SOS Hydration Inc. | yes | medium | 1B, hosted |
| Cantabio Pharmaceutica | yes | medium | mistral-large-or |
| Hoku Scientific, Inc. | no | easy | mistral-large-or |
| Infinity Pharmaceutica | no | easy | 1B |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

---

## Test 6.2 — Vesting schedule: cliff present vs absent

**Corpus:** 12 real SEC-filed equity-award agreements and disclosures, human-validated answers (6 cliff / 6 no-cliff). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 96% | 67% | 12/12 | 239/240 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 11/12 | 157/240 (65%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **cliff · no-cliff** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | cliff | no-cliff |
|---|---|---|
| `gemma3:1b` | 6/6 | 2/6 |
| `deepseek-v4-flash` | 6/6 | 5/6 |
| `google/gemma-4-31b-it` | 6/6 | 6/6 |
| `mistralai/mistral-large-2512` | 5/5 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Interval Leisure Group | yes | medium | 1B, mistral-large-or |
| World Heart Corp | no | hard | 1B |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

---

## Test 5.2 — Protective provisions: investor class-veto right present vs absent

**Corpus:** 12 real SEC-filed charters and governance documents, human-validated answers (6 veto-right / 6 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 97% | 58% | 12/12 | 239/240 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 11/12 | 155/240 (65%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **veto-right · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | veto-right | absent |
|---|---|---|
| `gemma3:1b` | 6/6 | 1/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |
| `google/gemma-4-31b-it` | 5/6 | 6/6 |
| `mistralai/mistral-large-2512` | 6/6 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SCYNEXIS, Inc. | yes | medium | 1B |
| Non-binding LOI (Omni  | no | easy | 1B |
| Trident Bancshares, In | no | easy | mistral-large-or |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 5.3 — Information rights: live financial-reporting obligation vs absent

**Corpus:** 12 real SEC-filed investors' rights agreements and equity-award docs, human-validated answers (6 info-rights / 6 absent/waived). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 95% | 50% | 12/12 | 233/240 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **8%** | 98% | 92% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 90% | 10/12 | 132/240 (55%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **info-rights · absent/waived** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | info-rights | absent/waived |
|---|---|---|
| `gemma3:1b` | 6/6 | 0/6 |
| `deepseek-v4-flash` | 5/6 | 6/6 |
| `google/gemma-4-31b-it` | 5/6 | 6/6 |
| `mistralai/mistral-large-2512` | 4/5 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Vocera Communications, | yes | easy | mistral-large-or |
| Bell Microproducts Inc | yes | hard | gemma4-31b-or |
| Speedway Motorsports,  | no | easy | 1B |
| Pool Corp | no | easy | 1B |
| Restore Medical Inc. | no | hard | mistral-large-or |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 92% accuracy).

---

## Test 5.7 — Vesting acceleration: granted on trigger vs absent

**Corpus:** 9 real SEC-filed equity-award agreements and proxy disclosures, human-validated answers (6 accelerates / 3 no-acceleration). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 67% | 9/9 | 174/180 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **accelerates · no-acceleration** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | accelerates | no-acceleration |
|---|---|---|
| `gemma3:1b` | 4/6 | 2/3 |
| `deepseek-v4-flash` | 6/6 | 3/3 |
| `google/gemma-4-31b-it` | 6/6 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GIBRALTAR INDUSTRIES,  | yes | easy | 1B |
| Silverback Therapeutic | yes | easy | 1B |
| CASTLIGHT HEALTH, INC. | yes | medium | 1B |
| YELP INC | no | easy | 1B |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.3.1 — Liquidation preference multiple: 1x vs 2x vs 3x vs other

**Corpus:** 9 real SEC-filed preferred-stock liquidation preference clauses, human-validated answers (0 non-part / 3 1x / 3 2x / 3 3x / 0 other). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **56%** | 94% | 0% | 9/9 | 144/180 (80%) |
| `deepseek-v4-flash` | hosted | **33%** | 92% | 67% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **11%** | 94% | 67% | 9/9 | 117/180 (65%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **non-part · 1x · 2x · 3x · other** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | non-part | 1x | 2x | 3x | other |
|---|---|---|---|---|---|
| `gemma3:1b` | — | 0/3 | 0/3 | 0/3 | — |
| `deepseek-v4-flash` | — | 2/3 | 1/3 | 3/3 | — |
| `google/gemma-4-31b-it` | — | 2/3 | 1/3 | 3/3 | — |
| `mistralai/mistral-large-2512` | — | 2/3 | 1/3 | 3/3 | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| COUNTERPATH CORP  (CIK | 1x | easy | 1B |
| Revance Therapeutics,  | 1x | easy | 1B |
| Oportun Financial Corp | 2x | easy | 1B, hosted, mistral-large-or |
| Pagaya Technologies Lt | 2x | easy | 1B, hosted |
| BECEEM COMMUNICATIONS  | 3x | easy | 1B |
| CASTLE BIOSCIENCES INC | 3x | easy | hosted |

## What this shows

- **Wobble spread: 0%–56% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 67% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 5.1 — Board seats: number an investor has the right to designate

**Corpus:** 9 real SEC-filed voting/shareholders'/designation agreements, human-validated answers (values range 1-9). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 92% | 78% | 9/9 | 176/180 (98%) |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 78% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **33%** | 94% | 67% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **11%** | 99% | 43% | 7/9 | 108/180 (60%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SICOR Inc. | 3 | easy | 1B |
| Dollar General Corpora | 1 | medium | 1B |
| Ute Energy Corporation | 1 | medium | 1B, gemma4-31b-or |
| Ute Energy Corporation | 2 | medium | 1B, gemma4-31b-or, mistral-large-or |
| Cinemark Holdings, Inc | 5 | easy | gemma4-31b-or, mistral-large-or |
| Cinemark Holdings, Inc | 9 | hard | hosted |
| Eleison Pharmaceutical | 1 | easy | mistral-large-or |

## What this shows

- **Wobble spread: 11%–44% across the ladder.** Lowest-wobble model: **hosted** (11% wobble, 78% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.6 — SAFE pro-rata side letter: granted vs absent

**Corpus:** 15 real SEC-filed SAFEs and pro-rata side letters, human-validated answers (9 pro-rata / 6 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 97% | 93% | 15/15 | 217/300 (72%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pro-rata · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pro-rata | absent |
|---|---|---|
| `gemma3:1b` | 9/9 | 5/6 |
| `deepseek-v4-flash` | 9/9 | 6/6 |
| `google/gemma-4-31b-it` | 9/9 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SNM Global Holdings, I | yes | easy | 1B |
| SOS Hydration Inc. | yes | hard | 1B |
| TaoWeave, Inc. | no | hard | 1B |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 1.1.2 — Priced round basis: pre-money vs post-money

**Corpus:** 19 real SEC-filed priced-round financing documents, human-validated answers (13 pre / 6 post). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 83% | 68% | 19/19 | 363/380 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pre · post** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pre | post |
|---|---|---|
| `gemma3:1b` | 7/13 | 6/6 |
| `deepseek-v4-flash` | 13/13 | 5/6 |
| `google/gemma-4-31b-it` | 13/13 | 5/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Viking Therapeutics, I | pre-money | easy | 1B |
| Rules-Based Medicine I | pre-money | easy | 1B |
| SUNESIS PHARMACEUTICAL | pre-money | easy | 1B |
| RMG Acquisition Corp.  | pre-money | easy | 1B |
| Ucommune Group Holding | pre-money | easy | 1B |
| VIEWRAY INC | pre-money | easy | 1B |
| Cytosorbents Corp | pre-money | medium | 1B |
| GreenCell, Inc | pre-money | medium | 1B |
| BIOLARGO, INC. | pre-money | medium | 1B |
| Cytosorbents Corp | pre-money | medium | 1B |
| HAGUE CORP. | pre-money | easy | 1B |
| SOCIETY PASS INCORPORA | pre-money | easy | 1B |
| HAGUE CORP. | pre-money | easy | 1B |
| PROVECTUS BIOPHARMACEU | post-money | easy | 1B |
| Fold Holdings, Inc. | post-money | easy | 1B |
| New Global Energy, Inc | post-money | easy | 1B |
| Cerebras Systems Inc. | post-money | medium | 1B |
| Oculus Innovative Scie | post-money | medium | 1B |
| Oculus Innovative Scie | post-money | medium | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 95% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.2 — Risk flag: full-ratchet anti-dilution present vs absent

**Corpus:** 7 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (4 full-ratchet / 3 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 98% | 57% | 7/7 | 130/140 (93%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 6/7 | 78/140 (56%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **full-ratchet · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | full-ratchet | absent |
|---|---|---|
| `gemma3:1b` | 4/4 | 0/3 |
| `deepseek-v4-flash` | 4/4 | 3/3 |
| `google/gemma-4-31b-it` | 4/4 | 3/3 |
| `mistralai/mistral-large-2512` | 3/3 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CROSSROADS SYSTEMS INC | yes | medium | mistral-large-or |
| ZIX CORP | no | easy | 1B |
| VISIUM TECHNOLOGIES, I | no | medium | 1B |

## What this shows

- **Wobble spread: 0%–29% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 1.1.1 — Post-money valuation extraction

**Corpus:** 4 real SEC-filed priced-round financing documents, human-validated answers (values range 5000000-275000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 25% | 4/4 | 60/80 (75%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/4 | 52/80 (65%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| XTI Aerospace, Inc. | 275000000 | medium | mistral-large-or |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none

**Corpus:** 5 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (2 full-ratchet / 2 weighted-avg / 0 broad-based / 0 narrow-based / 1 none). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 99% | 40% | 5/5 | 98/100 (98%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 76/100 (76%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **full-ratchet · weighted-avg · broad-based · narrow-based · none** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | full-ratchet | weighted-avg | broad-based | narrow-based | none |
|---|---|---|---|---|---|
| `gemma3:1b` | 2/2 | 0/2 | — | — | 0/1 |
| `deepseek-v4-flash` | 2/2 | 2/2 | — | — | 1/1 |
| `google/gemma-4-31b-it` | 2/2 | 2/2 | — | — | 1/1 |
| `mistralai/mistral-large-2512` | 2/2 | 2/2 | — | — | 1/1 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CROSSROADS SYSTEMS INC | full-ratchet | medium | 1B |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 8.3 — Risk flag: uncapped participating-preferred present vs absent

**Corpus:** 13 real SEC-filed preferred-stock liquidation/participation clauses, human-validated answers (4 uncapped / 9 capped/none). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **8%** | 99% | 31% | 13/13 | 195/260 (75%) |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 77% | 13/13 | 260/260 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 82% | 11/13 | 147/260 (57%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **uncapped · capped/none** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | uncapped | capped/none |
|---|---|---|
| `gemma3:1b` | 4/4 | 0/9 |
| `deepseek-v4-flash` | 2/4 | 9/9 |
| `google/gemma-4-31b-it` | 2/4 | 8/9 |
| `mistralai/mistral-large-2512` | 2/4 | 7/7 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| The Medicines Co (Remp | no | medium | mistral-large-or |
| Jazz Semiconductor Inc | no | medium | hosted |
| Workday, Inc. | no | medium | 1B |
| BioAccelerate Holdings | no | hard | mistral-large-or |

## What this shows

- **Wobble spread: 0%–8% across the ladder.** Lowest-wobble model: **mistral-large-or** (0% wobble, 82% accuracy).

---

## Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent

**Corpus:** 7 real SEC-filed SAFE agreements, human-validated answers (4 MFN / 3 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 97% | 100% | 7/7 | 124/140 (89%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **MFN · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | MFN | absent |
|---|---|---|
| `gemma3:1b` | 4/4 | 3/3 |
| `deepseek-v4-flash` | 4/4 | 3/3 |
| `google/gemma-4-31b-it` | 4/4 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| THC Therapeutics, Inc. | yes | easy | 1B |
| CEMTREX INC | yes | easy | 1B |

## What this shows

- **Wobble spread: 0%–29% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 1.3.3 — Participation cap multiple extraction

**Corpus:** 3 real SEC-filed capped-participating-preferred liquidation clauses, human-validated answers (values range 3-3.5). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 3/3 | 58/60 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/3 | 44/60 (73%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 6.4 — Stock option exercise (strike) price extraction

**Corpus:** 7 real SEC-filed stock option grant agreements, human-validated answers (values range 0.03-11.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 86% | 71% | 7/7 | 133/140 (95%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 7/7 | 80/140 (57%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Medecision, Inc. | 1.25 | medium | 1B |
| Medecision, Inc. | 2.0 | medium | 1B |

## What this shows

- **Wobble spread: 0%–29% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 2.1.1 — SAFE valuation cap extraction

**Corpus:** 8 real SEC-filed SAFE agreements, human-validated answers (values range 15000000-150000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 96% | 88% | 8/8 | 144/160 (90%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Lomond Therapeutics Ho | 100000000 | medium | 1B |
| Invizyne Technologies  | 100000000 | hard | 1B |
| PaxMedica, Inc. | 150000000 | hard | 1B |

## What this shows

- **Wobble spread: 0%–38% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.1 — Convertible note principal amount extraction

**Corpus:** 7 real SEC-filed convertible promissory notes, human-validated answers (values range 12500-17364375). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 7/7 | 138/140 (99%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 6/7 | 84/140 (60%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MINERCO, INC. (Rios) | 100000 | medium | mistral-large-or |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 2.1.2 — SAFE discount rate extraction

**Corpus:** 9 real SEC-filed SAFE agreements, human-validated answers (values range 10-50). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 89% | 56% | 9/9 | 160/180 (89%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Complete Solaria, Inc. | 20 | easy | 1B |
| Maison Luxe, Inc. | 20 | easy | 1B |
| Parker Clay Global, PB | 15 | medium | 1B |
| SOS Hydration Inc. | 50 | hard | 1B |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.4 — Convertible note valuation cap extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 25000000-125000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 91% | 75% | 4/4 | 72/80 (90%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/4 | 28/80 (35%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Damon Motors Inc. | 125000000 | easy | 1B, mistral-large-or |
| Greenfield Robotics Co | 30000000 | easy | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.6.1 — Preferred-stock conversion ratio extraction

**Corpus:** 5 real SEC-filed preferred-stock charters, human-validated answers (values range 1-8000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 92% | 80% | 5/5 | 99/100 (99%) |
| `deepseek-v4-flash` | hosted | **20%** | 98% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 74/100 (74%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Air Defense Services,  | 100 | medium | hosted |
| Boston Life Sciences,  | 8000 | hard | 1B |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

---

## Test 1.5.2 — Anti-dilution weighted-average base: broad-based vs narrow-based vs n/a

**Corpus:** 10 real SEC-filed preferred-stock charter anti-dilution clauses, human-validated answers (3 broad / 4 narrow / 3 n/a). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 96% | 70% | 10/10 | 199/200 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 9/10 | 124/200 (62%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **broad · narrow · n/a** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | broad | narrow | n/a |
|---|---|---|---|
| `gemma3:1b` | 3/3 | 4/4 | 0/3 |
| `deepseek-v4-flash` | 3/3 | 4/4 | 3/3 |
| `google/gemma-4-31b-it` | 3/3 | 4/4 | 3/3 |
| `mistralai/mistral-large-2512` | 3/3 | 3/3 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| YX Asset Recovery Ltd  | narrow-based | medium | mistral-large-or |
| Galecto Inc.  (GLTO)   | narrow-based | hard | 1B |
| CROSSROADS SYSTEMS INC | n/a | medium | 1B |
| YODLEE INC  (CIK 00011 | n/a | medium | 1B |
| POPULAR INC  (BPOP, BP | n/a | easy | 1B |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.6.2 — Automatic conversion (QPO) proceeds threshold extraction

**Corpus:** 5 real SEC-filed preferred-stock charter automatic-conversion clauses, human-validated answers (values range 30000000-100000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 68/100 (68%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 2.2.2 — Convertible note interest rate extraction

**Corpus:** 6 real SEC-filed convertible promissory notes, human-validated answers (values range 0.28-10.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 83% | 6/6 | 113/120 (94%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 6/6 | 62/120 (52%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)

**Corpus:** 13 real SEC-filed SAFE (Simple Agreement for Future Equity) instruments, human-validated answers (2 cap / 1 discount / 10 both-mfn). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 88% | 77% | 13/13 | 216/260 (83%) |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 13/13 | 221/260 (85%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **cap · discount · both-mfn** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | cap | discount | both-mfn |
|---|---|---|---|
| `gemma3:1b` | 2/2 | 0/1 | 8/10 |
| `deepseek-v4-flash` | 2/2 | 1/1 | 10/10 |
| `google/gemma-4-31b-it` | 2/2 | 1/1 | 10/10 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SNM Global Holdings, I | discount | easy | 1B |
| Parker Clay Global, PB | both-mfn | medium | 1B |
| Maison Luxe, Inc. | both-mfn | medium | 1B |
| Rentberry Inc. | both-mfn | medium | 1B |
| Creci Inc. | both-mfn | medium | 1B |
| Manako Labs Ltd | both-mfn | medium | hosted |
| Gardedam Therapeutics  | cap | medium | 1B |

## What this shows

- **Wobble spread: 0%–46% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.1.3 — Priced-round price-per-share extraction

**Corpus:** 8 real SEC-filed stock purchase agreements / charters / offerings, human-validated answers (values range 0.2-1000.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 92% | 62% | 8/8 | 156/160 (98%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 62% | 8/8 | 147/160 (92%) |
| `google/gemma-4-31b-it` | ? | **12%** | 96% | 75% | 8/8 | 160/160 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 57% | 7/8 | 100/160 (62%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Astea International In | 3.63 | easy | 1B |
| Kiwa Bio-Tech Products | 1.3 | medium | 1B, mistral-large-or |
| Gelesis, Inc. | 1.26 | medium | gemma4-31b-or |
| WhiteGlove Health, Inc | 0.2 | easy | 1B |

## What this shows

- **Wobble spread: 0%–38% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 62% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.3 — Convertible note maturity date extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 2005-03-31-2026-12-31). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 94% | 50% | 4/4 | 75/80 (94%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/4 | 52/80 (65%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GARDENBURGER, INC. | 2005-03-31 | easy | 1B |
| ACOLOGY, INC. | 2015-03-04 | medium | 1B, gemma4-31b-or |
| XTI Aerospace Inc. | 2026-12-31 | easy | mistral-large-or |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.5 — Convertible note conversion-discount rate extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 5.0-50.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **25%** | 92% | 0% | 3/4 | 58/80 (72%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/4 | 50/80 (62%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Exyn Technologies, Inc | 25.0 | easy | mistral-large-or |
| ACOLOGY, INC. | 50.0 | easy | 1B |
| HepaLife Technologies, | 5.0 | medium | 1B |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction

**Corpus:** 2 real SEC-filed convertible promissory notes, human-validated answers (values range 10000000-40000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 97% | 100% | 2/2 | 37/40 (92%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 1/2 | 18/40 (45%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Valkyrie Sciences Hold | 10000000 | medium | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.1 — Equity vesting schedule extraction + normalization

**Corpus:** 9 real SEC-filed equity-award / employment agreements, human-validated answers (values range 1.5yr/no-cliff-4yr/no-cliff). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 38% | 8/9 | 92/180 (51%) |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 100% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CONOR MEDSYSTEMS, INC. | 1.5yr/no-cliff | medium | 1B |
| CLARCOR INC. | 4yr/no-cliff | hard | hosted |

## What this shows

- **Wobble spread: 0%–11% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 89% accuracy).

---

## Test 3.1 — Cap-table current ownership percentage (compute)

**Corpus:** 9 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-33.9). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 16% | 0% | 9/9 | 146/180 (81%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 179/180 (99%) |
| `google/gemma-4-31b-it` | ? | **22%** | 97% | 100% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 7/9 | 110/180 (61%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | 1B |
| Uber Technologies, Inc | 11.0 | easy | 1B |
| Uber Technologies, Inc | 2.4 | medium | 1B |
| Uber Technologies, Inc | 8.6 | easy | 1B |
| Uber Technologies, Inc | 5.4 | medium | 1B, gemma4-31b-or |
| Uber Technologies, Inc | 16.3 | medium | 1B, mistral-large-or |
| Uber Technologies, Inc | 5.2 | medium | 1B |
| Uber Technologies, Inc | 5.3 | medium | 1B |
| Uber Technologies, Inc | 33.9 | hard | 1B, gemma4-31b-or, mistral-large-or |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.1 — Named founder's ownership percentage (compute)

**Corpus:** 3 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-8.6). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 18% | 0% | 3/3 | 60/60 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/3 | 32/60 (53%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | 1B |
| Uber Technologies, Inc | 8.6 | easy | 1B |
| Uber Technologies, Inc | 2.4 | medium | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.2 — Named institutional investor's ownership percentage (compute)

**Corpus:** 4 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 5.2-16.3). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 38% | 0% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 39/80 (49%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 16.3 | easy | 1B |
| Uber Technologies, Inc | 11.0 | easy | 1B |
| Uber Technologies, Inc | 5.3 | medium | 1B |
| Uber Technologies, Inc | 5.2 | medium | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.3 — Employee option pool size as % of total shares (compute)

**Corpus:** 1 real SEC-filed S-1 capitalization narrative, human-validated answers (values range 9.5-9.5). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 47% | 0% | 1/1 | 17/20 (85%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 0% | 0% | 0/1 | 0/20 (0%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 9.5 | easy | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.1 — Securities Act exemption classification

**Corpus:** 10 real SEC Form D filings (structured federalExemptionsExclusions field), human-validated answers (6 506(b) / 4 506(c) / 0 504 / 0 Reg A / 0 other). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 86% | 100% | 10/10 | 170/200 (85%) |
| `deepseek-v4-flash` | hosted | **30%** | 96% | 100% | 10/10 | 200/200 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **506(b) · 506(c) · 504 · Reg A · other** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | 506(b) | 506(c) | 504 | Reg A | other |
|---|---|---|---|---|---|
| `gemma3:1b` | 6/6 | 4/4 | — | — | — |
| `deepseek-v4-flash` | 6/6 | 4/4 | — | — | — |
| `google/gemma-4-31b-it` | 6/6 | 4/4 | — | — | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VoCare, Inc. | 506c | medium | 1B, hosted |
| Brewer Lane Ventures F | 506c | medium | 1B, hosted |
| Material Impact Fund I | 506c | medium | 1B |
| NextView Ventures V, L | 506c | medium | 1B, hosted |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.2 — Form D field extraction (Total Amount Sold)

**Corpus:** 2 real SEC Form D filings, human-validated answers (values range 2,366,532-70,227,931.85). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 2/2 | 23/40 (57%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 22/40 (55%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 1.2.1 — Total financing round size extraction

**Corpus:** 10 real SEC Form D filings (structured totalAmountSold field, operating companies only), human-validated answers (values range 3728926-21272455). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 87% | 30% | 10/10 | 199/200 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 8/10 | 115/200 (57%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GTX INC /DE/ | 21272455 | ? | mistral-large-or |
| VoCare, Inc. | 5000000 | ? | 1B |
| McBride Sisters Collec | 14040000 | ? | 1B |
| POSEIDON MEDICAL INC. | 6085780 | ? | 1B |
| BEYONDCORE, INC. | 8881213 | ? | 1B |
| ShopTap, Inc. | 5500000 | ? | mistral-large-or |
| Link Labs, Inc. | 5787732 | ? | 1B |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.4.1 — Annual dividend rate percentage extraction

**Corpus:** 6 real venture-financing preferred-stock charters, human-validated answers (values range 6-10). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 2/6 | 27/120 (22%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/6 | 76/120 (63%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| BIOACCELERATE HOLDINGS | 6 | ? | 1B |
| AdaptHealth Corp. | 8.0 | ? | 1B |
| scPharmaceuticals Inc. | 6 | ? | 1B |
| IMPEL NEUROPHARMA INC | 8 | ? | 1B |
| Zoom Video Communicati | 6 | ? | mistral-large-or |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 3.6 — Per-share dilution to new investors (compute)

**Corpus:** 5 real IPO prospectus Dilution-section tables, human-validated answers (values range 1.96-32.89). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **80%** | 49% | 0% | 5/5 | 96/100 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 59/100 (59%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | 2.09 | ? | 1B |
| Castle Biosciences, In | 28.82 | ? | 1B |
| Veritone, Inc. | 14.9 | ? | 1B |
| Axcella Health Inc. | 1.96 | ? | 1B |

## What this shows

- **Wobble spread: 0%–80% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.4 — Fully-diluted vs issued-outstanding basis classification

**Corpus:** 8 real venture financing exhibits + S-1 capitalization tables, human-validated answers (4 Fully-diluted / 4 Issued-outstanding). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 64% | 50% | 8/8 | 152/160 (95%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 6/8 | 80/160 (50%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **Fully-diluted · Issued-outstanding** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | Fully-diluted | Issued-outstanding |
|---|---|---|
| `gemma3:1b` | 4/4 | 0/4 |
| `deepseek-v4-flash` | 4/4 | 4/4 |
| `google/gemma-4-31b-it` | 4/4 | 4/4 |
| `mistralai/mistral-large-2512` | 4/4 | 2/2 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Actelis Networks, Inc. | fully-diluted | ? | 1B |
| Sybari Software, Inc. | fully-diluted | ? | 1B |
| Emageon Inc. | fully-diluted | ? | 1B |
| IGN Entertainment, Inc | fully-diluted | ? | 1B |
| Actelis Networks, Inc. | issued-outstanding | ? | 1B, mistral-large-or |
| IGN Entertainment, Inc | issued-outstanding | ? | 1B |
| HyreCar Inc. | issued-outstanding | ? | 1B |
| Castle Biosciences, In | issued-outstanding | ? | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.5 — Named-period revenue figure extraction

**Corpus:** 5 real S-1 Selected/Summary Financial Data tables, human-validated answers (values range 12619-9777079). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 86% | 20% | 5/5 | 97/100 (97%) |
| `deepseek-v4-flash` | hosted | **20%** | 97% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **20%** | 90% | 75% | 4/5 | 56/100 (56%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Civitas Solutions, Inc | 1123118 | ? | 1B |
| IGN Entertainment, Inc | 17541 | ? | mistral-large-or |
| Castle Biosciences, In | 22786 | ? | hosted |
| Emageon Inc. | 12619 | ? | 1B, mistral-large-or |
| HyreCar Inc. | 9777079 | ? | 1B |

## What this shows

- **Wobble spread: 0%–60% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.6 — Cross-citation share-count consistency flag

**Corpus:** 5 real S-1/424B4 filings, paired share-count citations, human-validated answers (values range False-True). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 60% | 5/5 | 99/100 (99%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **20%** | 89% | 75% | 4/5 | 68/100 (68%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Actelis Networks, Inc. | False | ? | mistral-large-or |
| Castle Biosciences, In | True | ? | mistral-large-or |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 6.5 — Post-termination option exercise window extraction

**Corpus:** 5 real SEC-filed option grant agreement exhibits, human-validated answers (values range 180 days-90 days). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 87% | 80% | 5/5 | 96/100 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **40%** | 87% | 100% | 3/5 | 52/100 (52%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SIRVA, Inc. | 30 days | ? | 1B, mistral-large-or |
| Annas Linens, Inc. | 90 days | ? | mistral-large-or |
| Williams Scotsman Inte | 90 days | ? | 1B, mistral-large-or |
| Douglas Dynamics, Inc. | 180 days | ? | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–60% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.4 — S-1 risk-factor heading extraction

**Corpus:** 5 real S-1/424B4 Risk Factors sections, human-validated answers (values range Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results.-We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively.). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 24% | 0% | 5/5 | 97/100 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 56/100 (56%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | Our limited operating history makes it difficult to evaluate our current business and prospects and may increase the risks associated with your investment. | ? | 1B |
| HyreCar Inc. | If we do not respond appropriately, the evolution of the automotive industry towards autonomous vehicles and mobility on demand services could adversely affect our business. | ? | 1B |
| HyreCar Inc. | Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results. | ? | 1B |
| Axcella Health Inc. | If you purchase our common stock in this offering, you will incur immediate and substantial dilution in the net tangible book value of your shares. | ? | 1B |
| Axcella Health Inc. | We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively. | ? | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.5 — Explicit pro-rata waiver vs grant flag

**Corpus:** 4 real SEC-filed investor rights agreements + waivers, human-validated answers (values range False-True). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 93% | 50% | 4/4 | 79/80 (99%) |
| `deepseek-v4-flash` | hosted | **25%** | 96% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 48/80 (60%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Xcyte Therapies, Inc. | True | ? | 1B |
| Rapid7, Inc. | True | ? | 1B, hosted |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.3 — Primary use of IPO proceeds extraction

**Corpus:** 5 real S-1/424B4 Use of Proceeds sections, human-validated answers (values range advance our current liver programs-working capital and general corporate purposes). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 68% | 20% | 5/5 | 83/100 (83%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **20%** | 96% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **20%** | 96% | 100% | 4/5 | 69/100 (69%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | general corporate purposes | ? | 1B |
| Castle Biosciences, In | research and development activities | ? | 1B, gemma4-31b-or |
| Axcella Health Inc. | advance our current liver programs | ? | 1B, mistral-large-or |
| Veritone, Inc. | working capital and general corporate purposes | ? | 1B |
| Civitas Solutions, Inc | redeem all of the senior notes | ? | 1B, mistral-large-or |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.2.2 — Named investor's individual dollar allocation extraction

**Corpus:** 5 real SEC Schedule 13D/13D-A filings (investor-side), human-validated answers (values range 46715.64-9418200). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 91% | 80% | 5/5 | 97/100 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 80/100 (80%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 62/100 (62%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CAS Medical Systems, I | 9418200 | ? | 1B |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 3.3 — Pre-money option pool price-per-share compute

**Corpus:** 3 real SEC-filed Agreement for Future Equity worked examples (Form C exhibit), human-validated answers (values range 0.24-0.909). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 62% | 0% | 3/3 | 60/60 (100%) |
| `deepseek-v4-flash` | hosted | **67%** | 91% | 33% | 3/3 | 44/60 (73%) |
| `google/gemma-4-31b-it` | ? | **67%** | 80% | 33% | 3/3 | 60/60 (100%) |
| `mistralai/mistral-large-2512` | ? | **33%** | 97% | 67% | 3/3 | 37/60 (62%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Snapwire Media, Inc. ( | 0.909 | ? | 1B, hosted, gemma4-31b-or |
| Snapwire Media, Inc. ( | 0.24 | ? | 1B |
| Snapwire Media, Inc. ( | 0.6956 | ? | 1B, hosted, gemma4-31b-or, mistral-large-or |

## What this shows

- **Wobble spread: 33%–100% across the ladder.** Lowest-wobble model: **mistral-large-or** (33% wobble, 67% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 4.4 — Convert-vs-take-preference decision (compute)

**Corpus:** 2 real SEC-filed Agreement for Future Equity worked examples (Form C exhibit), human-validated answers (1 Convert / 1 Take preference). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 50% | 2/2 | 37/40 (92%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 34/40 (85%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **Convert · Take preference** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | Convert | Take preference |
|---|---|---|
| `gemma3:1b` | 1/1 | 0/1 |
| `deepseek-v4-flash` | 1/1 | 1/1 |
| `google/gemma-4-31b-it` | 1/1 | 1/1 |
| `mistralai/mistral-large-2512` | 1/1 | 1/1 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 4.1 — Per-share value to common after preferred waterfall (compute)

**Corpus:** 4 real SC 13E-3 going-private fairness opinion, human-validated answers (values range 0.39-0.51). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 17% | 0% | 4/4 | 77/80 (96%) |
| `deepseek-v4-flash` | hosted | **25%** | 99% | 100% | 4/4 | 62/80 (78%) |
| `google/gemma-4-31b-it` | ? | **100%** | 71% | 50% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **25%** | 97% | 67% | 3/4 | 51/80 (64%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Connecture, Inc. | 0.51 | ? | 1B, gemma4-31b-or, mistral-large-or |
| Connecture, Inc. | 0.42 | ? | 1B, gemma4-31b-or |
| Connecture, Inc. | 0.39 | ? | 1B, hosted, gemma4-31b-or, mistral-large-or |
| Connecture, Inc. | 0.44 | ? | 1B, gemma4-31b-or |

## What this shows

- **Wobble spread: 25%–100% across the ladder.** Lowest-wobble model: **hosted** (25% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 4.3 — Named preferred series' total waterfall payout (compute)

**Corpus:** 2 real SC 13E-3 going-private fairness opinion, human-validated answers (values range 19.7-58.9). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 52% | 50% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 24/40 (60%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Connecture, Inc. | 58.9 | ? | 1B |
| Connecture, Inc. | 19.7 | ? | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Models and scope

Per leaf during the build-out, Probity runs the **fast set** (1B/3B/12B local via Ollama, zero
egress, plus deepseek-v4-flash) so a leaf costs minutes. The **heavy comprehensive run**
(qwen3.5:27b and hosted frontier models - Gemini, Haiku, etc. - at N=20+) is deferred to a single
sweep across all leaves once the full benchmark exists.

## Reproduce

```bash
cd leaves/<test_name>
python3 source.py          # fetch the real SEC documents
python3 run.py             # run the model ladder, N=20
python3 ../../results/render.py
```

Answers are human-validated from each document's own legal text (`leaves/<test>/oracle.jsonl`, with
the validating quote + difficulty per item). Genuinely ambiguous clauses are excluded, not guessed.

