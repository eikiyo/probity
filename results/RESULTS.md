# Probity — Benchmark Results

**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a human-validated answer extracted from the source document. They are reported separately and never averaged — a model can be perfectly consistent and consistently wrong.

Models span a size ladder (1B → 12B local + a hosted model) to test whether wobble falls as capability rises. Local via Ollama (zero egress); hosted = deepseek-v4-flash.

---

## Test 1.3.2 — Preferred-stock liquidation participation

**Corpus:** 18 real SEC-filed charter clauses, human-validated answers (5 part / 8 non-part / 5 capped). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **61%** | 90% | 39% | 18/18 |
| `llama3.2:latest` | 3B | **72%** | 84% | 44% | 18/18 |
| `gemma4:12b` | 12B | **0%** | 100% | 72% | 18/18 |
| `deepseek-v4-flash` | hosted | **6%** | 98% | 67% | 18/18 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **non-part · part · capped** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | part | non-part | capped |
|---|---|---|---|
| `gemma3:1b` | 0/5 | 7/8 | 0/5 |
| `llama3.2:latest` | 0/5 | 7/8 | 1/5 |
| `gemma4:12b` | 2/5 | 6/8 | 5/5 |
| `deepseek-v4-flash` | 1/5 | 6/8 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| EndoStim, Inc. | non-participating | medium | 1B, 3B |
| Pfenex Inc. | non-participating | hard | 3B |
| Zoom Video Communicati | non-participating | easy | 3B |
| Sonos Inc | non-participating | easy | 3B |
| Enservco Corp | non-participating | easy | 1B |
| BioAccelerate Holdings | non-participating | hard | 1B |
| Entercom Communication | non-participating | hard | 1B |
| scPharmaceuticals Inc. | participating | medium | 1B, 3B |
| Akouos, Inc. | participating | medium | 1B, 3B |
| IESI Corp | participating | hard | 1B, 3B |
| The Medicines Co (Remp | capped | medium | 1B, 3B |
| Fitbit Inc | capped | hard | 1B, 3B |
| Workday, Inc. | capped | medium | 1B, 3B |
| Alexza Pharmaceuticals | capped | medium | 3B |
| Entellus Medical Inc | participating | easy | 3B, hosted |
| Internet Security Syst | participating | easy | 1B, 3B |

## What this shows

- **Wobble has a cliff, not a slope.** The 1B and 3B models flip their answer on 61-72% of items
  across 20 runs at temp 0.7 - unusable in a workflow that touches money. At 12B wobble collapses
  to 0%; the hosted model sits at 6%. The usable/unusable boundary is between 3B and 12B, not a
  smooth gradient. (N=5 hid this entirely - both mid/hosted models looked perfectly stable.)
- **A local 12B model beats a hosted frontier-cheap model here.** gemma4:12b: 0% wobble, 72%
  accuracy. deepseek-v4-flash: 6% wobble, 67%. Bigger-and-hosted is not automatically better.
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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **6%** | 98% | 62% | 16/16 |
| `llama3.2:latest` | 3B | **56%** | 88% | 81% | 16/16 |
| `gemma4:12b` | 12B | **0%** | 100% | 100% | 16/16 |
| `deepseek-v4-flash` | hosted | **19%** | 99% | 100% | 16/16 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **post · pre** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | post | pre |
|---|---|---|
| `gemma3:1b` | 10/10 | 0/6 |
| `llama3.2:latest` | 10/10 | 3/6 |
| `gemma4:12b` | 10/10 | 6/6 |
| `deepseek-v4-flash` | 10/10 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| TaoWeave, Inc.  (TWAV) | post-money | easy | 3B |
| Maison Luxe, Inc.  (MA | post-money | easy | 3B |
| AMC Robotics Corp  (AM | post-money | easy | 3B |
| Neo Aeronautics, Inc.  | pre-money | easy | 3B, hosted |
| Rentberry Inc.  (CIK 0 | pre-money | easy | 3B, hosted |
| Complete Solaria, Inc. | pre-money | easy | 3B, hosted |
| Invizyne Technologies  | pre-money | easy | 3B |
| IDEANOMICS, INC.  (IDE | pre-money | easy | 1B, 3B |
| Pluri Inc.  (PLUR)  (C | pre-money | easy | 3B |

## What this shows

- **Accuracy does not imply trustworthiness — the cleanest case yet.** deepseek-v4-flash answers
  every one of the 16 SAFEs correctly (100% accuracy) yet still **wobbles on 19% of them** across 20
  identical runs. A model you would call "100% accurate" from a single pass changes its answer on
  ~1 in 5 items when you actually repeat the question. Wobble catches what an accuracy score hides.
- **A local 12B fully solves the binary task** (gemma4:12b: 0% wobble, 100% accuracy) - and again
  beats the hosted model on the trust axis, matching it on accuracy at zero egress.
- **Low wobble can mask low accuracy.** gemma3:1b looks stable (6% wobble) but is only 62% accurate -
  it confidently and *repeatably* gives the wrong pre/post classification. Consistency without
  accuracy is its own trap; this is why the two numbers are never averaged.
- **The 3B is the worst wobbler** (llama3.2: 56% wobble) despite 81% accuracy - the mid-size model
  is both more right and far less stable than the 1B, so wobble is not a smooth function of size.

---

## Test 1.4.2 — Preferred dividends: cumulative vs non-cumulative

**Corpus:** 16 real SEC-filed preferred-stock charter dividend clauses, human-validated answers (8 cumulative / 8 non-cum). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 88% | 16/16 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 16/16 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **cumulative · non-cum** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | cumulative | non-cum |
|---|---|---|
| `gemma3:1b` | 7/8 | 7/8 |
| `deepseek-v4-flash` | 8/8 | 8/8 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ENTERCOM COMMUNICATION | cumulative | easy | 1B |
| BIOACCELERATE HOLDINGS | cumulative | easy | 1B |
| FS Credit Opportunitie | cumulative | hard | 1B |
| IMPEL NEUROPHARMA INC | non-cumulative | easy | 1B |
| Teladoc, Inc. | non-cumulative | easy | 1B |
| Eiger BioPharmaceutica | non-cumulative | medium | 1B |
| scPharmaceuticals Inc. | non-cumulative | easy | 1B |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger

**Corpus:** 13 real SEC-filed equity-award / employment agreements, human-validated answers (6 single / 7 double). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 97% | 85% | 13/13 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 13/13 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **single · double** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | single | double |
|---|---|---|
| `gemma3:1b` | 4/6 | 7/7 |
| `deepseek-v4-flash` | 6/6 | 7/7 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GIBRALTAR INDUSTRIES,  | double-trigger | hard | 1B |
| Vulcan Materials CO | double-trigger | hard | 1B |
| Nimble Storage Inc | single-trigger | medium | 1B |
| LogicMark, Inc. | single-trigger | easy | 1B |
| COMSCORE, INC. | single-trigger | hard | 1B |
| REVVITY, INC. | single-trigger | easy | 1B |

## What this shows

- **Wobble spread: 0%–46% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked

**Corpus:** 11 real SEC-filed multi-series preferred charters, human-validated answers (6 pari-passu / 5 stacked). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **45%** | 97% | 45% | 11/11 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 82% | 11/11 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **pari-passu · stacked** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pari-passu | stacked |
|---|---|---|
| `gemma3:1b` | 0/6 | 5/5 |
| `deepseek-v4-flash` | 4/6 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Banks.com, Inc. | stacked | medium | 1B |
| Teladoc, Inc. | stacked | easy | 1B |
| VioQuest Pharmaceutica | pari-passu | easy | 1B |
| RIGHT START INC /CA | pari-passu | medium | 1B |
| PRECOM TECHNOLOGY INC | pari-passu | hard | 1B |

## What this shows

- **Wobble spread: 0%–45% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 82% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.1 — Risk flag: off-market liquidation preference (>1x)

**Corpus:** 10 real SEC-filed preferred-stock liquidation clauses, human-validated answers (5 off-market(>1x) / 5 standard(1x)). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 95% | 40% | 10/10 |
| `deepseek-v4-flash` | hosted | **10%** | 99% | 90% | 10/10 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **off-market(>1x) · standard(1x)** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | off-market(>1x) | standard(1x) |
|---|---|---|
| `gemma3:1b` | 3/5 | 1/5 |
| `deepseek-v4-flash` | 5/5 | 4/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MELINTA THERAPEUTICS,  | yes | easy | 1B |
| Lulu's Fashion Lounge  | yes | hard | 1B |
| Workday, Inc. | no | hard | 1B, hosted |
| ENDOSTIM, INC. | no | easy | 1B |

## What this shows

- **Wobble spread: 10%–40% across the ladder.** Lowest-wobble model: **hosted** (10% wobble, 90% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.7 — Redemption rights: redeemable vs non-redeemable

**Corpus:** 10 real SEC-filed preferred-stock charter redemption clauses, human-validated answers (5 redeemable / 5 non-redeem). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 97% | 50% | 10/10 |
| `deepseek-v4-flash` | hosted | **10%** | 96% | 100% | 10/10 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **redeemable · non-redeem** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | redeemable | non-redeem |
|---|---|---|
| `gemma3:1b` | 0/5 | 5/5 |
| `deepseek-v4-flash` | 5/5 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Lulu's Fashion Lounge  | yes | medium | 1B |
| Tenable Holdings, Inc. | yes | medium | 1B |
| Pfenex Inc. | yes | hard | hosted |

## What this shows

- **Wobble spread: 10%–20% across the ladder.** Lowest-wobble model: **hosted** (10% wobble, 100% accuracy).

---

## Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)

**Corpus:** 12 real SEC-filed stockholder/transfer agreements, human-validated answers (6 drag(obligated) / 6 co-sale(right)). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 99% | 42% | 12/12 |
| `deepseek-v4-flash` | hosted | **8%** | 97% | 100% | 12/12 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **drag(obligated) · co-sale(right)** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | drag(obligated) | co-sale(right) |
|---|---|---|
| `gemma3:1b` | 4/6 | 1/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| TRUMP ENTERTAINMENT RE | yes | easy | 1B, hosted |
| LOEWS CINEPLEX ENTERTA | yes | medium | 1B |

## What this shows

- **Wobble spread: 8%–17% across the ladder.** Lowest-wobble model: **hosted** (8% wobble, 100% accuracy).

---

## Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent

**Corpus:** 12 real SEC-filed stockholder/transfer documents, human-validated answers (6 rofr/cosale / 6 absent/other-right). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 98% | 67% | 12/12 |
| `deepseek-v4-flash` | hosted | **17%** | 94% | 92% | 12/12 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **rofr/cosale · absent/other-right** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | rofr/cosale | absent/other-right |
|---|---|---|
| `gemma3:1b` | 6/6 | 2/6 |
| `deepseek-v4-flash` | 6/6 | 5/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MotivNation | no | hard | 1B, hosted |
| EntreMetrix | no | hard | 1B, hosted |

## What this shows

- **Wobble spread: 17%–17% across the ladder.** Lowest-wobble model: **hosted** (17% wobble, 92% accuracy).

---

## Test 5.4 — Pro-rata right on future financings: granted vs not

**Corpus:** 12 real SEC-filed SAFEs, side letters and investors' rights agreements, human-validated answers (6 pro-rata / 6 absent/waived). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 94% | 100% | 12/12 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 12/12 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **pro-rata · absent/waived** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pro-rata | absent/waived |
|---|---|---|
| `gemma3:1b` | 6/6 | 6/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SOS Hydration Inc. | yes | medium | 1B, hosted |
| Infinity Pharmaceutica | no | easy | 1B |

## What this shows

- **Wobble spread: 8%–17% across the ladder.** Lowest-wobble model: **hosted** (8% wobble, 100% accuracy).

---

## Test 6.2 — Vesting schedule: cliff present vs absent

**Corpus:** 12 real SEC-filed equity-award agreements and disclosures, human-validated answers (6 cliff / 6 no-cliff). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 96% | 67% | 12/12 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 12/12 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **cliff · no-cliff** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | cliff | no-cliff |
|---|---|---|
| `gemma3:1b` | 6/6 | 2/6 |
| `deepseek-v4-flash` | 6/6 | 5/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Interval Leisure Group | yes | medium | 1B |
| World Heart Corp | no | hard | 1B |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 92% accuracy).

---

## Test 5.2 — Protective provisions: investor class-veto right present vs absent

**Corpus:** 12 real SEC-filed charters and governance documents, human-validated answers (6 veto-right / 6 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 97% | 58% | 12/12 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 12/12 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **veto-right · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | veto-right | absent |
|---|---|---|
| `gemma3:1b` | 6/6 | 1/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SCYNEXIS, Inc. | yes | medium | 1B |
| Non-binding LOI (Omni  | no | easy | 1B |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 5.3 — Information rights: live financial-reporting obligation vs absent

**Corpus:** 12 real SEC-filed investors' rights agreements and equity-award docs, human-validated answers (6 info-rights / 6 absent/waived). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 95% | 50% | 12/12 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 12/12 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **info-rights · absent/waived** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | info-rights | absent/waived |
|---|---|---|
| `gemma3:1b` | 6/6 | 0/6 |
| `deepseek-v4-flash` | 5/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Speedway Motorsports,  | no | easy | 1B |
| Pool Corp | no | easy | 1B |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 92% accuracy).

---

## Test 5.7 — Vesting acceleration: granted on trigger vs absent

**Corpus:** 9 real SEC-filed equity-award agreements and proxy disclosures, human-validated answers (6 accelerates / 3 no-acceleration). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 67% | 9/9 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **accelerates · no-acceleration** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | accelerates | no-acceleration |
|---|---|---|
| `gemma3:1b` | 4/6 | 2/3 |
| `deepseek-v4-flash` | 6/6 | 3/3 |

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

**Corpus:** 13 real SEC-filed preferred-stock liquidation preference clauses, human-validated answers (0 non-part / 4 1x / 5 2x / 4 3x / 0 other). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 91% | 0% | 12/13 |
| `deepseek-v4-flash` | hosted | **46%** | 87% | 62% | 13/13 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **non-part · 1x · 2x · 3x · other** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | non-part | 1x | 2x | 3x | other |
|---|---|---|---|---|---|
| `gemma3:1b` | — | 0/4 | 0/5 | 0/3 | — |
| `deepseek-v4-flash` | — | 3/4 | 1/5 | 4/4 | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| BIOVENTRIX, INC.  (CIK | 1x | easy | 1B |
| Oportun Financial Corp | 2x | easy | 1B, hosted |
| Pagaya Technologies Lt | 2x | easy | 1B, hosted |
| Pagaya Technologies Lt | 2x | easy | 1B, hosted |
| Pagaya Technologies Lt | 2x | easy | 1B, hosted |
| 24/7 REAL MEDIA INC  ( | 3x | easy | 1B |
| CASTLE BIOSCIENCES INC | 3x | easy | hosted |
| CASTLE BIOSCIENCES INC | 3x | easy | 1B, hosted |

## What this shows

- **Wobble spread: 46%–46% across the ladder.** Lowest-wobble model: **hosted** (46% wobble, 62% accuracy).

---

## Test 5.1 — Board seats: number an investor has the right to designate

**Corpus:** 9 real SEC-filed voting/shareholders'/designation agreements, human-validated answers (values range 1-9). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 92% | 78% | 9/9 |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 78% | 9/9 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SICOR Inc. | 3 | easy | 1B |
| Dollar General Corpora | 1 | medium | 1B |
| Ute Energy Corporation | 1 | medium | 1B |
| Ute Energy Corporation | 2 | medium | 1B |
| Cinemark Holdings, Inc | 9 | hard | hosted |

## What this shows

- **Wobble spread: 11%–44% across the ladder.** Lowest-wobble model: **hosted** (11% wobble, 78% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.6 — SAFE pro-rata side letter: granted vs absent

**Corpus:** 15 real SEC-filed SAFEs and pro-rata side letters, human-validated answers (9 pro-rata / 6 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 96% | 93% | 15/15 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 15/15 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **pro-rata · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pro-rata | absent |
|---|---|---|
| `gemma3:1b` | 9/9 | 5/6 |
| `deepseek-v4-flash` | 9/9 | 6/6 |

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

**Corpus:** 21 real SEC-filed priced-round financing documents, human-validated answers (15 pre / 6 post). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **86%** | 84% | 71% | 21/21 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 95% | 21/21 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **pre · post** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pre | post |
|---|---|---|
| `gemma3:1b` | 9/15 | 6/6 |
| `deepseek-v4-flash` | 15/15 | 5/6 |

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
| Cytosorbents Corp | pre-money | medium | 1B |
| Cytosorbents Corp | pre-money | medium | 1B |
| GreenCell, Inc | pre-money | medium | 1B |
| BIOLARGO, INC. | pre-money | medium | 1B |
| HAGUE CORP. | pre-money | easy | 1B |
| SOCIETY PASS INCORPORA | pre-money | easy | 1B |
| PROVECTUS BIOPHARMACEU | post-money | easy | 1B |
| Fold Holdings, Inc. | post-money | easy | 1B |
| Cerebras Systems Inc. | post-money | medium | 1B |
| Oculus Innovative Scie | post-money | medium | 1B |
| Oculus Innovative Scie | post-money | medium | 1B |

## What this shows

- **Wobble spread: 0%–86% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 95% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.2 — Risk flag: full-ratchet anti-dilution present vs absent

**Corpus:** 7 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (4 full-ratchet / 3 absent). Each model run **28×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 57% | 7/7 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 86% | 7/7 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **full-ratchet · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | full-ratchet | absent |
|---|---|---|
| `gemma3:1b` | 4/4 | 0/3 |
| `deepseek-v4-flash` | 4/4 | 2/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 86% accuracy).

---

## Test 1.1.1 — Post-money valuation extraction

**Corpus:** 4 real SEC-filed priced-round financing documents, human-validated answers (values range 5000000-275000000). Each model run **30×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **25%** | 96% | 25% | 4/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 50% | 4/4 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Remark Holdings, Inc.  | 5000000 | easy | 1B |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 50% accuracy).

---

## Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none

**Corpus:** 5 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (2 full-ratchet / 2 weighted-avg / 0 broad-based / 0 narrow-based / 1 none). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 40% | 5/5 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **full-ratchet · weighted-avg · broad-based · narrow-based · none** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | full-ratchet | weighted-avg | broad-based | narrow-based | none |
|---|---|---|---|---|---|
| `gemma3:1b` | 2/2 | 0/2 | — | — | 0/1 |
| `deepseek-v4-flash` | 2/2 | 2/2 | — | — | 1/1 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 8.3 — Risk flag: uncapped participating-preferred present vs absent

**Corpus:** 13 real SEC-filed preferred-stock liquidation/participation clauses, human-validated answers (4 uncapped / 9 capped/none). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **8%** | 99% | 31% | 13/13 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 85% | 13/13 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **uncapped · capped/none** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | uncapped | capped/none |
|---|---|---|
| `gemma3:1b` | 4/4 | 0/9 |
| `deepseek-v4-flash` | 2/4 | 9/9 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Jazz Semiconductor Inc | no | medium | hosted |
| Workday, Inc. | no | medium | 1B |

## What this shows

- **Wobble spread: 8%–8% across the ladder.** Lowest-wobble model: **hosted** (8% wobble, 85% accuracy).

---

## Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent

**Corpus:** 7 real SEC-filed SAFE agreements, human-validated answers (4 MFN / 3 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 95% | 100% | 7/7 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **MFN · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | MFN | absent |
|---|---|---|
| `gemma3:1b` | 4/4 | 3/3 |
| `deepseek-v4-flash` | 4/4 | 3/3 |

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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 3/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/3 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **71%** | 87% | 57% | 7/7 |
| `deepseek-v4-flash` | hosted | **29%** | 90% | 43% | 7/7 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Medecision, Inc. | 0.03 | easy | 1B |
| Medecision, Inc. | 0.25 | easy | 1B |
| WhiteGlove Health, Inc | 0.61 | easy | 1B |
| Medecision, Inc. | 1.25 | medium | 1B, hosted |
| Medecision, Inc. | 2.0 | medium | 1B, hosted |

## What this shows

- **Wobble spread: 29%–71% across the ladder.** Lowest-wobble model: **hosted** (29% wobble, 43% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.1 — SAFE valuation cap extraction

**Corpus:** 8 real SEC-filed SAFE agreements, human-validated answers (values range 15000000-150000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 96% | 88% | 8/8 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 8/8 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 7/7 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 2.1.2 — SAFE discount rate extraction

**Corpus:** 9 real SEC-filed SAFE agreements, human-validated answers (values range 10-50). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 89% | 56% | 9/9 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 88% | 50% | 4/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/4 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Damon Motors Inc. | 125000000 | easy | 1B |
| Exyn Technologies, Inc | 90000000 | medium | hosted |
| Greenfield Robotics Co | 30000000 | easy | 1B |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.6.1 — Preferred-stock conversion ratio extraction

**Corpus:** 5 real SEC-filed preferred-stock charters, human-validated answers (values range 1-8000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 92% | 80% | 5/5 |
| `deepseek-v4-flash` | hosted | **20%** | 98% | 100% | 5/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Air Defense Services,  | 100 | medium | hosted |
| Boston Life Sciences,  | 8000 | hard | 1B |

## What this shows

- **Wobble spread: 20%–20% across the ladder.** Lowest-wobble model: **hosted** (20% wobble, 100% accuracy).

---

## Test 1.5.2 — Anti-dilution weighted-average base: broad-based vs narrow-based vs n/a

**Corpus:** 10 real SEC-filed preferred-stock charter anti-dilution clauses, human-validated answers (3 broad / 4 narrow / 3 n/a). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 96% | 70% | 10/10 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 10/10 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **broad · narrow · n/a** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | broad | narrow | n/a |
|---|---|---|---|
| `gemma3:1b` | 3/3 | 4/4 | 0/3 |
| `deepseek-v4-flash` | 3/3 | 4/4 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 5/5 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 83% | 6/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)

**Corpus:** 11 real SEC-filed SAFE (Simple Agreement for Future Equity) instruments, human-validated answers (0 cap / 1 discount / 10 both-mfn). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **18%** | 98% | 73% | 11/11 |
| `deepseek-v4-flash` | hosted | **9%** | 100% | 100% | 11/11 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **cap · discount · both-mfn** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | cap | discount | both-mfn |
|---|---|---|---|
| `gemma3:1b` | — | 0/1 | 8/10 |
| `deepseek-v4-flash` | — | 1/1 | 10/10 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SNM Global Holdings, I | discount | easy | 1B |
| Rentberry Inc. | both-mfn | medium | hosted |
| Creci Inc. | both-mfn | medium | 1B |

## What this shows

- **Wobble spread: 9%–18% across the ladder.** Lowest-wobble model: **hosted** (9% wobble, 100% accuracy).

---

## Test 1.1.3 — Priced-round price-per-share extraction

**Corpus:** 9 real SEC-filed stock purchase agreements / charters / offerings, human-validated answers (values range 0.0031-1.5). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **22%** | 95% | 56% | 9/9 |
| `deepseek-v4-flash` | hosted | **22%** | 94% | 67% | 9/9 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Airborne Wireless Netw | 1.5 | easy | 1B, hosted |
| General Metals Corpora | 0.025 | easy | hosted |
| WhiteGlove Health, Inc | 0.2 | easy | 1B |

## What this shows

- **Wobble spread: 22%–22% across the ladder.** Lowest-wobble model: **hosted** (22% wobble, 67% accuracy).

---

## Test 2.2.3 — Convertible note maturity date extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 2005-03-31-2026-12-31). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 94% | 50% | 4/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GARDENBURGER, INC. | 2005-03-31 | easy | 1B |
| ACOLOGY, INC. | 2015-03-04 | medium | 1B |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.5 — Convertible note conversion-discount rate extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 5.0-50.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 25% | 4/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction

**Corpus:** 2 real SEC-filed convertible promissory notes, human-validated answers (values range 10000000-40000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 2/2 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 6.1 — Equity vesting schedule extraction + normalization

**Corpus:** 9 real SEC-filed equity-award / employment agreements, human-validated answers (values range 1.5yr/no-cliff-4yr/no-cliff). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 25% | 8/9 |
| `deepseek-v4-flash` | hosted | **22%** | 95% | 89% | 9/9 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CONOR MEDSYSTEMS, INC. | 1.5yr/no-cliff | medium | 1B, hosted |
| CLARCOR INC. | 4yr/no-cliff | hard | hosted |

## What this shows

- **Wobble spread: 0%–22% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 25% accuracy).

---

## Test 3.1 — Cap-table current ownership percentage (compute)

**Corpus:** 9 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-33.9). Each model run **19×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 16% | 0% | 9/9 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | 1B |
| Uber Technologies, Inc | 11.0 | easy | 1B |
| Uber Technologies, Inc | 2.4 | medium | 1B |
| Uber Technologies, Inc | 8.6 | easy | 1B |
| Uber Technologies, Inc | 5.4 | medium | 1B |
| Uber Technologies, Inc | 16.3 | medium | 1B |
| Uber Technologies, Inc | 5.2 | medium | 1B |
| Uber Technologies, Inc | 5.3 | medium | 1B |
| Uber Technologies, Inc | 33.9 | hard | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.1 — Named founder's ownership percentage (compute)

**Corpus:** 3 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-8.6). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 18% | 0% | 3/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/3 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 38% | 0% | 4/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 47% | 0% | 1/1 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 1/1 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 9.5 | easy | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.1 — Securities Act exemption classification

**Corpus:** 10 real SEC Form D filings (structured federalExemptionsExclusions field), human-validated answers (6 506(b) / 4 506(c) / 0 504 / 0 Reg A / 0 other). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 87% | 90% | 10/10 |
| `deepseek-v4-flash` | hosted | **30%** | 96% | 100% | 10/10 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **506(b) · 506(c) · 504 · Reg A · other** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | 506(b) | 506(c) | 504 | Reg A | other |
|---|---|---|---|---|---|
| `gemma3:1b` | 6/6 | 3/4 | — | — | — |
| `deepseek-v4-flash` | 6/6 | 4/4 | — | — | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VoCare, Inc. | 506c | medium | 1B, hosted |
| Brewer Lane Ventures F | 506c | medium | 1B, hosted |
| Material Impact Fund I | 506c | medium | 1B |
| NextView Ventures V, L | 506c | medium | 1B, hosted |

## What this shows

- **Wobble spread: 30%–40% across the ladder.** Lowest-wobble model: **hosted** (30% wobble, 100% accuracy).

---

## Test 7.2 — Form D field extraction (Total Amount Sold)

**Corpus:** 2 real SEC Form D filings, human-validated answers (values range 2,366,532-70,227,931.85). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 90% | 0% | 2/2 |
| `deepseek-v4-flash` | hosted | **50%** | 95% | 100% | 2/2 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| NETBASE SOLUTIONS INC  | 2,366,532 | medium | hosted |
| Skybox Imaging, Inc.   | 70,227,931.85 | medium | 1B |

## What this shows

- **Wobble spread: 50%–50% across the ladder.** Lowest-wobble model: **hosted** (50% wobble, 100% accuracy).

---

## Test 1.2.1 — Total financing round size extraction

**Corpus:** 10 real SEC Form D filings (structured totalAmountSold field, operating companies only), human-validated answers (values range 3728926-21272455). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 30% | 10/10 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 30% | 10/10 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 30% accuracy).

---

## Test 1.4.1 — Annual dividend rate percentage extraction

**Corpus:** 6 real venture-financing preferred-stock charters, human-validated answers (values range 6-10). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 2/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| BIOACCELERATE HOLDINGS | 6 | ? | 1B |
| AdaptHealth Corp. | 8.0 | ? | 1B |
| scPharmaceuticals Inc. | 6 | ? | 1B |
| IMPEL NEUROPHARMA INC | 8 | ? | 1B |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).

---

## Test 3.6 — Per-share dilution to new investors (compute)

**Corpus:** 5 real IPO prospectus Dilution-section tables, human-validated answers (values range 1.96-32.89). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **80%** | 49% | 0% | 5/5 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 64% | 50% | 8/8 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 8/8 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Fully-diluted · Issued-outstanding** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | Fully-diluted | Issued-outstanding |
|---|---|---|
| `gemma3:1b` | 4/4 | 0/4 |
| `deepseek-v4-flash` | 4/4 | 4/4 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Actelis Networks, Inc. | fully-diluted | ? | 1B |
| Sybari Software, Inc. | fully-diluted | ? | 1B |
| Emageon Inc. | fully-diluted | ? | 1B |
| IGN Entertainment, Inc | fully-diluted | ? | 1B |
| Actelis Networks, Inc. | issued-outstanding | ? | 1B |
| IGN Entertainment, Inc | issued-outstanding | ? | 1B |
| HyreCar Inc. | issued-outstanding | ? | 1B |
| Castle Biosciences, In | issued-outstanding | ? | 1B |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.5 — Named-period revenue figure extraction

**Corpus:** 5 real S-1 Selected/Summary Financial Data tables, human-validated answers (values range 12619-9777079). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 86% | 20% | 5/5 |
| `deepseek-v4-flash` | hosted | **20%** | 97% | 100% | 5/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Civitas Solutions, Inc | 1123118 | ? | 1B |
| Castle Biosciences, In | 22786 | ? | hosted |
| Emageon Inc. | 12619 | ? | 1B |
| HyreCar Inc. | 9777079 | ? | 1B |

## What this shows

- **Wobble spread: 20%–60% across the ladder.** Lowest-wobble model: **hosted** (20% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.6 — Cross-citation share-count consistency flag

**Corpus:** 5 real S-1/424B4 filings, paired share-count citations, human-validated answers (values range False-True). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 60% | 5/5 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

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

