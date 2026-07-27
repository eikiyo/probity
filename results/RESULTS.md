# Probity — Benchmark Results

**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a human-validated answer extracted from the source document. They are reported separately and never averaged — a model can be perfectly consistent and consistently wrong.

11 models span a size ladder (1B local → hosted frontier) to test whether wobble falls as capability rises. Local via Ollama (zero egress); hosted via OpenRouter and direct provider APIs.

---

## Test 1.3.2 — Preferred-stock liquidation participation

**Corpus:** 18 real SEC-filed charter clauses, human-validated answers (6 part / 7 non-part / 5 capped). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **83%** | 89% | 33% | 18/18 | 340/360 (94%) |
| `deepseek-v4-flash` | hosted | **11%** | 98% | 67% | 18/18 | 342/360 (95%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |
| `mistralai/mistral-large-2512` | ? | **6%** | 98% | 72% | 18/18 | 360/360 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **11%** | 97% | 78% | 18/18 | 360/360 (100%) |
| `gemma3:1b-it-qat` | ? | **56%** | 89% | 39% | 18/18 | 360/360 (100%) |
| `minimax/minimax-m2.5` | ? | **11%** | 99% | 72% | 18/18 | 359/360 (100%) |
| `google/gemini-3-flash-preview` | ? | **6%** | 99% | 67% | 18/18 | 359/360 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |
| `openai/gpt-oss-120b` | ? | **22%** | 97% | 72% | 18/18 | 353/360 (98%) |
| `openai/gpt-5-mini` | ? | **6%** | 100% | 72% | 18/18 | 360/360 (100%) |

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
| `mistralai/mistral-large-2512` | 1/6 | 7/7 | 5/5 |
| `meta-llama/llama-3.3-70b-instruct` | 3/6 | 6/7 | 5/5 |
| `gemma3:1b-it-qat` | 2/6 | 4/7 | 1/5 |
| `minimax/minimax-m2.5` | 2/6 | 6/7 | 5/5 |
| `google/gemini-3-flash-preview` | 2/6 | 6/7 | 4/5 |
| `claude-haiku-4-5-20251001` | 2/6 | 6/7 | 5/5 |
| `openai/gpt-oss-120b` | 2/6 | 6/7 | 5/5 |
| `openai/gpt-5-mini` | 2/6 | 6/7 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| EndoStim, Inc. | non-participating | medium | 1B |
| Interlink Electronics  | non-participating | easy | 1B, gemma3-1b-qat, gpt-oss-120b-or |
| Pfenex Inc. | participating | hard | 1B, gemma3-1b-qat |
| Zoom Video Communicati | non-participating | easy | gpt5-mini-or |
| Sonos Inc | non-participating | easy | 1B |
| Enservco Corp | non-participating | easy | 1B |
| BioAccelerate Holdings | non-participating | hard | 1B, gemma3-1b-qat |
| Entercom Communication | non-participating | hard | 1B, gemma3-1b-qat |
| scPharmaceuticals Inc. | participating | medium | 1B, gpt-oss-120b-or |
| Akouos, Inc. | participating | medium | 1B, gemma3-1b-qat, gpt-oss-120b-or |
| IESI Corp | participating | hard | mistral-large-or, gemma3-1b-qat |
| Jazz Semiconductor Inc | capped | medium | 1B, hosted, minimax-m2.5-or, gemini3-flash-or |
| The Medicines Co (Remp | capped | medium | 1B, gemma3-1b-qat |
| Fitbit Inc | capped | hard | 1B, gemma3-1b-qat, gpt-oss-120b-or |
| Workday, Inc. | capped | medium | 1B, llama3.3-70b-or, minimax-m2.5-or |
| Alexza Pharmaceuticals | capped | medium | gemma3-1b-qat |
| Entellus Medical Inc | participating | easy | 1B, hosted |
| Internet Security Syst | participating | easy | 1B, llama3.3-70b-or, gemma3-1b-qat |

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
| `gemma3:1b` | 1B | **6%** | 99% | 62% | 16/16 | 320/320 (100%) |
| `deepseek-v4-flash` | hosted | **19%** | 99% | 100% | 16/16 | 320/320 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 16/16 | 308/320 (96%) |
| `gemma3:1b-it-qat` | ? | **6%** | 100% | 62% | 16/16 | 320/320 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 16/16 | 319/320 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |

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
| `mistralai/mistral-large-2512` | 10/10 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 10/10 | 6/6 |
| `minimax/minimax-m2.5` | 10/10 | 6/6 |
| `gemma3:1b-it-qat` | 10/10 | 0/6 |
| `google/gemini-3-flash-preview` | 10/10 | 6/6 |
| `claude-haiku-4-5-20251001` | 10/10 | 6/6 |
| `openai/gpt-oss-120b` | 10/10 | 6/6 |
| `openai/gpt-5-mini` | 10/10 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Neo Aeronautics, Inc.  | pre-money | easy | hosted |
| Rentberry Inc.  (CIK 0 | pre-money | easy | hosted, gemma3-1b-qat |
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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 81% | 16/16 | 320/320 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |

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
| `mistralai/mistral-large-2512` | 8/8 | 8/8 |
| `minimax/minimax-m2.5` | 8/8 | 8/8 |
| `gemma3:1b-it-qat` | 5/8 | 8/8 |
| `meta-llama/llama-3.3-70b-instruct` | 8/8 | 8/8 |
| `google/gemini-3-flash-preview` | 8/8 | 8/8 |
| `claude-haiku-4-5-20251001` | 8/8 | 8/8 |
| `openai/gpt-oss-120b` | 8/8 | 8/8 |
| `openai/gpt-5-mini` | 8/8 | 8/8 |

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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 97% | 85% | 13/13 | 259/260 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 13/13 | 253/260 (97%) |
| `gemma3:1b-it-qat` | ? | **8%** | 100% | 92% | 13/13 | 260/260 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 7/7 |
| `minimax/minimax-m2.5` | 6/6 | 7/7 |
| `gemma3:1b-it-qat` | 5/6 | 7/7 |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 7/7 |
| `google/gemini-3-flash-preview` | 6/6 | 7/7 |
| `claude-haiku-4-5-20251001` | 6/6 | 7/7 |
| `openai/gpt-oss-120b` | 6/6 | 7/7 |
| `openai/gpt-5-mini` | 6/6 | 7/7 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GIBRALTAR INDUSTRIES,  | double-trigger | hard | 1B |
| Vulcan Materials CO | double-trigger | hard | 1B |
| Nimble Storage Inc | single-trigger | medium | 1B |
| LogicMark, Inc. | single-trigger | easy | 1B |
| COMSCORE, INC. | single-trigger | hard | 1B, gemma3-1b-qat |
| REVVITY, INC. | single-trigger | easy | 1B |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `minimax/minimax-m2.5` | ? | **9%** | 97% | 82% | 11/11 | 180/220 (82%) |
| `gemma3:1b-it-qat` | ? | **9%** | 99% | 45% | 11/11 | 220/220 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 82% | 11/11 | 219/220 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `openai/gpt-oss-120b` | ? | **9%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |

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
| `mistralai/mistral-large-2512` | 4/6 | 5/5 |
| `meta-llama/llama-3.3-70b-instruct` | 4/6 | 5/5 |
| `minimax/minimax-m2.5` | 4/6 | 5/5 |
| `gemma3:1b-it-qat` | 0/6 | 5/5 |
| `google/gemini-3-flash-preview` | 4/6 | 5/5 |
| `claude-haiku-4-5-20251001` | 4/6 | 5/5 |
| `openai/gpt-oss-120b` | 4/6 | 5/5 |
| `openai/gpt-5-mini` | 4/6 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Banks.com, Inc. | stacked | medium | 1B |
| Teladoc, Inc. | stacked | easy | 1B |
| Zoom Video Communicati | pari-passu | hard | minimax-m2.5-or |
| VioQuest Pharmaceutica | pari-passu | easy | 1B, gemma3-1b-qat |
| RIGHT START INC /CA | pari-passu | medium | 1B |
| PRECOM TECHNOLOGY INC | pari-passu | hard | 1B, gpt-oss-120b-or |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 90% | 10/10 | 179/200 (90%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `gemma3:1b-it-qat` | ? | **70%** | 82% | 30% | 10/10 | 200/200 (100%) |
| `google/gemini-3-flash-preview` | ? | **10%** | 99% | 90% | 10/10 | 200/200 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 90% | 10/10 | 199/200 (100%) |

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
| `mistralai/mistral-large-2512` | 5/5 | 4/5 |
| `minimax/minimax-m2.5` | 5/5 | 4/5 |
| `meta-llama/llama-3.3-70b-instruct` | 5/5 | 4/5 |
| `gemma3:1b-it-qat` | 0/5 | 3/5 |
| `google/gemini-3-flash-preview` | 5/5 | 4/5 |
| `claude-haiku-4-5-20251001` | 5/5 | 4/5 |
| `openai/gpt-oss-120b` | 5/5 | 4/5 |
| `openai/gpt-5-mini` | 5/5 | 4/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MELINTA THERAPEUTICS,  | yes | easy | 1B, gemma3-1b-qat |
| Vertical Communication | yes | easy | gemma3-1b-qat |
| Lulu's Fashion Lounge  | yes | hard | 1B |
| ACME PACKET INC | yes | medium | gemma3-1b-qat |
| FITBIT INC | no | medium | gemma3-1b-qat |
| Akouos, Inc. | no | easy | gemma3-1b-qat |
| Workday, Inc. | no | hard | 1B, hosted, gemma3-1b-qat, gemini3-flash-or |
| ENDOSTIM, INC. | no | easy | 1B, gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–70% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
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
| `mistralai/mistral-large-2512` | ? | **10%** | 98% | 100% | 10/10 | 200/200 (100%) |
| `minimax/minimax-m2.5` | ? | **10%** | 97% | 100% | 10/10 | 187/200 (94%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma3:1b-it-qat` | ? | **30%** | 91% | 80% | 10/10 | 200/200 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `claude-haiku-4-5-20251001` | ? | **10%** | 96% | 90% | 10/10 | 200/200 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

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
| `minimax/minimax-m2.5` | 5/5 | 5/5 |
| `meta-llama/llama-3.3-70b-instruct` | 5/5 | 5/5 |
| `gemma3:1b-it-qat` | 3/5 | 5/5 |
| `google/gemini-3-flash-preview` | 5/5 | 5/5 |
| `claude-haiku-4-5-20251001` | 4/5 | 5/5 |
| `openai/gpt-oss-120b` | 5/5 | 5/5 |
| `openai/gpt-5-mini` | 5/5 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| AdaptHealth Corp. | yes | easy | gemma3-1b-qat |
| Lulu's Fashion Lounge  | yes | medium | 1B, gemma3-1b-qat |
| ENDOSTIM, INC. | yes | medium | gemma3-1b-qat |
| Tenable Holdings, Inc. | yes | medium | 1B |
| Pfenex Inc. | yes | hard | hosted, mistral-large-or, minimax-m2.5-or, haiku-4.5-direct |

## What this shows

- **Wobble spread: 0%–30% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `minimax/minimax-m2.5` | ? | **8%** | 96% | 92% | 12/12 | 216/240 (90%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 75% | 12/12 | 240/240 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 95% | 58% | 12/12 | 240/240 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 12/12 | 239/240 (100%) |
| `claude-haiku-4-5-20251001` | ? | **17%** | 92% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-oss-120b` | ? | **8%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `openai/gpt-5-mini` | ? | **17%** | 97% | 83% | 12/12 | 240/240 (100%) |

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
| `mistralai/mistral-large-2512` | 5/6 | 6/6 |
| `minimax/minimax-m2.5` | 5/6 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 3/6 | 6/6 |
| `gemma3:1b-it-qat` | 3/6 | 4/6 |
| `google/gemini-3-flash-preview` | 6/6 | 6/6 |
| `claude-haiku-4-5-20251001` | 6/6 | 6/6 |
| `openai/gpt-oss-120b` | 5/6 | 6/6 |
| `openai/gpt-5-mini` | 4/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| TRUMP ENTERTAINMENT RE | yes | easy | 1B, hosted, minimax-m2.5-or, haiku-4.5-direct, gpt-oss-120b-or, gpt5-mini-or |
| LOEWS CINEPLEX ENTERTA | yes | medium | 1B, gemma3-1b-qat |
| AVENTINE RENEWABLE ENE | yes | hard | haiku-4.5-direct, gpt5-mini-or |
| ACCELERON PHARMA INC | no | easy | gemma3-1b-qat |
| Yext, Inc. | no | easy | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 12/12 | 217/240 (90%) |
| `gemma3:1b-it-qat` | ? | **42%** | 93% | 92% | 12/12 | 240/240 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 4/6 |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 4/6 |
| `minimax/minimax-m2.5` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 5/6 | 6/6 |
| `google/gemini-3-flash-preview` | 6/6 | 4/6 |
| `claude-haiku-4-5-20251001` | 6/6 | 4/6 |
| `openai/gpt-oss-120b` | 6/6 | 6/6 |
| `openai/gpt-5-mini` | 6/6 | 4/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Symbion (Uniphy Health | yes | easy | gemma3-1b-qat |
| Aclarion | yes | easy | gemma3-1b-qat |
| Digirad | yes | hard | gemma3-1b-qat |
| Clearwire | no | easy | gemma3-1b-qat |
| Taylor Morrison (TMM H | no | easy | gemma3-1b-qat |
| MotivNation | no | hard | 1B, hosted |
| EntreMetrix | no | hard | 1B, hosted |

## What this shows

- **Wobble spread: 0%–42% across the ladder.** Lowest-wobble model: **minimax-m2.5-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 5.4 — Pro-rata right on future financings: granted vs not

**Corpus:** 12 real SEC-filed SAFEs, side letters and investors' rights agreements, human-validated answers (6 pro-rata / 6 absent/waived). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **33%** | 92% | 100% | 12/12 | 239/240 (100%) |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **8%** | 97% | 100% | 12/12 | 240/240 (100%) |
| `minimax/minimax-m2.5` | ? | **8%** | 99% | 100% | 12/12 | 226/240 (94%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gemma3:1b-it-qat` | ? | **17%** | 96% | 83% | 12/12 | 240/240 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-oss-120b` | ? | **17%** | 98% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 6/6 |
| `minimax/minimax-m2.5` | 6/6 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 4/6 | 6/6 |
| `google/gemini-3-flash-preview` | 6/6 | 6/6 |
| `claude-haiku-4-5-20251001` | 6/6 | 6/6 |
| `openai/gpt-oss-120b` | 6/6 | 6/6 |
| `openai/gpt-5-mini` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SOS Hydration Inc. | yes | medium | 1B, hosted, minimax-m2.5-or, gpt-oss-120b-or |
| Millennium Blockchain, | yes | medium | gemma3-1b-qat, gpt-oss-120b-or |
| Cantabio Pharmaceutica | yes | medium | mistral-large-or, gemma3-1b-qat |
| Supernus Pharmaceutica | no | easy | 1B |
| Infinity Pharmaceutica | no | easy | 1B |
| Xcyte Therapies, Inc. | no | hard | 1B |

## What this shows

- **Wobble spread: 0%–33% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `minimax/minimax-m2.5` | ? | **17%** | 95% | 100% | 12/12 | 223/240 (93%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **8%** | 97% | 100% | 12/12 | 240/240 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 96% | 92% | 12/12 | 240/240 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-oss-120b` | ? | **8%** | 98% | 92% | 12/12 | 240/240 (100%) |
| `openai/gpt-5-mini` | ? | **17%** | 98% | 92% | 12/12 | 240/240 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 6/6 |
| `minimax/minimax-m2.5` | 6/6 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 6/6 | 5/6 |
| `google/gemini-3-flash-preview` | 6/6 | 6/6 |
| `claude-haiku-4-5-20251001` | 6/6 | 6/6 |
| `openai/gpt-oss-120b` | 6/6 | 5/6 |
| `openai/gpt-5-mini` | 6/6 | 5/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| NorthStar Healthcare I | yes | easy | llama3.3-70b-or, gemma3-1b-qat |
| Interval Leisure Group | yes | medium | 1B, gemma3-1b-qat, gpt-oss-120b-or |
| Atossa Genetics Inc. | no | easy | gemma3-1b-qat |
| Clarcor Inc. | no | hard | minimax-m2.5-or, gpt5-mini-or |
| World Heart Corp | no | hard | 1B, minimax-m2.5-or, gpt5-mini-or |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).

---

## Test 5.2 — Protective provisions: investor class-veto right present vs absent

**Corpus:** 12 real SEC-filed charters and governance documents, human-validated answers (6 veto-right / 6 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 97% | 58% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `minimax/minimax-m2.5` | ? | **17%** | 93% | 92% | 12/12 | 215/240 (90%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gemma3:1b-it-qat` | ? | **42%** | 95% | 75% | 12/12 | 238/240 (99%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-oss-120b` | ? | **17%** | 99% | 92% | 12/12 | 240/240 (100%) |
| `openai/gpt-5-mini` | ? | **17%** | 99% | 100% | 12/12 | 240/240 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 6/6 |
| `minimax/minimax-m2.5` | 5/6 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 3/6 | 6/6 |
| `google/gemini-3-flash-preview` | 6/6 | 6/6 |
| `claude-haiku-4-5-20251001` | 6/6 | 6/6 |
| `openai/gpt-oss-120b` | 5/6 | 6/6 |
| `openai/gpt-5-mini` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Gitlab Inc. | yes | easy | gemma3-1b-qat |
| BroadSoft, Inc. | yes | medium | minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or, gpt5-mini-or |
| SCYNEXIS, Inc. | yes | medium | 1B, gemma3-1b-qat |
| JCM Partners, LLC | yes | medium | minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or, gpt5-mini-or |
| UCP Holdings, Inc. | no | easy | gemma3-1b-qat |
| Non-binding LOI (Omni  | no | easy | 1B |

## What this shows

- **Wobble spread: 0%–42% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 5.3 — Information rights: live financial-reporting obligation vs absent

**Corpus:** 12 real SEC-filed investors' rights agreements and equity-award docs, human-validated answers (6 info-rights / 6 absent/waived). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 96% | 50% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `google/gemma-4-31b-it` | ? | **8%** | 98% | 92% | 12/12 | 240/240 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 92% | 12/12 | 236/240 (98%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gemma3:1b-it-qat` | ? | **17%** | 99% | 50% | 12/12 | 240/240 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `openai/gpt-oss-120b` | ? | **8%** | 98% | 92% | 12/12 | 240/240 (100%) |
| `openai/gpt-5-mini` | ? | **8%** | 98% | 100% | 12/12 | 240/240 (100%) |

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
| `mistralai/mistral-large-2512` | 5/6 | 6/6 |
| `minimax/minimax-m2.5` | 5/6 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 5/6 | 6/6 |
| `gemma3:1b-it-qat` | 6/6 | 0/6 |
| `google/gemini-3-flash-preview` | 5/6 | 6/6 |
| `claude-haiku-4-5-20251001` | 6/6 | 6/6 |
| `openai/gpt-oss-120b` | 5/6 | 6/6 |
| `openai/gpt-5-mini` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Bell Microproducts Inc | yes | hard | gemma4-31b-or, gpt-oss-120b-or, gpt5-mini-or |
| Speedway Motorsports,  | no | easy | 1B |
| TSFG (The South Financ | no | easy | gemma3-1b-qat |
| Pool Corp | no | easy | 1B, gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **haiku-4.5-direct** (0% wobble, 100% accuracy).

---

## Test 5.7 — Vesting acceleration: granted on trigger vs absent

**Corpus:** 9 real SEC-filed equity-award agreements and proxy disclosures, human-validated answers (6 accelerates / 3 no-acceleration). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 67% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 44% | 9/9 | 174/180 (97%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 3/3 |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 3/3 |
| `minimax/minimax-m2.5` | 6/6 | 3/3 |
| `gemma3:1b-it-qat` | 2/6 | 2/3 |
| `google/gemini-3-flash-preview` | 6/6 | 3/3 |
| `claude-haiku-4-5-20251001` | 6/6 | 3/3 |
| `openai/gpt-oss-120b` | 6/6 | 3/3 |
| `openai/gpt-5-mini` | 6/6 | 3/3 |

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
| `gemma3:1b` | 1B | **67%** | 94% | 0% | 9/9 | 178/180 (99%) |
| `deepseek-v4-flash` | hosted | **33%** | 92% | 67% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **11%** | 99% | 67% | 9/9 | 180/180 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 67% | 9/9 | 158/180 (88%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **11%** | 96% | 67% | 9/9 | 180/180 (100%) |
| `gemma3:1b-it-qat` | ? | **78%** | 72% | 44% | 9/9 | 180/180 (100%) |
| `google/gemini-3-flash-preview` | ? | **11%** | 97% | 67% | 9/9 | 180/180 (100%) |
| `claude-haiku-4-5-20251001` | ? | **11%** | 97% | 78% | 9/9 | 180/180 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |

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
| `minimax/minimax-m2.5` | — | 2/3 | 1/3 | 3/3 | — |
| `meta-llama/llama-3.3-70b-instruct` | — | 2/3 | 1/3 | 3/3 | — |
| `gemma3:1b-it-qat` | — | 1/3 | 1/3 | 2/3 | — |
| `google/gemini-3-flash-preview` | — | 2/3 | 1/3 | 3/3 | — |
| `claude-haiku-4-5-20251001` | — | 2/3 | 2/3 | 3/3 | — |
| `openai/gpt-oss-120b` | — | 2/3 | 1/3 | 3/3 | — |
| `openai/gpt-5-mini` | — | 2/3 | 1/3 | 3/3 | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| COUNTERPATH CORP  (CIK | 1x | easy | 1B, gemma3-1b-qat |
| BIOVENTRIX, INC.  (CIK | 1x | easy | gemma3-1b-qat |
| Revance Therapeutics,  | 1x | easy | 1B, gemma3-1b-qat |
| Oportun Financial Corp | 2x | easy | 1B, hosted, mistral-large-or, llama3.3-70b-or, gemma3-1b-qat, haiku-4.5-direct |
| Pagaya Technologies Lt | 2x | easy | 1B, hosted, gemma3-1b-qat |
| 24/7 REAL MEDIA INC  ( | 3x | easy | 1B |
| BECEEM COMMUNICATIONS  | 3x | easy | 1B, gemma3-1b-qat |
| CASTLE BIOSCIENCES INC | 3x | easy | hosted, gemma3-1b-qat, gemini3-flash-or |

## What this shows

- **Wobble spread: 0%–78% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 67% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 5.1 — Board seats: number an investor has the right to designate

**Corpus:** 9 real SEC-filed voting/shareholders'/designation agreements, human-validated answers (values range 1-9). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 92% | 78% | 9/9 | 179/180 (99%) |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 78% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **33%** | 94% | 67% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **22%** | 99% | 44% | 9/9 | 180/180 (100%) |
| `minimax/minimax-m2.5` | ? | **44%** | 94% | 67% | 9/9 | 165/180 (92%) |
| `gemma3:1b-it-qat` | ? | **33%** | 93% | 100% | 9/9 | 180/180 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **33%** | 98% | 44% | 9/9 | 180/180 (100%) |
| `google/gemini-3-flash-preview` | ? | **11%** | 97% | 78% | 9/9 | 180/180 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 78% | 9/9 | 180/180 (100%) |
| `openai/gpt-oss-120b` | ? | **11%** | 99% | 78% | 9/9 | 180/180 (100%) |
| `openai/gpt-5-mini` | ? | **44%** | 92% | 78% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SICOR Inc. | 3 | easy | 1B |
| Dollar General Corpora | 1 | medium | 1B, gemma3-1b-qat, llama3.3-70b-or |
| Emergent Capital, Inc. | 3 | medium | minimax-m2.5-or, gpt5-mini-or |
| Ute Energy Corporation | 1 | medium | 1B, gemma4-31b-or, mistral-large-or, minimax-m2.5-or, gemma3-1b-qat, llama3.3-70b-or, gpt5-mini-or |
| Ute Energy Corporation | 2 | medium | 1B, gemma4-31b-or, minimax-m2.5-or, gemma3-1b-qat, llama3.3-70b-or, gemini3-flash-or, gpt5-mini-or |
| Cinemark Holdings, Inc | 5 | easy | gemma4-31b-or, mistral-large-or, minimax-m2.5-or, gpt-oss-120b-or, gpt5-mini-or |
| Cinemark Holdings, Inc | 9 | hard | hosted |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **haiku-4.5-direct** (0% wobble, 78% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.6 — SAFE pro-rata side letter: granted vs absent

**Corpus:** 15 real SEC-filed SAFEs and pro-rata side letters, human-validated answers (9 pro-rata / 6 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **33%** | 97% | 93% | 15/15 | 300/300 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 15/15 | 297/300 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `gemma3:1b-it-qat` | ? | **27%** | 96% | 100% | 15/15 | 300/300 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 15/15 | 299/300 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |

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
| `mistralai/mistral-large-2512` | 9/9 | 6/6 |
| `minimax/minimax-m2.5` | 9/9 | 6/6 |
| `meta-llama/llama-3.3-70b-instruct` | 9/9 | 6/6 |
| `gemma3:1b-it-qat` | 9/9 | 6/6 |
| `google/gemini-3-flash-preview` | 9/9 | 6/6 |
| `claude-haiku-4-5-20251001` | 9/9 | 6/6 |
| `openai/gpt-oss-120b` | 9/9 | 6/6 |
| `openai/gpt-5-mini` | 9/9 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SNM Global Holdings, I | yes | easy | 1B |
| SNM Global Holdings, I | yes | easy | 1B, gemma3-1b-qat |
| Parker Clay Global, PB | yes | hard | gemma3-1b-qat |
| SOS Hydration Inc. | yes | hard | 1B, gemma3-1b-qat |
| Rare Earths Americas,  | no | easy | 1B |
| TaoWeave, Inc. | no | hard | 1B, gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–33% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.1.2 — Priced round basis: pre-money vs post-money

**Corpus:** 19 real SEC-filed priced-round financing documents, human-validated answers (13 pre / 6 post). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 82% | 68% | 19/19 | 376/380 (99%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 95% | 19/19 | 349/380 (92%) |
| `gemma3:1b-it-qat` | ? | **32%** | 93% | 63% | 19/19 | 380/380 (100%) |
| `google/gemini-3-flash-preview` | ? | **5%** | 98% | 95% | 19/19 | 380/380 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `openai/gpt-oss-120b` | ? | **5%** | 98% | 95% | 19/19 | 380/380 (100%) |
| `openai/gpt-5-mini` | ? | **11%** | 98% | 100% | 19/19 | 380/380 (100%) |

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
| `mistralai/mistral-large-2512` | 13/13 | 5/6 |
| `meta-llama/llama-3.3-70b-instruct` | 13/13 | 5/6 |
| `minimax/minimax-m2.5` | 13/13 | 5/6 |
| `gemma3:1b-it-qat` | 6/13 | 6/6 |
| `google/gemini-3-flash-preview` | 13/13 | 5/6 |
| `claude-haiku-4-5-20251001` | 13/13 | 5/6 |
| `openai/gpt-oss-120b` | 13/13 | 5/6 |
| `openai/gpt-5-mini` | 13/13 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Viking Therapeutics, I | pre-money | easy | 1B, gemma3-1b-qat |
| Rules-Based Medicine I | pre-money | easy | 1B, gemma3-1b-qat |
| SUNESIS PHARMACEUTICAL | pre-money | easy | 1B |
| RMG Acquisition Corp.  | pre-money | easy | 1B, gemma3-1b-qat, gpt5-mini-or |
| Ucommune Group Holding | pre-money | easy | 1B |
| VIEWRAY INC | pre-money | easy | 1B, gemma3-1b-qat |
| Cytosorbents Corp | pre-money | medium | 1B |
| GreenCell, Inc | pre-money | medium | 1B |
| BIOLARGO, INC. | pre-money | medium | 1B |
| Cytosorbents Corp | pre-money | medium | 1B |
| HAGUE CORP. | pre-money | easy | 1B |
| SOCIETY PASS INCORPORA | pre-money | easy | 1B, gemma3-1b-qat |
| HAGUE CORP. | pre-money | easy | 1B |
| PROVECTUS BIOPHARMACEU | post-money | easy | 1B |
| Fold Holdings, Inc. | post-money | easy | 1B |
| New Global Energy, Inc | post-money | easy | 1B, gemma3-1b-qat, gemini3-flash-or, gpt-oss-120b-or, gpt5-mini-or |
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
| `gemma3:1b` | 1B | **29%** | 98% | 57% | 7/7 | 140/140 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 7/7 | 136/140 (97%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 86% | 7/7 | 140/140 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 57% | 7/7 | 140/140 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

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
| `mistralai/mistral-large-2512` | 4/4 | 3/3 |
| `minimax/minimax-m2.5` | 4/4 | 3/3 |
| `meta-llama/llama-3.3-70b-instruct` | 3/4 | 3/3 |
| `gemma3:1b-it-qat` | 4/4 | 0/3 |
| `google/gemini-3-flash-preview` | 4/4 | 3/3 |
| `claude-haiku-4-5-20251001` | 4/4 | 3/3 |
| `openai/gpt-oss-120b` | 4/4 | 3/3 |
| `openai/gpt-5-mini` | 4/4 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
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
| `gemma3:1b` | 1B | **0%** | 100% | 25% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 98% | 75% | 4/4 | 80/80 (100%) |
| `google/gemini-3-flash-preview` | ? | **25%** | 98% | 100% | 4/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Remark Holdings, Inc.  | 5000000 | easy | gemma3-1b-qat, gemini3-flash-or |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none

**Corpus:** 5 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (2 full-ratchet / 2 weighted-avg / 0 broad-based / 0 narrow-based / 1 none). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 99% | 40% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **40%** | 89% | 60% | 5/5 | 100/100 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

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
| `minimax/minimax-m2.5` | 2/2 | 2/2 | — | — | 1/1 |
| `gemma3:1b-it-qat` | 2/2 | 1/2 | — | — | 0/1 |
| `meta-llama/llama-3.3-70b-instruct` | 2/2 | 2/2 | — | — | 1/1 |
| `google/gemini-3-flash-preview` | 2/2 | 2/2 | — | — | 1/1 |
| `claude-haiku-4-5-20251001` | 2/2 | 2/2 | — | — | 1/1 |
| `openai/gpt-oss-120b` | 2/2 | 2/2 | — | — | 1/1 |
| `openai/gpt-5-mini` | 2/2 | 2/2 | — | — | 1/1 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VISIUM TECHNOLOGIES, I | weighted-average | medium | gemma3-1b-qat |
| CROSSROADS SYSTEMS INC | full-ratchet | medium | 1B |
| RASER TECHNOLOGIES INC | weighted-average | medium | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.3 — Risk flag: uncapped participating-preferred present vs absent

**Corpus:** 13 real SEC-filed preferred-stock liquidation/participation clauses, human-validated answers (4 uncapped / 9 capped/none). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **8%** | 99% | 31% | 13/13 | 255/260 (98%) |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 77% | 13/13 | 260/260 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 85% | 13/13 | 227/260 (87%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 77% | 13/13 | 260/260 (100%) |
| `gemma3:1b-it-qat` | ? | **8%** | 100% | 62% | 13/13 | 260/260 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 77% | 13/13 | 260/260 (100%) |
| `claude-haiku-4-5-20251001` | ? | **8%** | 98% | 69% | 13/13 | 260/260 (100%) |
| `openai/gpt-oss-120b` | ? | **8%** | 96% | 85% | 13/13 | 259/260 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 85% | 13/13 | 260/260 (100%) |

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
| `mistralai/mistral-large-2512` | 2/4 | 9/9 |
| `minimax/minimax-m2.5` | 2/4 | 9/9 |
| `meta-llama/llama-3.3-70b-instruct` | 2/4 | 8/9 |
| `gemma3:1b-it-qat` | 0/4 | 8/9 |
| `google/gemini-3-flash-preview` | 2/4 | 8/9 |
| `claude-haiku-4-5-20251001` | 2/4 | 7/9 |
| `openai/gpt-oss-120b` | 2/4 | 9/9 |
| `openai/gpt-5-mini` | 2/4 | 9/9 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Jazz Semiconductor Inc | no | medium | hosted |
| Workday, Inc. | no | medium | 1B |
| Internet Security Syst | no | medium | gemma3-1b-qat |
| BioAccelerate Holdings | no | hard | haiku-4.5-direct, gpt-oss-120b-or |

## What this shows

- **Wobble spread: 0%–8% across the ladder.** Lowest-wobble model: **mistral-large-or** (0% wobble, 85% accuracy).

---

## Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent

**Corpus:** 7 real SEC-filed SAFE agreements, human-validated answers (4 MFN / 3 absent). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 98% | 100% | 7/7 | 140/140 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 7/7 | 136/140 (97%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 57% | 7/7 | 140/140 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

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
| `mistralai/mistral-large-2512` | 4/4 | 3/3 |
| `minimax/minimax-m2.5` | 4/4 | 3/3 |
| `meta-llama/llama-3.3-70b-instruct` | 4/4 | 3/3 |
| `gemma3:1b-it-qat` | 1/4 | 3/3 |
| `google/gemini-3-flash-preview` | 4/4 | 3/3 |
| `claude-haiku-4-5-20251001` | 4/4 | 3/3 |
| `openai/gpt-oss-120b` | 4/4 | 3/3 |
| `openai/gpt-5-mini` | 4/4 | 3/3 |

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
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 3/3 | 59/60 (98%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 100% | 3/3 | 54/60 (90%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |

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
| `gemma3:1b` | 1B | **43%** | 85% | 71% | 7/7 | 134/140 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 7/7 | 139/140 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma3:1b-it-qat` | ? | **43%** | 93% | 57% | 7/7 | 132/140 (94%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Medecision, Inc. | 0.03 | easy | 1B |
| Medecision, Inc. | 0.25 | easy | gemma3-1b-qat |
| WhiteGlove Health, Inc | 0.61 | easy | gemma3-1b-qat |
| Medecision, Inc. | 1.25 | medium | 1B, gemma3-1b-qat |
| Medecision, Inc. | 2.0 | medium | 1B |

## What this shows

- **Wobble spread: 0%–43% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.1 — SAFE valuation cap extraction

**Corpus:** 8 real SEC-filed SAFE agreements, human-validated answers (values range 15000000-150000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 96% | 88% | 8/8 | 150/160 (94%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 8/8 | 158/160 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 94% | 88% | 8/8 | 160/160 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Complete Solaria, Inc. | 53540000 | medium | gemma3-1b-qat |
| Lomond Therapeutics Ho | 100000000 | medium | 1B |
| Invizyne Technologies  | 100000000 | hard | 1B, gemma3-1b-qat |
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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

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

## Test 2.1.2 — SAFE discount rate extraction

**Corpus:** 9 real SEC-filed SAFE agreements, human-validated answers (values range 10-50). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 90% | 56% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax/minimax-m2.5` | ? | **44%** | 92% | 78% | 9/9 | 173/180 (96%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma3:1b-it-qat` | ? | **44%** | 93% | 33% | 9/9 | 180/180 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `openai/gpt-oss-120b` | ? | **22%** | 99% | 100% | 9/9 | 180/180 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Creci Inc. | 20 | medium | gemma3-1b-qat, gpt-oss-120b-or |
| Complete Solaria, Inc. | 20 | easy | 1B, minimax-m2.5-or |
| Lomond Therapeutics Ho | 10 | hard | minimax-m2.5-or |
| Maison Luxe, Inc. | 20 | easy | 1B, minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or |
| SNM Global Holdings, I | 50 | medium | gemma3-1b-qat |
| Parker Clay Global, PB | 15 | medium | 1B, minimax-m2.5-or |
| SOS Hydration Inc. | 50 | hard | 1B, gemma3-1b-qat |

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
| `gemma3:1b` | 1B | **50%** | 90% | 75% | 4/4 | 75/80 (94%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 91% | 100% | 4/4 | 80/80 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Damon Motors Inc. | 125000000 | easy | 1B, gemma3-1b-qat |
| Greenfield Robotics Co | 30000000 | easy | 1B |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 83/100 (83%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **40%** | 86% | 60% | 5/5 | 95/100 (95%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Loop Industries, Inc. | 1 | easy | gemma3-1b-qat |
| Air Defense Services,  | 100 | medium | hosted, gpt5-mini-or |
| Boston Life Sciences,  | 8000 | hard | 1B, gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 10/10 | 195/200 (98%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 70% | 10/10 | 200/200 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

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
| `mistralai/mistral-large-2512` | 3/3 | 4/4 | 3/3 |
| `minimax/minimax-m2.5` | 3/3 | 4/4 | 3/3 |
| `gemma3:1b-it-qat` | 3/3 | 4/4 | 0/3 |
| `meta-llama/llama-3.3-70b-instruct` | 3/3 | 4/4 | 3/3 |
| `google/gemini-3-flash-preview` | 3/3 | 4/4 | 3/3 |
| `claude-haiku-4-5-20251001` | 3/3 | 4/4 | 3/3 |
| `openai/gpt-oss-120b` | 3/3 | 4/4 | 3/3 |
| `openai/gpt-5-mini` | 3/3 | 4/4 | 3/3 |

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

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 97/100 (97%) |
| `gemma3:1b-it-qat` | ? | **40%** | 89% | 80% | 5/5 | 100/100 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Asana, Inc. | 100000000 | easy | gemma3-1b-qat |
| TerraScend Corp. | 30000000 | medium | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.2 — Convertible note interest rate extraction

**Corpus:** 6 real SEC-filed convertible promissory notes, human-validated answers (values range 0.28-10.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 83% | 6/6 | 118/120 (98%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gemma3:1b-it-qat` | ? | **83%** | 70% | 83% | 6/6 | 115/120 (96%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ACOLOGY, INC. | 0.28 | easy | gemma3-1b-qat |
| VERITAS Farms Inc. | 10.0 | easy | gemma3-1b-qat |
| Golden Matrix Group, I | 8.0 | easy | gemma3-1b-qat |
| LanzaTech Global, Inc. | 8.0 | easy | gemma3-1b-qat |
| XTI Aerospace Inc. | 10.0 | medium | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–83% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)

**Corpus:** 13 real SEC-filed SAFE (Simple Agreement for Future Equity) instruments, human-validated answers (2 cap / 1 discount / 10 both-mfn). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **54%** | 88% | 77% | 13/13 | 252/260 (97%) |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 13/13 | 221/260 (85%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 13/13 | 248/260 (95%) |
| `gemma3:1b-it-qat` | ? | **62%** | 86% | 54% | 13/13 | 260/260 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 13/13 | 258/260 (99%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |

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
| `mistralai/mistral-large-2512` | 2/2 | 1/1 | 10/10 |
| `meta-llama/llama-3.3-70b-instruct` | 2/2 | 1/1 | 10/10 |
| `minimax/minimax-m2.5` | 2/2 | 1/1 | 10/10 |
| `gemma3:1b-it-qat` | 1/2 | 0/1 | 6/10 |
| `google/gemini-3-flash-preview` | 2/2 | 1/1 | 10/10 |
| `claude-haiku-4-5-20251001` | 2/2 | 1/1 | 10/10 |
| `openai/gpt-oss-120b` | 2/2 | 1/1 | 10/10 |
| `openai/gpt-5-mini` | 2/2 | 1/1 | 10/10 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SNM Global Holdings, I | discount | easy | 1B |
| Parker Clay Global, PB | both-mfn | medium | 1B, gemma3-1b-qat |
| Maison Luxe, Inc. | both-mfn | medium | 1B, gemma3-1b-qat |
| Rentberry Inc. | both-mfn | medium | 1B, gemma3-1b-qat |
| Creci Inc. | both-mfn | medium | 1B, gemma3-1b-qat |
| Lomond Therapeutics Ho | both-mfn | medium | 1B, gemma3-1b-qat |
| Neo Aeronautics, Inc. | both-mfn | medium | gemma3-1b-qat |
| Manako Labs Ltd | both-mfn | medium | hosted, gemma3-1b-qat |
| Gardedam Therapeutics  | cap | medium | 1B, gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–62% across the ladder.** Lowest-wobble model: **gemma4-31b-or** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.1.3 — Priced-round price-per-share extraction

**Corpus:** 8 real SEC-filed stock purchase agreements / charters / offerings, human-validated answers (values range 0.2-1000.0). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 91% | 62% | 8/8 | 160/160 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 62% | 8/8 | 147/160 (92%) |
| `google/gemma-4-31b-it` | ? | **12%** | 96% | 75% | 8/8 | 160/160 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 62% | 8/8 | 160/160 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 75% | 8/8 | 151/160 (94%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 75% | 8/8 | 160/160 (100%) |
| `gemma3:1b-it-qat` | ? | **50%** | 91% | 62% | 8/8 | 160/160 (100%) |
| `google/gemini-3-flash-preview` | ? | **12%** | 95% | 75% | 8/8 | 160/160 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 62% | 8/8 | 160/160 (100%) |
| `openai/gpt-oss-120b` | ? | **12%** | 97% | 75% | 8/8 | 160/160 (100%) |
| `openai/gpt-5-mini` | ? | **12%** | 94% | 62% | 8/8 | 160/160 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Astea International In | 3.63 | easy | 1B, gemma3-1b-qat |
| Kiwa Bio-Tech Products | 1.3 | medium | 1B, gemma3-1b-qat |
| Gelesis, Inc. | 1.26 | medium | gemma4-31b-or, gemini3-flash-or, gpt-oss-120b-or, gpt5-mini-or |
| Elicio Therapeutics, I | 1.0 | easy | gemma3-1b-qat |
| WhiteGlove Health, Inc | 0.2 | easy | 1B |
| Geos Communications, I | 0.625 | medium | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **minimax-m2.5-or** (0% wobble, 75% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.3 — Convertible note maturity date extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 2005-03-31-2026-12-31). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 95% | 50% | 4/4 | 79/80 (99%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 4/4 | 79/80 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **50%** | 95% | 75% | 4/4 | 80/80 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GARDENBURGER, INC. | 2005-03-31 | easy | 1B, gemma3-1b-qat |
| ACOLOGY, INC. | 2015-03-04 | medium | 1B, gemma4-31b-or, llama3.3-70b-or, gemini3-flash-or, haiku-4.5-direct, gpt-oss-120b-or |
| VERITAS Farms Inc. | 2026-10-01 | medium | gemma3-1b-qat |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 4/4 | 71/80 (89%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 99% | 0% | 4/4 | 59/80 (74%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Greenfield Robotics Co | 20.0 | easy | gemma3-1b-qat |
| ACOLOGY, INC. | 50.0 | easy | 1B |
| HepaLife Technologies, | 5.0 | medium | 1B, haiku-4.5-direct |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).

---

## Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction

**Corpus:** 2 real SEC-filed convertible promissory notes, human-validated answers (values range 10000000-40000000). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 97% | 100% | 2/2 | 38/40 (95%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 2/2 | 36/40 (90%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | ? | **50%** | 92% | 100% | 2/2 | 33/40 (82%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Valkyrie Sciences Hold | 10000000 | medium | 1B, gemma3-1b-qat |

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
| `gemma3:1b` | 1B | **22%** | 89% | 33% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 100% | 9/9 | 180/180 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **11%** | 94% | 78% | 9/9 | 180/180 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax/minimax-m2.5` | ? | **11%** | 99% | 100% | 9/9 | 131/180 (73%) |
| `gemma3:1b-it-qat` | ? | **22%** | 89% | 33% | 9/9 | 180/180 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `openai/gpt-oss-120b` | ? | **11%** | 99% | 89% | 9/9 | 180/180 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CONOR MEDSYSTEMS, INC. | 1.5yr/no-cliff | medium | 1B, gemma3-1b-qat |
| CLARCOR INC. | 4yr/no-cliff | hard | 1B, hosted, minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or |
| WORLD HEART CORP | 4yr/1yr-cliff | hard | mistral-large-or |

## What this shows

- **Wobble spread: 0%–22% across the ladder.** Lowest-wobble model: **llama3.3-70b-or** (0% wobble, 100% accuracy).

---

## Test 3.1 — Cap-table current ownership percentage (compute)

**Corpus:** 9 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-33.9). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 18% | 0% | 9/9 | 177/180 (98%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 179/180 (99%) |
| `google/gemma-4-31b-it` | ? | **22%** | 97% | 100% | 9/9 | 180/180 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 63% | 0% | 9/9 | 180/180 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `claude-haiku-4-5-20251001` | ? | **11%** | 99% | 89% | 9/9 | 180/180 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 9/9 | 174/180 (97%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | 1B, gemma3-1b-qat, haiku-4.5-direct |
| Uber Technologies, Inc | 11.0 | easy | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 2.4 | medium | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 8.6 | easy | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 5.4 | medium | 1B, gemma4-31b-or, gemma3-1b-qat |
| Uber Technologies, Inc | 16.3 | medium | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 5.2 | medium | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 5.3 | medium | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 33.9 | hard | 1B, gemma4-31b-or, gemma3-1b-qat |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 3/3 | 59/60 (98%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 63% | 0% | 3/3 | 60/60 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `claude-haiku-4-5-20251001` | ? | **33%** | 98% | 67% | 3/3 | 60/60 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | 1B, gemma3-1b-qat, haiku-4.5-direct |
| Uber Technologies, Inc | 8.6 | easy | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 2.4 | medium | 1B, gemma3-1b-qat |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 92% | 0% | 4/4 | 80/80 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **25%** | 99% | 100% | 4/4 | 68/80 (85%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 4/4 | 65/80 (81%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 16.3 | easy | 1B |
| Uber Technologies, Inc | 11.0 | easy | 1B, gemma3-1b-qat |
| Uber Technologies, Inc | 5.3 | medium | 1B, gpt-oss-120b-or |
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
| `gemma3:1b` | 1B | **100%** | 45% | 0% | 1/1 | 20/20 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `minimax/minimax-m2.5` | ? | **100%** | 93% | 100% | 1/1 | 14/20 (70%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 90% | 0% | 1/1 | 20/20 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `openai/gpt-oss-120b` | ? | **100%** | 85% | 100% | 1/1 | 20/20 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 1/1 | 18/20 (90%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 9.5 | easy | 1B, minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or |

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
| `gemma3:1b` | 1B | **40%** | 86% | 100% | 10/10 | 171/200 (86%) |
| `deepseek-v4-flash` | hosted | **30%** | 96% | 100% | 10/10 | 200/200 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 70% | 10/10 | 200/200 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `minimax/minimax-m2.5` | ? | **40%** | 90% | 100% | 10/10 | 152/200 (76%) |
| `gemma3:1b-it-qat` | ? | **30%** | 90% | 60% | 10/10 | 200/200 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-oss-120b` | ? | **10%** | 99% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-5-mini` | ? | **10%** | 99% | 100% | 10/10 | 200/200 (100%) |

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
| `mistralai/mistral-large-2512` | 6/6 | 1/4 | — | — | — |
| `meta-llama/llama-3.3-70b-instruct` | 6/6 | 4/4 | — | — | — |
| `minimax/minimax-m2.5` | 6/6 | 4/4 | — | — | — |
| `gemma3:1b-it-qat` | 6/6 | 0/4 | — | — | — |
| `google/gemini-3-flash-preview` | 6/6 | 4/4 | — | — | — |
| `claude-haiku-4-5-20251001` | 6/6 | 4/4 | — | — | — |
| `openai/gpt-oss-120b` | 6/6 | 4/4 | — | — | — |
| `openai/gpt-5-mini` | 6/6 | 4/4 | — | — | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VoCare, Inc. | 506c | medium | 1B, hosted |
| Handybook, Inc. | 506b | medium | minimax-m2.5-or |
| Brewer Lane Ventures F | 506c | medium | 1B, hosted, minimax-m2.5-or, gemma3-1b-qat |
| Material Impact Fund I | 506c | medium | 1B, minimax-m2.5-or, gemma3-1b-qat |
| NextView Ventures V, L | 506c | medium | 1B, hosted, minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or |
| McBride Sisters Collec | 506b | medium | gpt5-mini-or |

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
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 2/2 | 39/40 (98%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **50%** | 88% | 100% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 50% | 2/2 | 40/40 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| NETBASE SOLUTIONS INC  | 2,366,532 | medium | llama3.3-70b-or |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **1B** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 30% | 10/10 | 200/200 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 10/10 | 199/200 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VoCare, Inc. | 5000000 | ? | 1B |
| McBride Sisters Collec | 14040000 | ? | 1B |
| POSEIDON MEDICAL INC. | 6085780 | ? | 1B |
| BEYONDCORE, INC. | 8881213 | ? | 1B |
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
| `gemma3:1b` | 1B | **33%** | 88% | 100% | 6/6 | 115/120 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 6/6 | 119/120 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gemma3:1b-it-qat` | ? | **33%** | 94% | 100% | 6/6 | 119/120 (99%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Exela Technologies, In | 10 | ? | 1B, gemma3-1b-qat |
| scPharmaceuticals Inc. | 6 | ? | 1B |
| Zoom Video Communicati | 6 | ? | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–33% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **20%** | 90% | 80% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **60%** | 69% | 0% | 5/5 | 100/100 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Civitas Solutions, Inc | 32.89 | ? | llama3.3-70b-or, gpt-oss-120b-or |
| HyreCar Inc. | 2.09 | ? | 1B, gemma3-1b-qat |
| Castle Biosciences, In | 28.82 | ? | 1B |
| Veritone, Inc. | 14.9 | ? | 1B, gemma3-1b-qat |
| Axcella Health Inc. | 1.96 | ? | 1B, gemma3-1b-qat |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 8/8 | 157/160 (98%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gemma3:1b-it-qat` | ? | **38%** | 91% | 62% | 8/8 | 160/160 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |

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
| `mistralai/mistral-large-2512` | 4/4 | 4/4 |
| `minimax/minimax-m2.5` | 4/4 | 4/4 |
| `meta-llama/llama-3.3-70b-instruct` | 4/4 | 4/4 |
| `gemma3:1b-it-qat` | 4/4 | 1/4 |
| `google/gemini-3-flash-preview` | 4/4 | 4/4 |
| `claude-haiku-4-5-20251001` | 4/4 | 4/4 |
| `openai/gpt-oss-120b` | 4/4 | 4/4 |
| `openai/gpt-5-mini` | 4/4 | 4/4 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Actelis Networks, Inc. | fully-diluted | ? | 1B |
| Sybari Software, Inc. | fully-diluted | ? | 1B |
| Emageon Inc. | fully-diluted | ? | 1B |
| IGN Entertainment, Inc | fully-diluted | ? | 1B |
| Actelis Networks, Inc. | issued-outstanding | ? | 1B |
| IGN Entertainment, Inc | issued-outstanding | ? | 1B, gemma3-1b-qat |
| HyreCar Inc. | issued-outstanding | ? | 1B, gemma3-1b-qat |
| Castle Biosciences, In | issued-outstanding | ? | 1B, gemma3-1b-qat |

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
| `gemma3:1b` | 1B | **60%** | 84% | 20% | 5/5 | 99/100 (99%) |
| `deepseek-v4-flash` | hosted | **20%** | 97% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **20%** | 92% | 80% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **40%** | 94% | 100% | 5/5 | 80/100 (80%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **40%** | 84% | 20% | 5/5 | 85/100 (85%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **40%** | 85% | 80% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **20%** | 98% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Civitas Solutions, Inc | 1123118 | ? | 1B, gpt-oss-120b-or |
| IGN Entertainment, Inc | 17541 | ? | mistral-large-or |
| Castle Biosciences, In | 22786 | ? | hosted |
| Emageon Inc. | 12619 | ? | 1B, minimax-m2.5-or, gemma3-1b-qat |
| HyreCar Inc. | 9777079 | ? | 1B, minimax-m2.5-or, gemma3-1b-qat, gpt-oss-120b-or, gpt5-mini-or |

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
| `gemma3:1b` | 1B | **0%** | 100% | 60% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **20%** | 93% | 80% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 74% | 60% | 5/5 | 100/100 (100%) |
| `google/gemini-3-flash-preview` | ? | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Actelis Networks, Inc. | False | ? | mistral-large-or, gemma3-1b-qat |
| Castle Biosciences, In | False | ? | gemma3-1b-qat |
| Castle Biosciences, In | True | ? | gemma3-1b-qat |
| HyreCar Inc. | True | ? | gemma3-1b-qat, gemini3-flash-or |
| IGN Entertainment, Inc | True | ? | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.5 — Post-termination option exercise window extraction

**Corpus:** 5 real SEC-filed option grant agreement exhibits, human-validated answers (values range 180 days-90 days). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 88% | 80% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **40%** | 90% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 99/100 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **60%** | 87% | 80% | 5/5 | 100/100 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SIRVA, Inc. | 30 days | ? | 1B, gemma3-1b-qat |
| Covisint Corp. | 85 days | ? | gemma3-1b-qat |
| Annas Linens, Inc. | 90 days | ? | mistral-large-or |
| Williams Scotsman Inte | 90 days | ? | 1B |
| Douglas Dynamics, Inc. | 180 days | ? | 1B, mistral-large-or, gemma3-1b-qat |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 56% | 80% | 5/5 | 96/100 (96%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | Our limited operating history makes it difficult to evaluate our current business and prospects and may increase the risks associated with your investment. | ? | 1B, gemma3-1b-qat |
| HyreCar Inc. | If we do not respond appropriately, the evolution of the automotive industry towards autonomous vehicles and mobility on demand services could adversely affect our business. | ? | 1B, gemma3-1b-qat |
| HyreCar Inc. | Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results. | ? | 1B, gemma3-1b-qat |
| Axcella Health Inc. | If you purchase our common stock in this offering, you will incur immediate and substantial dilution in the net tangible book value of your shares. | ? | 1B, gemma3-1b-qat |
| Axcella Health Inc. | We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively. | ? | 1B, gemma3-1b-qat |

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
| `gemma3:1b` | 1B | **50%** | 92% | 50% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted | **25%** | 96% | 100% | 4/4 | 80/80 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **25%** | 89% | 25% | 4/4 | 80/80 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 75% | 4/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

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
| SOS Hydration Inc. | False | ? | gemma3-1b-qat |

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
| `gemma3:1b` | 1B | **100%** | 68% | 20% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `google/gemma-4-31b-it` | ? | **20%** | 96% | 100% | 5/5 | 100/100 (100%) |
| `mistralai/mistral-large-2512` | ? | **20%** | 97% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **40%** | 88% | 80% | 5/5 | 99/100 (99%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **40%** | 83% | 40% | 5/5 | 80/100 (80%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **20%** | 94% | 80% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **40%** | 94% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | general corporate purposes | ? | 1B |
| Castle Biosciences, In | research and development activities | ? | 1B, gemma4-31b-or, haiku-4.5-direct |
| Axcella Health Inc. | advance our current liver programs | ? | 1B, minimax-m2.5-or, llama3.3-70b-or, gpt5-mini-or |
| Veritone, Inc. | working capital and general corporate purposes | ? | 1B, gemma3-1b-qat |
| Civitas Solutions, Inc | redeem all of the senior notes | ? | 1B, mistral-large-or, minimax-m2.5-or, gemma3-1b-qat, gpt5-mini-or |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax/minimax-m2.5` | ? | **40%** | 97% | 100% | 5/5 | 87/100 (87%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | ? | **60%** | 90% | 40% | 5/5 | 98/100 (98%) |
| `google/gemini-3-flash-preview` | ? | **20%** | 93% | 100% | 5/5 | 100/100 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CAS Medical Systems, I | 9418200 | ? | 1B, minimax-m2.5-or, gemma3-1b-qat, gemini3-flash-or |
| Ocular Therapeutix, In | 1650000 | ? | minimax-m2.5-or, gemma3-1b-qat |
| Navidea Biopharmaceuti | 3000000 | ? | gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–60% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

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
| `mistralai/mistral-large-2512` | ? | **33%** | 98% | 67% | 3/3 | 60/60 (100%) |
| `minimax/minimax-m2.5` | ? | **67%** | 69% | 67% | 3/3 | 56/60 (93%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **67%** | 84% | 67% | 3/3 | 59/60 (98%) |
| `gemma3:1b-it-qat` | ? | **100%** | 61% | 33% | 3/3 | 59/60 (98%) |
| `google/gemini-3-flash-preview` | ? | **67%** | 60% | 33% | 3/3 | 60/60 (100%) |
| `claude-haiku-4-5-20251001` | ? | **33%** | 83% | 33% | 3/3 | 60/60 (100%) |
| `openai/gpt-oss-120b` | ? | **67%** | 77% | 67% | 3/3 | 60/60 (100%) |
| `openai/gpt-5-mini` | ? | **67%** | 95% | 33% | 3/3 | 60/60 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Snapwire Media, Inc. ( | 0.909 | ? | 1B, hosted, gemma4-31b-or, minimax-m2.5-or, llama3.3-70b-or, gemma3-1b-qat, gemini3-flash-or, haiku-4.5-direct, gpt-oss-120b-or, gpt5-mini-or |
| Snapwire Media, Inc. ( | 0.24 | ? | 1B, gemma3-1b-qat |
| Snapwire Media, Inc. ( | 0.6956 | ? | 1B, hosted, gemma4-31b-or, mistral-large-or, minimax-m2.5-or, llama3.3-70b-or, gemma3-1b-qat, gemini3-flash-or, gpt-oss-120b-or, gpt5-mini-or |

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
| `gemma3:1b` | 1B | **0%** | 100% | 50% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `google/gemma-4-31b-it` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax/minimax-m2.5` | ? | **0%** | 100% | 100% | 2/2 | 38/40 (95%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | ? | **0%** | 100% | 50% | 2/2 | 40/40 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

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
| `minimax/minimax-m2.5` | 1/1 | 1/1 |
| `meta-llama/llama-3.3-70b-instruct` | 1/1 | 1/1 |
| `gemma3:1b-it-qat` | 1/1 | 0/1 |
| `google/gemini-3-flash-preview` | 1/1 | 1/1 |
| `claude-haiku-4-5-20251001` | 1/1 | 1/1 |
| `openai/gpt-oss-120b` | 1/1 | 1/1 |
| `openai/gpt-5-mini` | 1/1 | 1/1 |

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
| `mistralai/mistral-large-2512` | ? | **50%** | 90% | 75% | 4/4 | 80/80 (100%) |
| `minimax/minimax-m2.5` | ? | **50%** | 76% | 75% | 4/4 | 64/80 (80%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **75%** | 86% | 25% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 64% | 25% | 4/4 | 80/80 (100%) |
| `google/gemini-3-flash-preview` | ? | **25%** | 98% | 75% | 4/4 | 80/80 (100%) |
| `claude-haiku-4-5-20251001` | ? | **100%** | 31% | 0% | 4/4 | 80/80 (100%) |
| `openai/gpt-oss-120b` | ? | **50%** | 92% | 75% | 4/4 | 80/80 (100%) |
| `openai/gpt-5-mini` | ? | **100%** | 52% | 25% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Connecture, Inc. | 0.51 | ? | 1B, gemma4-31b-or, mistral-large-or, gemma3-1b-qat, haiku-4.5-direct, gpt5-mini-or |
| Connecture, Inc. | 0.42 | ? | 1B, gemma4-31b-or, minimax-m2.5-or, llama3.3-70b-or, gemma3-1b-qat, haiku-4.5-direct, gpt-oss-120b-or, gpt5-mini-or |
| Connecture, Inc. | 0.39 | ? | 1B, hosted, gemma4-31b-or, mistral-large-or, minimax-m2.5-or, llama3.3-70b-or, gemma3-1b-qat, gemini3-flash-or, haiku-4.5-direct, gpt-oss-120b-or, gpt5-mini-or |
| Connecture, Inc. | 0.44 | ? | 1B, gemma4-31b-or, llama3.3-70b-or, gemma3-1b-qat, haiku-4.5-direct, gpt5-mini-or |

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
| `mistralai/mistral-large-2512` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax/minimax-m2.5` | ? | **50%** | 86% | 100% | 2/2 | 38/40 (95%) |
| `meta-llama/llama-3.3-70b-instruct` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | ? | **100%** | 25% | 0% | 2/2 | 40/40 (100%) |
| `google/gemini-3-flash-preview` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `claude-haiku-4-5-20251001` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-oss-120b` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `openai/gpt-5-mini` | ? | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Connecture, Inc. | 58.9 | ? | 1B, minimax-m2.5-or, gemma3-1b-qat |
| Connecture, Inc. | 19.7 | ? | 1B, gemma3-1b-qat |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **hosted** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Reproduce

```bash
cd leaves/<test_name>
python3 source.py                                   # fetch the real SEC documents
python3 ../../engine/run_hosted_sweep.py --label <model> --model <id> --temperature 0.1
python3 ../../results/render.py --temperature 0.1
```

Answers are human-validated from each document's own legal text (`leaves/<test>/oracle.jsonl`, with
the validating quote + difficulty per item). Genuinely ambiguous clauses are excluded, not guessed.

