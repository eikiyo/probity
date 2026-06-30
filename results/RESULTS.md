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

