# Probity — Benchmark Results

**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at temperature 0.1 and count how often the answer changes. **Accuracy** = % correct vs a human-validated answer extracted from the source document. They are reported separately and never averaged — a model can be perfectly consistent and consistently wrong.

12 models span a size ladder (1B local → hosted frontier) to test whether wobble falls as capability rises. Local via Ollama (zero egress); hosted via OpenRouter and direct provider APIs.

---

## Test 1.3.2 — Preferred-stock liquidation participation

**Corpus:** 18 real SEC-filed charter clauses, human-validated answers (6 part / 7 non-part / 5 capped). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **11%** | 98% | 33% | 18/18 | 360/360 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 72% | 18/18 | 359/360 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 78% | 18/18 | 360/360 (100%) |
| `minimax-m2.5` | hosted (OR) | **6%** | 99% | 72% | 18/18 | 351/360 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **11%** | 98% | 72% | 18/18 | 359/360 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **22%** | 95% | 33% | 18/18 | 360/360 (100%) |
| `gemini-3-flash` | hosted (OR) | **6%** | 98% | 67% | 18/18 | 345/360 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **28%** | 96% | 72% | 18/18 | 359/360 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 72% | 18/18 | 360/360 (100%) |

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
| `deepseek-v4-flash` | 2/6 | 6/7 | 5/5 |
| `deepseek-v4-pro` | 2/6 | 6/7 | 5/5 |
| `gemma-4-31b-it` | 2/6 | 6/7 | 5/5 |
| `mistral-large-2512` | 2/6 | 7/7 | 5/5 |
| `minimax-m2.5` | 2/6 | 6/7 | 5/5 |
| `llama-3.3-70b` | 3/6 | 6/7 | 4/5 |
| `gemma3:1b-it-qat` | 1/6 | 4/7 | 1/5 |
| `gemini-3-flash` | 2/6 | 6/7 | 4/5 |
| `claude-haiku-4.5` | 2/6 | 6/7 | 5/5 |
| `gpt-oss-120b` | 2/6 | 6/7 | 5/5 |
| `gpt-5-mini` | 2/6 | 6/7 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Interlink Electronics  | non-participating | easy | gemma3:1b-it-qat, gpt-oss-120b |
| Pfenex Inc. | participating | hard | gemma3:1b-it-qat |
| scPharmaceuticals Inc. | participating | medium | gpt-oss-120b |
| Akouos, Inc. | participating | medium | gemma3:1b, gpt-oss-120b |
| Jazz Semiconductor Inc | capped | medium | minimax-m2.5, gemini-3-flash, gpt-oss-120b |
| The Medicines Co (Remp | capped | medium | gemma3:1b-it-qat |
| Fitbit Inc | capped | hard | gpt-oss-120b |
| Workday, Inc. | capped | medium | gemma3:1b, llama-3.3-70b |
| Internet Security Syst | participating | easy | llama-3.3-70b, gemma3:1b-it-qat |

## What this shows

- **Participating preferred is the universal blind spot.** Even the best models get only 1-2 of 5
  participating clauses right; the small models get 0. The "preference AND THEN also share with the
  common" structure is systematically misread as capped or non-participating.
- **Small models can't classify the hard classes at all** (1B: 0/5 participating, 0/5 capped) -
  they collapse everything to non-participating.

---

## Test 2.1.4 — SAFE valuation cap: pre-money vs post-money

**Corpus:** 16 real SEC-filed YC SAFE provisions, human-validated answers (10 post / 6 pre). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 62% | 16/16 | 320/320 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 62% | 16/16 | 320/320 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 311/320 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |

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
| `deepseek-v4-pro` | 10/10 | 6/6 |
| `gemma-4-31b-it` | 10/10 | 6/6 |
| `mistral-large-2512` | 10/10 | 6/6 |
| `minimax-m2.5` | 10/10 | 6/6 |
| `llama-3.3-70b` | 10/10 | 6/6 |
| `gemma3:1b-it-qat` | 10/10 | 0/6 |
| `gemini-3-flash` | 10/10 | 6/6 |
| `claude-haiku-4.5` | 10/10 | 6/6 |
| `gpt-oss-120b` | 10/10 | 6/6 |
| `gpt-5-mini` | 10/10 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

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

**Corpus:** 16 real SEC-filed preferred-stock charter dividend clauses, human-validated answers (8 cumulative / 8 non-cum). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **12%** | 99% | 88% | 16/16 | 320/320 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 16/16 | 317/320 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 81% | 16/16 | 320/320 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 310/320 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 16/16 | 320/320 (100%) |

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
| `deepseek-v4-pro` | 8/8 | 8/8 |
| `gemma-4-31b-it` | 8/8 | 8/8 |
| `mistral-large-2512` | 8/8 | 8/8 |
| `minimax-m2.5` | 8/8 | 8/8 |
| `llama-3.3-70b` | 8/8 | 8/8 |
| `gemma3:1b-it-qat` | 5/8 | 8/8 |
| `gemini-3-flash` | 8/8 | 8/8 |
| `claude-haiku-4.5` | 8/8 | 8/8 |
| `gpt-oss-120b` | 8/8 | 8/8 |
| `gpt-5-mini` | 8/8 | 8/8 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| BIOACCELERATE HOLDINGS | cumulative | easy | gemma3:1b |
| Eiger BioPharmaceutica | non-cumulative | medium | gemma3:1b |

## What this shows

- **Wobble spread: 0%–12% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger

**Corpus:** 13 real SEC-filed equity-award / employment agreements, human-validated answers (6 single / 7 double). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **15%** | 96% | 85% | 13/13 | 252/260 (97%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 13/13 | 257/260 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 92% | 13/13 | 252/260 (97%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 249/260 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |

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
| `deepseek-v4-pro` | 6/6 | 7/7 |
| `gemma-4-31b-it` | 6/6 | 7/7 |
| `mistral-large-2512` | 6/6 | 7/7 |
| `minimax-m2.5` | 6/6 | 7/7 |
| `llama-3.3-70b` | 6/6 | 7/7 |
| `gemma3:1b-it-qat` | 5/6 | 7/7 |
| `gemini-3-flash` | 6/6 | 7/7 |
| `claude-haiku-4.5` | 6/6 | 7/7 |
| `gpt-oss-120b` | 6/6 | 7/7 |
| `gpt-5-mini` | 6/6 | 7/7 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GIBRALTAR INDUSTRIES,  | double-trigger | hard | gemma3:1b |
| Vulcan Materials CO | double-trigger | hard | gemma3:1b |

## What this shows

- **Wobble spread: 0%–15% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked

**Corpus:** 11 real SEC-filed multi-series preferred charters, human-validated answers (6 pari-passu / 5 stacked). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **18%** | 97% | 45% | 11/11 | 220/220 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 82% | 11/11 | 219/220 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |
| `minimax-m2.5` | hosted (OR) | **9%** | 99% | 82% | 11/11 | 215/220 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 82% | 11/11 | 219/220 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 45% | 11/11 | 220/220 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 82% | 11/11 | 213/220 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 78% | 9/11 | 220/220 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **9%** | 99% | 82% | 11/11 | 220/220 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 82% | 11/11 | 220/220 (100%) |

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
| `deepseek-v4-pro` | 4/6 | 5/5 |
| `gemma-4-31b-it` | 4/6 | 5/5 |
| `mistral-large-2512` | 4/6 | 5/5 |
| `minimax-m2.5` | 4/6 | 5/5 |
| `llama-3.3-70b` | 4/6 | 5/5 |
| `gemma3:1b-it-qat` | 0/6 | 5/5 |
| `gemini-3-flash` | 4/6 | 5/5 |
| `claude-haiku-4.5` | 4/6 | 3/3 |
| `gpt-oss-120b` | 4/6 | 5/5 |
| `gpt-5-mini` | 4/6 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Banks.com, Inc. | stacked | medium | gemma3:1b |
| AMERICAN POWER GROUP C | stacked | easy | claude-haiku-4.5 |
| E CENTIVES INC | stacked | easy | claude-haiku-4.5 |
| Zoom Video Communicati | pari-passu | hard | minimax-m2.5 |
| RIGHT START INC /CA | pari-passu | medium | gemma3:1b |
| PRECOM TECHNOLOGY INC | pari-passu | hard | gpt-oss-120b |

## What this shows

- **Wobble spread: 0%–18% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 82% accuracy).

---

## Test 8.1 — Risk flag: off-market liquidation preference (>1x)

**Corpus:** 10 real SEC-filed preferred-stock liquidation clauses, human-validated answers (5 off-market(>1x) / 5 standard(1x)). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **50%** | 89% | 50% | 10/10 | 200/200 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 90% | 10/10 | 193/200 (96%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `minimax-m2.5` | hosted (OR) | **10%** | 97% | 100% | 10/10 | 196/200 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 90% | 10/10 | 196/200 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **50%** | 89% | 30% | 10/10 | 200/200 (100%) |
| `gemini-3-flash` | hosted (OR) | **10%** | 99% | 90% | 10/10 | 194/200 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **10%** | 99% | 90% | 10/10 | 200/200 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 90% | 10/10 | 199/200 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **off-market(>1x) · standard(1x)** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | off-market(>1x) | standard(1x) |
|---|---|---|
| `gemma3:1b` | 3/5 | 2/5 |
| `deepseek-v4-flash` | 5/5 | 4/5 |
| `deepseek-v4-pro` | 5/5 | 4/5 |
| `gemma-4-31b-it` | 5/5 | 5/5 |
| `mistral-large-2512` | 5/5 | 4/5 |
| `minimax-m2.5` | 5/5 | 5/5 |
| `llama-3.3-70b` | 5/5 | 4/5 |
| `gemma3:1b-it-qat` | 0/5 | 3/5 |
| `gemini-3-flash` | 5/5 | 4/5 |
| `claude-haiku-4.5` | 5/5 | 4/5 |
| `gpt-oss-120b` | 5/5 | 4/5 |
| `gpt-5-mini` | 5/5 | 4/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Lulu's Fashion Lounge  | yes | hard | gemma3:1b |
| ACME PACKET INC | yes | medium | gemma3:1b, gemma3:1b-it-qat |
| FITBIT INC | no | medium | gemma3:1b-it-qat |
| Akouos, Inc. | no | easy | gemma3:1b-it-qat |
| BIOACCELERATE HOLDINGS | no | medium | gemma3:1b |
| Workday, Inc. | no | hard | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat, gemini-3-flash, gpt-oss-120b |
| ENDOSTIM, INC. | no | easy | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **gemma-4-31b-it** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.7 — Redemption rights: redeemable vs non-redeemable

**Corpus:** 10 real SEC-filed preferred-stock charter redemption clauses, human-validated answers (5 redeemable / 5 non-redeem). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **30%** | 96% | 50% | 10/10 | 200/200 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 90% | 10/10 | 200/200 (100%) |
| `deepseek-v4-pro` | hosted, direct | **10%** | 99% | 100% | 10/10 | 200/200 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistral-large-2512` | hosted (OR) | **10%** | 99% | 100% | 10/10 | 200/200 (100%) |
| `minimax-m2.5` | hosted (OR) | **10%** | 98% | 100% | 10/10 | 193/200 (96%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **30%** | 97% | 90% | 10/10 | 200/200 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 190/200 (95%) |
| `claude-haiku-4.5` | hosted, direct API | **10%** | 96% | 100% | 10/10 | 200/200 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **10%** | 99% | 100% | 10/10 | 200/200 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

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
| `deepseek-v4-flash` | 4/5 | 5/5 |
| `deepseek-v4-pro` | 5/5 | 5/5 |
| `gemma-4-31b-it` | 5/5 | 5/5 |
| `mistral-large-2512` | 5/5 | 5/5 |
| `minimax-m2.5` | 5/5 | 5/5 |
| `llama-3.3-70b` | 5/5 | 5/5 |
| `gemma3:1b-it-qat` | 4/5 | 5/5 |
| `gemini-3-flash` | 5/5 | 5/5 |
| `claude-haiku-4.5` | 5/5 | 5/5 |
| `gpt-oss-120b` | 5/5 | 5/5 |
| `gpt-5-mini` | 5/5 | 5/5 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| AdaptHealth Corp. | yes | easy | gemma3:1b-it-qat |
| Lulu's Fashion Lounge  | yes | medium | gemma3:1b, gemma3:1b-it-qat |
| ENDOSTIM, INC. | yes | medium | gemma3:1b, gemma3:1b-it-qat |
| Tenable Holdings, Inc. | yes | medium | gemma3:1b |
| Pfenex Inc. | yes | hard | deepseek-v4-pro, mistral-large-2512, minimax-m2.5, claude-haiku-4.5, gpt-oss-120b |

## What this shows

- **Wobble spread: 0%–30% across the ladder.** Lowest-wobble model: **gemma-4-31b-it** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)

**Corpus:** 12 real SEC-filed stockholder/transfer agreements, human-validated answers (6 drag(obligated) / 6 co-sale(right)). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **8%** | 100% | 42% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted, direct | **8%** | 98% | 100% | 12/12 | 240/240 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `minimax-m2.5` | hosted (OR) | **17%** | 96% | 83% | 12/12 | 238/240 (99%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 75% | 12/12 | 235/240 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **17%** | 96% | 58% | 12/12 | 240/240 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 232/240 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **8%** | 98% | 100% | 12/12 | 240/240 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **17%** | 98% | 92% | 12/12 | 240/240 (100%) |
| `gpt-5-mini` | hosted (OR) | **17%** | 96% | 83% | 12/12 | 240/240 (100%) |

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
| `deepseek-v4-pro` | 5/6 | 6/6 |
| `gemma-4-31b-it` | 6/6 | 6/6 |
| `mistral-large-2512` | 5/6 | 6/6 |
| `minimax-m2.5` | 4/6 | 6/6 |
| `llama-3.3-70b` | 3/6 | 6/6 |
| `gemma3:1b-it-qat` | 3/6 | 4/6 |
| `gemini-3-flash` | 6/6 | 6/6 |
| `claude-haiku-4.5` | 6/6 | 6/6 |
| `gpt-oss-120b` | 5/6 | 6/6 |
| `gpt-5-mini` | 4/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| MCLEODUSA INC | yes | easy | gemma3:1b |
| TRUMP ENTERTAINMENT RE | yes | easy | deepseek-v4-flash, minimax-m2.5, claude-haiku-4.5, gpt-oss-120b, gpt-5-mini |
| LOEWS CINEPLEX ENTERTA | yes | medium | gemma3:1b-it-qat |
| AVENTINE RENEWABLE ENE | yes | hard | minimax-m2.5, gpt-oss-120b, gpt-5-mini |
| ACCELERON PHARMA INC | no | easy | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **gemma-4-31b-it** (0% wobble, 100% accuracy).

---

## Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent

**Corpus:** 12 real SEC-filed stockholder/transfer documents, human-validated answers (6 rofr/cosale / 6 absent/other-right). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 67% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted, direct | **8%** | 97% | 100% | 12/12 | 240/240 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 83% | 12/12 | 238/240 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **25%** | 97% | 92% | 12/12 | 240/240 (100%) |
| `gemini-3-flash` | hosted (OR) | **17%** | 93% | 92% | 12/12 | 233/240 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 83% | 12/12 | 240/240 (100%) |

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
| `deepseek-v4-flash` | 6/6 | 6/6 |
| `deepseek-v4-pro` | 6/6 | 6/6 |
| `gemma-4-31b-it` | 6/6 | 4/6 |
| `mistral-large-2512` | 6/6 | 4/6 |
| `minimax-m2.5` | 6/6 | 6/6 |
| `llama-3.3-70b` | 6/6 | 4/6 |
| `gemma3:1b-it-qat` | 5/6 | 6/6 |
| `gemini-3-flash` | 6/6 | 5/6 |
| `claude-haiku-4.5` | 6/6 | 4/6 |
| `gpt-oss-120b` | 6/6 | 6/6 |
| `gpt-5-mini` | 6/6 | 4/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Symbion (Uniphy Health | yes | easy | gemma3:1b-it-qat |
| Aclarion | yes | easy | gemma3:1b-it-qat |
| Taylor Morrison (TMM H | no | easy | gemma3:1b-it-qat |
| MotivNation | no | hard | deepseek-v4-flash, gemini-3-flash |
| EntreMetrix | no | hard | gemini-3-flash |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **deepseek-v4-pro** (0% wobble, 100% accuracy).

---

## Test 5.4 — Pro-rata right on future financings: granted vs not

**Corpus:** 12 real SEC-filed SAFEs, side letters and investors' rights agreements, human-validated answers (6 pro-rata / 6 absent/waived). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **33%** | 94% | 83% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `minimax-m2.5` | hosted (OR) | **25%** | 98% | 100% | 12/12 | 236/240 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 12/12 | 239/240 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **17%** | 96% | 83% | 12/12 | 240/240 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 232/240 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **17%** | 99% | 100% | 12/12 | 240/240 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pro-rata · absent/waived** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pro-rata | absent/waived |
|---|---|---|
| `gemma3:1b` | 6/6 | 4/6 |
| `deepseek-v4-flash` | 6/6 | 6/6 |
| `deepseek-v4-pro` | 6/6 | 6/6 |
| `gemma-4-31b-it` | 6/6 | 6/6 |
| `mistral-large-2512` | 6/6 | 6/6 |
| `minimax-m2.5` | 6/6 | 6/6 |
| `llama-3.3-70b` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 4/6 | 6/6 |
| `gemini-3-flash` | 6/6 | 6/6 |
| `claude-haiku-4.5` | 6/6 | 6/6 |
| `gpt-oss-120b` | 6/6 | 6/6 |
| `gpt-5-mini` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SOS Hydration Inc. | yes | medium | gemma3:1b, minimax-m2.5, gpt-oss-120b |
| Millennium Blockchain, | yes | medium | minimax-m2.5, gemma3:1b-it-qat, gpt-oss-120b |
| Cantabio Pharmaceutica | yes | medium | minimax-m2.5, gemma3:1b-it-qat |
| Supernus Pharmaceutica | no | easy | gemma3:1b |
| Infinity Pharmaceutica | no | easy | gemma3:1b |
| Xcyte Therapies, Inc. | no | hard | gemma3:1b |

## What this shows

- **Wobble spread: 0%–33% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.2 — Vesting schedule: cliff present vs absent

**Corpus:** 12 real SEC-filed equity-award agreements and disclosures, human-validated answers (6 cliff / 6 no-cliff). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **8%** | 98% | 67% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `minimax-m2.5` | hosted (OR) | **25%** | 97% | 100% | 12/12 | 239/240 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **17%** | 96% | 100% | 12/12 | 233/240 (97%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **8%** | 99% | 92% | 12/12 | 240/240 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 229/240 (95%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **8%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gpt-5-mini` | hosted (OR) | **17%** | 98% | 92% | 12/12 | 240/240 (100%) |

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
| `deepseek-v4-pro` | 6/6 | 6/6 |
| `gemma-4-31b-it` | 6/6 | 6/6 |
| `mistral-large-2512` | 6/6 | 6/6 |
| `minimax-m2.5` | 6/6 | 6/6 |
| `llama-3.3-70b` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 6/6 | 5/6 |
| `gemini-3-flash` | 6/6 | 6/6 |
| `claude-haiku-4.5` | 6/6 | 6/6 |
| `gpt-oss-120b` | 6/6 | 5/6 |
| `gpt-5-mini` | 6/6 | 5/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| NorthStar Healthcare I | yes | easy | llama-3.3-70b |
| Interval Leisure Group | yes | medium | gemma3:1b, minimax-m2.5, llama-3.3-70b, gpt-5-mini |
| Atossa Genetics Inc. | no | easy | gemma3:1b-it-qat |
| Clarcor Inc. | no | hard | minimax-m2.5, gpt-5-mini |
| World Heart Corp | no | hard | minimax-m2.5, gpt-oss-120b |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **deepseek-v4-pro** (0% wobble, 100% accuracy).

---

## Test 5.2 — Protective provisions: investor class-veto right present vs absent

**Corpus:** 12 real SEC-filed charters and governance documents, human-validated answers (6 veto-right / 6 absent). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **8%** | 100% | 58% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `deepseek-v4-pro` | hosted, direct | **8%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `minimax-m2.5` | hosted (OR) | **17%** | 98% | 92% | 12/12 | 237/240 (99%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **8%** | 100% | 75% | 12/12 | 240/240 (100%) |
| `gemini-3-flash` | hosted (OR) | **8%** | 99% | 100% | 12/12 | 231/240 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **8%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gpt-5-mini` | hosted (OR) | **8%** | 99% | 100% | 12/12 | 240/240 (100%) |

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
| `deepseek-v4-pro` | 5/6 | 6/6 |
| `gemma-4-31b-it` | 5/6 | 6/6 |
| `mistral-large-2512` | 6/6 | 6/6 |
| `minimax-m2.5` | 5/6 | 6/6 |
| `llama-3.3-70b` | 6/6 | 6/6 |
| `gemma3:1b-it-qat` | 3/6 | 6/6 |
| `gemini-3-flash` | 6/6 | 6/6 |
| `claude-haiku-4.5` | 6/6 | 6/6 |
| `gpt-oss-120b` | 5/6 | 6/6 |
| `gpt-5-mini` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| BroadSoft, Inc. | yes | medium | deepseek-v4-pro, minimax-m2.5, gemini-3-flash, gpt-oss-120b, gpt-5-mini |
| SCYNEXIS, Inc. | yes | medium | gemma3:1b |
| JCM Partners, LLC | yes | medium | minimax-m2.5, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 5.3 — Information rights: live financial-reporting obligation vs absent

**Corpus:** 12 real SEC-filed investors' rights agreements and equity-award docs, human-validated answers (6 info-rights / 6 absent/waived). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **17%** | 95% | 50% | 12/12 | 240/240 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 92% | 12/12 | 167/240 (70%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 92% | 12/12 | 235/240 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **8%** | 100% | 50% | 12/12 | 240/240 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 92% | 12/12 | 228/240 (95%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 12/12 | 240/240 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **8%** | 100% | 92% | 12/12 | 240/240 (100%) |
| `gpt-5-mini` | hosted (OR) | **8%** | 99% | 100% | 12/12 | 240/240 (100%) |

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
| `deepseek-v4-pro` | 5/6 | 6/6 |
| `gemma-4-31b-it` | 5/6 | 6/6 |
| `mistral-large-2512` | 5/6 | 6/6 |
| `minimax-m2.5` | 5/6 | 6/6 |
| `llama-3.3-70b` | 5/6 | 6/6 |
| `gemma3:1b-it-qat` | 6/6 | 0/6 |
| `gemini-3-flash` | 5/6 | 6/6 |
| `claude-haiku-4.5` | 6/6 | 6/6 |
| `gpt-oss-120b` | 5/6 | 6/6 |
| `gpt-5-mini` | 6/6 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Bell Microproducts Inc | yes | hard | gpt-oss-120b, gpt-5-mini |
| Speedway Motorsports,  | no | easy | gemma3:1b |
| Pool Corp | no | easy | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–17% across the ladder.** Lowest-wobble model: **claude-haiku-4.5** (0% wobble, 100% accuracy).

---

## Test 5.7 — Vesting acceleration: granted on trigger vs absent

**Corpus:** 9 real SEC-filed equity-award agreements and proxy disclosures, human-validated answers (6 accelerates / 3 no-acceleration). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **33%** | 96% | 78% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 177/180 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 179/180 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 44% | 9/9 | 180/180 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 177/180 (98%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **accelerates · no-acceleration** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | accelerates | no-acceleration |
|---|---|---|
| `gemma3:1b` | 5/6 | 2/3 |
| `deepseek-v4-flash` | 6/6 | 3/3 |
| `deepseek-v4-pro` | 6/6 | 3/3 |
| `gemma-4-31b-it` | 6/6 | 3/3 |
| `mistral-large-2512` | 6/6 | 3/3 |
| `minimax-m2.5` | 6/6 | 3/3 |
| `llama-3.3-70b` | 6/6 | 3/3 |
| `gemma3:1b-it-qat` | 2/6 | 2/3 |
| `gemini-3-flash` | 6/6 | 3/3 |
| `claude-haiku-4.5` | 6/6 | 3/3 |
| `gpt-oss-120b` | 6/6 | 3/3 |
| `gpt-5-mini` | 6/6 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| GIBRALTAR INDUSTRIES,  | yes | easy | gemma3:1b |
| CASTLIGHT HEALTH, INC. | yes | medium | gemma3:1b |
| YELP INC | no | easy | gemma3:1b |

## What this shows

- **Wobble spread: 0%–33% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.3.1 — Liquidation preference multiple: 1x vs 2x vs 3x vs other

**Corpus:** 9 real SEC-filed preferred-stock liquidation preference clauses, human-validated answers (0 non-part / 3 1x / 3 2x / 3 3x / 0 other). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **11%** | 99% | 0% | 7/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted, direct | **11%** | 96% | 67% | 9/9 | 112/180 (62%) |
| `deepseek-v4-pro` | hosted, direct | **11%** | 98% | 67% | 9/9 | 180/180 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |
| `mistral-large-2512` | hosted (OR) | **11%** | 99% | 67% | 9/9 | 180/180 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 67% | 9/9 | 171/180 (95%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **11%** | 97% | 67% | 9/9 | 179/180 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **67%** | 73% | 56% | 9/9 | 180/180 (100%) |
| `gemini-3-flash` | hosted (OR) | **11%** | 98% | 67% | 9/9 | 172/180 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 78% | 9/9 | 180/180 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |
| `gpt-5-mini` | hosted (OR) | **22%** | 99% | 67% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **non-part · 1x · 2x · 3x · other** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | non-part | 1x | 2x | 3x | other |
|---|---|---|---|---|---|
| `gemma3:1b` | — | 0/2 | 0/3 | 0/2 | — |
| `deepseek-v4-flash` | — | 2/3 | 1/3 | 3/3 | — |
| `deepseek-v4-pro` | — | 2/3 | 1/3 | 3/3 | — |
| `gemma-4-31b-it` | — | 2/3 | 1/3 | 3/3 | — |
| `mistral-large-2512` | — | 2/3 | 1/3 | 3/3 | — |
| `minimax-m2.5` | — | 2/3 | 1/3 | 3/3 | — |
| `llama-3.3-70b` | — | 2/3 | 1/3 | 3/3 | — |
| `gemma3:1b-it-qat` | — | 1/3 | 2/3 | 2/3 | — |
| `gemini-3-flash` | — | 2/3 | 1/3 | 3/3 | — |
| `claude-haiku-4.5` | — | 2/3 | 2/3 | 3/3 | — |
| `gpt-oss-120b` | — | 2/3 | 1/3 | 3/3 | — |
| `gpt-5-mini` | — | 2/3 | 1/3 | 3/3 | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| COUNTERPATH CORP  (CIK | 1x | easy | gemma3:1b-it-qat |
| BIOVENTRIX, INC.  (CIK | 1x | easy | gemma3:1b, gemma3:1b-it-qat |
| Revance Therapeutics,  | 1x | easy | gemma3:1b-it-qat |
| Oportun Financial Corp | 2x | easy | gemma3:1b, deepseek-v4-flash, deepseek-v4-pro, mistral-large-2512, llama-3.3-70b, gemma3:1b-it-qat, gpt-5-mini |
| Pagaya Technologies Lt | 2x | easy | gemma3:1b-it-qat, gpt-5-mini |
| BECEEM COMMUNICATIONS  | 3x | easy | gemma3:1b-it-qat |
| CASTLE BIOSCIENCES INC | 3x | easy | gemma3:1b, gemini-3-flash |

## What this shows

- **Wobble spread: 0%–67% across the ladder.** Lowest-wobble model: **claude-haiku-4.5** (0% wobble, 78% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 5.1 — Board seats: number an investor has the right to designate

**Corpus:** 9 real SEC-filed voting/shareholders'/designation agreements, human-validated answers (values range 1-9). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **11%** | 96% | 78% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 67% | 9/9 | 180/180 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **33%** | 93% | 67% | 9/9 | 175/180 (97%) |
| `mistral-large-2512` | hosted (OR) | **11%** | 98% | 44% | 9/9 | 180/180 (100%) |
| `minimax-m2.5` | hosted (OR) | **33%** | 92% | 67% | 9/9 | 146/180 (81%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **22%** | 96% | 44% | 9/9 | 179/180 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **11%** | 99% | 100% | 9/9 | 180/180 (100%) |
| `gemini-3-flash` | hosted (OR) | **11%** | 94% | 78% | 9/9 | 175/180 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 78% | 9/9 | 180/180 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **22%** | 94% | 78% | 9/9 | 180/180 (100%) |
| `gpt-5-mini` | hosted (OR) | **44%** | 94% | 78% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Dollar General Corpora | 1 | medium | llama-3.3-70b |
| Emergent Capital, Inc. | 3 | medium | minimax-m2.5, gpt-oss-120b, gpt-5-mini |
| Ute Energy Corporation | 1 | medium | gemma3:1b, gemma-4-31b-it, minimax-m2.5, llama-3.3-70b |
| Ute Energy Corporation | 2 | medium | gemma-4-31b-it, gemma3:1b-it-qat, gemini-3-flash, gpt-5-mini |
| Cinemark Holdings, Inc | 5 | easy | gemma-4-31b-it, mistral-large-2512, minimax-m2.5, gpt-oss-120b, gpt-5-mini |
| Cinemark Holdings, Inc | 9 | hard | gpt-5-mini |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **deepseek-v4-pro** (0% wobble, 89% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.6 — SAFE pro-rata side letter: granted vs absent

**Corpus:** 15 real SEC-filed SAFEs and pro-rata side letters, human-validated answers (9 pro-rata / 6 absent). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **13%** | 97% | 87% | 15/15 | 300/300 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 15/15 | 299/300 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **7%** | 98% | 100% | 15/15 | 300/300 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 15/15 | 289/300 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 15/15 | 300/300 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pro-rata · absent** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pro-rata | absent |
|---|---|---|
| `gemma3:1b` | 9/9 | 4/6 |
| `deepseek-v4-flash` | 9/9 | 6/6 |
| `deepseek-v4-pro` | 9/9 | 6/6 |
| `gemma-4-31b-it` | 9/9 | 6/6 |
| `mistral-large-2512` | 9/9 | 6/6 |
| `minimax-m2.5` | 9/9 | 6/6 |
| `llama-3.3-70b` | 9/9 | 6/6 |
| `gemma3:1b-it-qat` | 9/9 | 6/6 |
| `gemini-3-flash` | 9/9 | 6/6 |
| `claude-haiku-4.5` | 9/9 | 6/6 |
| `gpt-oss-120b` | 9/9 | 6/6 |
| `gpt-5-mini` | 9/9 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Rare Earths Americas,  | no | easy | gemma3:1b |
| TaoWeave, Inc. | no | hard | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–13% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 1.1.2 — Priced round basis: pre-money vs post-money

**Corpus:** 19 real SEC-filed priced-round financing documents, human-validated answers (13 pre / 6 post). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **16%** | 96% | 63% | 19/19 | 380/380 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 95% | 19/19 | 375/380 (99%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **21%** | 96% | 68% | 19/19 | 380/380 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 19/19 | 359/380 (94%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 95% | 19/19 | 380/380 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **11%** | 97% | 100% | 19/19 | 379/380 (100%) |
| `gpt-5-mini` | hosted (OR) | **11%** | 98% | 100% | 19/19 | 380/380 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **pre · post** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | pre | post |
|---|---|---|
| `gemma3:1b` | 6/13 | 6/6 |
| `deepseek-v4-flash` | 13/13 | 5/6 |
| `deepseek-v4-pro` | 13/13 | 5/6 |
| `gemma-4-31b-it` | 13/13 | 5/6 |
| `mistral-large-2512` | 13/13 | 5/6 |
| `minimax-m2.5` | 13/13 | 5/6 |
| `llama-3.3-70b` | 13/13 | 5/6 |
| `gemma3:1b-it-qat` | 7/13 | 6/6 |
| `gemini-3-flash` | 13/13 | 6/6 |
| `claude-haiku-4.5` | 13/13 | 5/6 |
| `gpt-oss-120b` | 13/13 | 6/6 |
| `gpt-5-mini` | 13/13 | 6/6 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Viking Therapeutics, I | pre-money | easy | gemma3:1b-it-qat |
| Rules-Based Medicine I | pre-money | easy | gemma3:1b-it-qat |
| RMG Acquisition Corp.  | pre-money | easy | gpt-oss-120b, gpt-5-mini |
| Ucommune Group Holding | pre-money | easy | gemma3:1b |
| VIEWRAY INC | pre-money | easy | gemma3:1b, gemma3:1b-it-qat |
| SOCIETY PASS INCORPORA | pre-money | easy | gemma3:1b, gemma3:1b-it-qat |
| New Global Energy, Inc | post-money | easy | gpt-oss-120b, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–21% across the ladder.** Lowest-wobble model: **gemini-3-flash** (0% wobble, 100% accuracy).

---

## Test 8.2 — Risk flag: full-ratchet anti-dilution present vs absent

**Corpus:** 7 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (4 full-ratchet / 3 absent). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **29%** | 91% | 57% | 7/7 | 140/140 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 139/140 (99%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 139/140 (99%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **14%** | 98% | 86% | 7/7 | 138/140 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **14%** | 99% | 57% | 7/7 | 140/140 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 134/140 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

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
| `deepseek-v4-pro` | 4/4 | 3/3 |
| `gemma-4-31b-it` | 4/4 | 3/3 |
| `mistral-large-2512` | 4/4 | 3/3 |
| `minimax-m2.5` | 4/4 | 3/3 |
| `llama-3.3-70b` | 3/4 | 3/3 |
| `gemma3:1b-it-qat` | 4/4 | 0/3 |
| `gemini-3-flash` | 4/4 | 3/3 |
| `claude-haiku-4.5` | 4/4 | 3/3 |
| `gpt-oss-120b` | 4/4 | 3/3 |
| `gpt-5-mini` | 4/4 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| NYTEX Energy Holdings, | yes | hard | llama-3.3-70b |
| ZIX CORP | no | easy | gemma3:1b |
| VISIUM TECHNOLOGIES, I | no | medium | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–29% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 1.1.1 — Post-money valuation extraction

**Corpus:** 4 real SEC-filed priced-round financing documents, human-validated answers (values range 5000000-275000000). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **25%** | 97% | 25% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **25%** | 95% | 75% | 4/4 | 80/80 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 75/80 (94%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| XTI Aerospace, Inc. | 275000000 | medium | gemma3:1b |
| Remark Holdings, Inc.  | 5000000 | easy | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none

**Corpus:** 5 real SEC-filed preferred-stock anti-dilution clauses, human-validated answers (2 full-ratchet / 2 weighted-avg / 0 broad-based / 0 narrow-based / 1 none). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 40% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 98/100 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **20%** | 91% | 40% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 97/100 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

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
| `deepseek-v4-pro` | 2/2 | 2/2 | — | — | 1/1 |
| `gemma-4-31b-it` | 2/2 | 2/2 | — | — | 1/1 |
| `mistral-large-2512` | 2/2 | 2/2 | — | — | 1/1 |
| `minimax-m2.5` | 2/2 | 2/2 | — | — | 1/1 |
| `llama-3.3-70b` | 2/2 | 2/2 | — | — | 1/1 |
| `gemma3:1b-it-qat` | 2/2 | 0/2 | — | — | 0/1 |
| `gemini-3-flash` | 2/2 | 2/2 | — | — | 1/1 |
| `claude-haiku-4.5` | 2/2 | 2/2 | — | — | 1/1 |
| `gpt-oss-120b` | 2/2 | 2/2 | — | — | 1/1 |
| `gpt-5-mini` | 2/2 | 2/2 | — | — | 1/1 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VISIUM TECHNOLOGIES, I | weighted-average | medium | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 8.3 — Risk flag: uncapped participating-preferred present vs absent

**Corpus:** 13 real SEC-filed preferred-stock liquidation/participation clauses, human-validated answers (4 uncapped / 9 capped/none). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **8%** | 100% | 31% | 13/13 | 260/260 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 85% | 13/13 | 191/260 (73%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 77% | 13/13 | 260/260 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 77% | 13/13 | 259/260 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **8%** | 99% | 62% | 13/13 | 260/260 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 77% | 13/13 | 250/260 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 69% | 13/13 | 260/260 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **8%** | 100% | 85% | 13/13 | 260/260 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 85% | 13/13 | 260/260 (100%) |

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
| `deepseek-v4-pro` | 2/4 | 9/9 |
| `gemma-4-31b-it` | 2/4 | 8/9 |
| `mistral-large-2512` | 2/4 | 9/9 |
| `minimax-m2.5` | 2/4 | 9/9 |
| `llama-3.3-70b` | 2/4 | 8/9 |
| `gemma3:1b-it-qat` | 0/4 | 8/9 |
| `gemini-3-flash` | 2/4 | 8/9 |
| `claude-haiku-4.5` | 2/4 | 7/9 |
| `gpt-oss-120b` | 2/4 | 9/9 |
| `gpt-5-mini` | 2/4 | 9/9 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Fitbit Inc | no | hard | gemma3:1b |
| Internet Security Syst | no | medium | gemma3:1b-it-qat |
| BioAccelerate Holdings | no | hard | gpt-oss-120b |

## What this shows

- **Wobble spread: 0%–8% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 85% accuracy).

---

## Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent

**Corpus:** 7 real SEC-filed SAFE agreements, human-validated answers (4 MFN / 3 absent). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 57% | 7/7 | 140/140 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 136/140 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

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
| `deepseek-v4-pro` | 4/4 | 3/3 |
| `gemma-4-31b-it` | 4/4 | 3/3 |
| `mistral-large-2512` | 4/4 | 3/3 |
| `minimax-m2.5` | 4/4 | 3/3 |
| `llama-3.3-70b` | 4/4 | 3/3 |
| `gemma3:1b-it-qat` | 1/4 | 3/3 |
| `gemini-3-flash` | 4/4 | 3/3 |
| `claude-haiku-4.5` | 4/4 | 3/3 |
| `gpt-oss-120b` | 4/4 | 3/3 |
| `gpt-5-mini` | 4/4 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **gemma3:1b** (0% wobble, 100% accuracy).

---

## Test 1.3.3 — Participation cap multiple extraction

**Corpus:** 3 real SEC-filed capped-participating-preferred liquidation clauses, human-validated answers (values range 3-3.5). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 100% | 3/3 | 59/60 (98%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 56/60 (93%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **gemma3:1b** (0% wobble, 100% accuracy).

---

## Test 6.4 — Stock option exercise (strike) price extraction

**Corpus:** 7 real SEC-filed stock option grant agreements, human-validated answers (values range 0.03-11.0). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **43%** | 90% | 71% | 7/7 | 134/140 (96%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 139/140 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **14%** | 95% | 43% | 7/7 | 140/140 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 136/140 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Medecision, Inc. | 0.03 | easy | gemma3:1b |
| Medecision, Inc. | 0.25 | easy | gemma3:1b-it-qat |
| Medecision, Inc. | 1.25 | medium | gemma3:1b |
| Medecision, Inc. | 2.0 | medium | gemma3:1b |

## What this shows

- **Wobble spread: 0%–43% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.1 — SAFE valuation cap extraction

**Corpus:** 8 real SEC-filed SAFE agreements, human-validated answers (values range 15000000-150000000). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **25%** | 95% | 75% | 8/8 | 160/160 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **25%** | 93% | 75% | 8/8 | 160/160 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 155/160 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Complete Solaria, Inc. | 53540000 | medium | gemma3:1b-it-qat |
| Invizyne Technologies  | 100000000 | hard | gemma3:1b, gemma3:1b-it-qat |
| PaxMedica, Inc. | 150000000 | hard | gemma3:1b |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 2.2.1 — Convertible note principal amount extraction

**Corpus:** 7 real SEC-filed convertible promissory notes, human-validated answers (values range 12500-17364375). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 100% | 7/7 | 139/140 (99%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/7 | 100/140 (71%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 139/140 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 135/140 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 7/7 | 140/140 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ACOLOGY, INC. | 400000 | easy | deepseek-v4-flash |
| GARDENBURGER, INC. | 17364375 | easy | deepseek-v4-flash |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **gemma3:1b** (0% wobble, 100% accuracy).

---

## Test 2.1.2 — SAFE discount rate extraction

**Corpus:** 9 real SEC-filed SAFE agreements, human-validated answers (values range 10-50). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **22%** | 92% | 56% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax-m2.5` | hosted (OR) | **44%** | 91% | 100% | 9/9 | 180/180 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **11%** | 98% | 33% | 9/9 | 180/180 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 175/180 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **11%** | 99% | 100% | 9/9 | 180/180 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Creci Inc. | 20 | medium | gpt-oss-120b |
| Complete Solaria, Inc. | 20 | easy | gemma3:1b, minimax-m2.5 |
| Lomond Therapeutics Ho | 10 | hard | minimax-m2.5 |
| Maison Luxe, Inc. | 20 | easy | minimax-m2.5 |
| Parker Clay Global, PB | 15 | medium | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–44% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.4 — Convertible note valuation cap extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 25000000-125000000). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **50%** | 90% | 75% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 68/80 (85%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 79/80 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **25%** | 89% | 100% | 4/4 | 80/80 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 77/80 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Damon Motors Inc. | 125000000 | easy | gemma3:1b, gemma3:1b-it-qat |
| Greenfield Robotics Co | 30000000 | easy | gemma3:1b |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.6.1 — Preferred-stock conversion ratio extraction

**Corpus:** 5 real SEC-filed preferred-stock charters, human-validated answers (values range 1-8000). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **20%** | 90% | 80% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **20%** | 97% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 82/100 (82%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 97/100 (97%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **40%** | 92% | 80% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 97/100 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Loop Industries, Inc. | 1 | easy | gemma3:1b-it-qat |
| Air Defense Services,  | 100 | medium | gemma-4-31b-it |
| Boston Life Sciences,  | 8000 | hard | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.5.2 — Anti-dilution weighted-average base: broad-based vs narrow-based vs n/a

**Corpus:** 10 real SEC-filed preferred-stock charter anti-dilution clauses, human-validated answers (3 broad / 4 narrow / 3 n/a). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 70% | 10/10 | 200/200 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 198/200 (99%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 194/200 (97%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 70% | 10/10 | 200/200 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 192/200 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

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
| `deepseek-v4-pro` | 3/3 | 4/4 | 3/3 |
| `gemma-4-31b-it` | 3/3 | 4/4 | 3/3 |
| `mistral-large-2512` | 3/3 | 4/4 | 3/3 |
| `minimax-m2.5` | 3/3 | 4/4 | 3/3 |
| `llama-3.3-70b` | 3/3 | 4/4 | 3/3 |
| `gemma3:1b-it-qat` | 3/3 | 4/4 | 0/3 |
| `gemini-3-flash` | 3/3 | 4/4 | 3/3 |
| `claude-haiku-4.5` | 3/3 | 4/4 | 3/3 |
| `gpt-oss-120b` | 3/3 | 4/4 | 3/3 |
| `gpt-5-mini` | 3/3 | 4/4 | 3/3 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 1.6.2 — Automatic conversion (QPO) proceeds threshold extraction

**Corpus:** 5 real SEC-filed preferred-stock charter automatic-conversion clauses, human-validated answers (values range 30000000-100000000). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 98/100 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **20%** | 93% | 80% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 96/100 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Asana, Inc. | 100000000 | easy | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–20% across the ladder.** Lowest-wobble model: **gemma3:1b** (0% wobble, 100% accuracy).

---

## Test 2.2.2 — Convertible note interest rate extraction

**Corpus:** 6 real SEC-filed convertible promissory notes, human-validated answers (values range 0.28-10.0). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 83% | 6/6 | 120/120 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/6 | 50/120 (42%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **67%** | 83% | 67% | 6/6 | 113/120 (94%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 116/120 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VERITAS Farms Inc. | 10.0 | easy | deepseek-v4-flash, gemma3:1b-it-qat |
| Golden Matrix Group, I | 8.0 | easy | gemma3:1b-it-qat |
| LanzaTech Global, Inc. | 8.0 | easy | gemma3:1b-it-qat |
| XTI Aerospace Inc. | 10.0 | medium | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–67% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)

**Corpus:** 13 real SEC-filed SAFE (Simple Agreement for Future Equity) instruments, human-validated answers (2 cap / 1 discount / 10 both-mfn). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **54%** | 90% | 77% | 13/13 | 245/260 (94%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `minimax-m2.5` | hosted (OR) | **38%** | 96% | 100% | 13/13 | 255/260 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **46%** | 92% | 54% | 13/13 | 260/260 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 251/260 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 13/13 | 260/260 (100%) |

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
| `deepseek-v4-pro` | 2/2 | 1/1 | 10/10 |
| `gemma-4-31b-it` | 2/2 | 1/1 | 10/10 |
| `mistral-large-2512` | 2/2 | 1/1 | 10/10 |
| `minimax-m2.5` | 2/2 | 1/1 | 10/10 |
| `llama-3.3-70b` | 2/2 | 1/1 | 10/10 |
| `gemma3:1b-it-qat` | 1/2 | 0/1 | 6/10 |
| `gemini-3-flash` | 2/2 | 1/1 | 10/10 |
| `claude-haiku-4.5` | 2/2 | 1/1 | 10/10 |
| `gpt-oss-120b` | 2/2 | 1/1 | 10/10 |
| `gpt-5-mini` | 2/2 | 1/1 | 10/10 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Parker Clay Global, PB | both-mfn | medium | minimax-m2.5, gemma3:1b-it-qat |
| Maison Luxe, Inc. | both-mfn | medium | gemma3:1b, gemma3:1b-it-qat |
| Rentberry Inc. | both-mfn | medium | gemma3:1b, gemma3:1b-it-qat |
| Creci Inc. | both-mfn | medium | gemma3:1b |
| Complete Solaria, Inc. | both-mfn | easy | minimax-m2.5 |
| Lomond Therapeutics Ho | both-mfn | medium | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |
| Neo Aeronautics, Inc. | both-mfn | medium | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |
| Manako Labs Ltd | both-mfn | medium | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |
| Gardedam Therapeutics  | cap | medium | gemma3:1b |

## What this shows

- **Wobble spread: 0%–54% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.1.3 — Priced-round price-per-share extraction

**Corpus:** 8 real SEC-filed stock purchase agreements / charters / offerings, human-validated answers (values range 0.2-1000.0). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **25%** | 95% | 62% | 8/8 | 160/160 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 62% | 8/8 | 160/160 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 62% | 8/8 | 160/160 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 75% | 8/8 | 160/160 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 62% | 8/8 | 160/160 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 75% | 8/8 | 155/160 (97%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 75% | 8/8 | 157/160 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **50%** | 92% | 62% | 8/8 | 160/160 (100%) |
| `gemini-3-flash` | hosted (OR) | **12%** | 95% | 75% | 8/8 | 154/160 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 62% | 8/8 | 160/160 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **12%** | 96% | 75% | 8/8 | 160/160 (100%) |
| `gpt-5-mini` | hosted (OR) | **25%** | 98% | 75% | 8/8 | 160/160 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Astea International In | 3.63 | easy | gemma3:1b-it-qat |
| Kiwa Bio-Tech Products | 1.3 | medium | gemma3:1b, gemma3:1b-it-qat |
| Gelesis, Inc. | 1.26 | medium | gemini-3-flash, gpt-oss-120b, gpt-5-mini |
| Elicio Therapeutics, I | 1.0 | easy | gemma3:1b-it-qat |
| WhiteGlove Health, Inc | 0.2 | easy | gemma3:1b |
| Geos Communications, I | 0.625 | medium | gemma3:1b-it-qat, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **gemma-4-31b-it** (0% wobble, 75% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 2.2.3 — Convertible note maturity date extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 2005-03-31-2026-12-31). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 50% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 20/80 (25%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 3/4 | 79/80 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 75% | 4/4 | 80/80 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 3/4 | 77/80 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ACOLOGY, INC. | 2015-03-04 | medium | deepseek-v4-pro, gemma-4-31b-it, llama-3.3-70b, gemini-3-flash, claude-haiku-4.5, gpt-oss-120b |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 2.2.5 — Convertible note conversion-discount rate extraction

**Corpus:** 4 real SEC-filed convertible promissory notes, human-validated answers (values range 5.0-50.0). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 0% | 2/4 | 36/80 (45%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 36/80 (45%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 2/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 79/80 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 0% | 4/4 | 61/80 (76%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 76/80 (95%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 3/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ACOLOGY, INC. | 50.0 | easy | gemma3:1b, deepseek-v4-pro |
| HepaLife Technologies, | 5.0 | medium | gemma3:1b, deepseek-v4-pro, minimax-m2.5, claude-haiku-4.5 |

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction

**Corpus:** 2 real SEC-filed convertible promissory notes, human-validated answers (values range 10000000-40000000). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **50%** | 92% | 100% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 2/2 | 15/40 (38%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 100% | 2/2 | 29/40 (72%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 37/40 (92%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Valkyrie Sciences Hold | 10000000 | medium | gemma3:1b |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.1 — Equity vesting schedule extraction + normalization

**Corpus:** 9 real SEC-filed equity-award / employment agreements, human-validated answers (values range 1.5yr/no-cliff-4yr/no-cliff). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **22%** | 91% | 33% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |
| `mistral-large-2512` | hosted (OR) | **11%** | 99% | 78% | 9/9 | 180/180 (100%) |
| `minimax-m2.5` | hosted (OR) | **22%** | 93% | 100% | 9/9 | 166/180 (92%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **22%** | 95% | 33% | 9/9 | 180/180 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 172/180 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **11%** | 99% | 89% | 9/9 | 180/180 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CONOR MEDSYSTEMS, INC. | 1.5yr/no-cliff | medium | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |
| CLARCOR INC. | 4yr/no-cliff | hard | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |
| WORLD HEART CORP | 4yr/1yr-cliff | hard | mistral-large-2512, gpt-oss-120b |

## What this shows

- **Wobble spread: 0%–22% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 3.1 — Cap-table current ownership percentage (compute)

**Corpus:** 9 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-33.9). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **100%** | 64% | 0% | 9/9 | 180/180 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **22%** | 94% | 100% | 9/9 | 180/180 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |
| `minimax-m2.5` | hosted (OR) | **11%** | 99% | 100% | 9/9 | 172/180 (96%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 9/9 | 176/180 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **33%** | 93% | 0% | 9/9 | 180/180 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 173/180 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 89% | 9/9 | 180/180 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **22%** | 99% | 100% | 9/9 | 180/180 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 9/9 | 180/180 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | gemma3:1b, gpt-oss-120b |
| Uber Technologies, Inc | 11.0 | easy | gemma3:1b, gemma3:1b-it-qat |
| Uber Technologies, Inc | 2.4 | medium | gemma3:1b, gemma3:1b-it-qat |
| Uber Technologies, Inc | 8.6 | easy | gemma3:1b, gpt-oss-120b |
| Uber Technologies, Inc | 5.4 | medium | gemma3:1b, gemma-4-31b-it |
| Uber Technologies, Inc | 16.3 | medium | gemma3:1b |
| Uber Technologies, Inc | 5.2 | medium | gemma3:1b |
| Uber Technologies, Inc | 5.3 | medium | gemma3:1b |
| Uber Technologies, Inc | 33.9 | hard | gemma3:1b, gemma-4-31b-it, minimax-m2.5, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.1 — Named founder's ownership percentage (compute)

**Corpus:** 3 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 2.4-8.6). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **100%** | 58% | 0% | 3/3 | 60/60 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 58/60 (97%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **67%** | 82% | 0% | 3/3 | 60/60 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 67% | 3/3 | 60/60 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 3/3 | 60/60 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 6.0 | easy | gemma3:1b |
| Uber Technologies, Inc | 8.6 | easy | gemma3:1b, gemma3:1b-it-qat |
| Uber Technologies, Inc | 2.4 | medium | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.2 — Named institutional investor's ownership percentage (compute)

**Corpus:** 4 real SEC-filed S-1 Security Ownership tables (single-class stock only), human-validated answers (values range 5.2-16.3). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **100%** | 59% | 0% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 78/80 (98%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 0% | 4/4 | 80/80 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 77/80 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **25%** | 99% | 100% | 4/4 | 80/80 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 16.3 | easy | gemma3:1b |
| Uber Technologies, Inc | 11.0 | easy | gemma3:1b |
| Uber Technologies, Inc | 5.3 | medium | gemma3:1b, gpt-oss-120b |
| Uber Technologies, Inc | 5.2 | medium | gemma3:1b |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.2.3 — Employee option pool size as % of total shares (compute)

**Corpus:** 1 real SEC-filed S-1 capitalization narrative, human-validated answers (values range 9.5-9.5). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **100%** | 90% | 0% | 1/1 | 20/20 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 1/1 | 19/20 (95%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 0% | 1/1 | 20/20 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 1/1 | 20/20 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Uber Technologies, Inc | 9.5 | easy | gemma3:1b |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.1 — Securities Act exemption classification

**Corpus:** 10 real SEC Form D filings (structured federalExemptionsExclusions field), human-validated answers (6 506(b) / 4 506(c) / 0 504 / 0 Reg A / 0 other). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **40%** | 90% | 90% | 10/10 | 198/200 (99%) |
| `deepseek-v4-flash` | hosted, direct | **10%** | 98% | 100% | 10/10 | 200/200 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 70% | 10/10 | 200/200 (100%) |
| `minimax-m2.5` | hosted (OR) | **80%** | 93% | 100% | 10/10 | 184/200 (92%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **30%** | 93% | 60% | 10/10 | 200/200 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 193/200 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **10%** | 99% | 100% | 10/10 | 200/200 (100%) |
| `gpt-5-mini` | hosted (OR) | **20%** | 99% | 100% | 10/10 | 200/200 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
- **506(b) · 506(c) · 504 · Reg A · other** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | 506(b) | 506(c) | 504 | Reg A | other |
|---|---|---|---|---|---|
| `gemma3:1b` | 6/6 | 3/4 | — | — | — |
| `deepseek-v4-flash` | 6/6 | 4/4 | — | — | — |
| `deepseek-v4-pro` | 6/6 | 4/4 | — | — | — |
| `gemma-4-31b-it` | 6/6 | 4/4 | — | — | — |
| `mistral-large-2512` | 6/6 | 1/4 | — | — | — |
| `minimax-m2.5` | 6/6 | 4/4 | — | — | — |
| `llama-3.3-70b` | 6/6 | 4/4 | — | — | — |
| `gemma3:1b-it-qat` | 6/6 | 0/4 | — | — | — |
| `gemini-3-flash` | 6/6 | 4/4 | — | — | — |
| `claude-haiku-4.5` | 6/6 | 4/4 | — | — | — |
| `gpt-oss-120b` | 6/6 | 4/4 | — | — | — |
| `gpt-5-mini` | 6/6 | 4/4 | — | — | — |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| ACCELERATED I/O INC | 506b | medium | minimax-m2.5 |
| GTX INC /DE/ | 506b | medium | minimax-m2.5 |
| VoCare, Inc. | 506c | medium | gemma3:1b, minimax-m2.5 |
| Handybook, Inc. | 506b | medium | minimax-m2.5 |
| Brewer Lane Ventures F | 506c | medium | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat |
| Material Impact Fund I | 506c | medium | gemma3:1b, deepseek-v4-flash, minimax-m2.5, gemma3:1b-it-qat |
| NextView Ventures V, L | 506c | medium | gemma3:1b, gemma3:1b-it-qat, gpt-5-mini |
| Devorto Corp | 506b | medium | minimax-m2.5, gpt-oss-120b |
| McBride Sisters Collec | 506b | medium | minimax-m2.5, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–80% across the ladder.** Lowest-wobble model: **deepseek-v4-pro** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.2 — Form D field extraction (Total Amount Sold)

**Corpus:** 2 real SEC Form D filings, human-validated answers (values range 2,366,532-70,227,931.85). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `deepseek-v4-pro` | hosted, direct | **50%** | 98% | 100% | 2/2 | 40/40 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **50%** | 95% | 50% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemini-3-flash` | hosted (OR) | **50%** | 88% | 100% | 2/2 | 36/40 (90%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| NETBASE SOLUTIONS INC  | 2,366,532 | medium | deepseek-v4-pro, llama-3.3-70b, gemini-3-flash |

## What this shows

- **Wobble spread: 0%–50% across the ladder.** Lowest-wobble model: **gemma3:1b** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.2.1 — Total financing round size extraction

**Corpus:** 10 real SEC Form D filings (structured totalAmountSold field, operating companies only), human-validated answers (values range 3728926-21272455). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **20%** | 94% | 40% | 10/10 | 200/200 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `minimax-m2.5` | hosted (OR) | **30%** | 97% | 100% | 10/10 | 200/200 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 30% | 10/10 | 200/200 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 193/200 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 10/10 | 200/200 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| VoCare, Inc. | 5000000 | ? | minimax-m2.5 |
| Handybook, Inc. | 3728926 | ? | minimax-m2.5 |
| TIGO ENERGY INC | 7661116 | ? | minimax-m2.5 |
| POSEIDON MEDICAL INC. | 6085780 | ? | gemma3:1b |
| BEYONDCORE, INC. | 8881213 | ? | gemma3:1b |

## What this shows

- **Wobble spread: 0%–30% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.4.1 — Annual dividend rate percentage extraction

**Corpus:** 6 real venture-financing preferred-stock charters, human-validated answers (values range 6-10). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **33%** | 97% | 83% | 6/6 | 120/120 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 6/6 | 118/120 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **17%** | 94% | 100% | 6/6 | 120/120 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 116/120 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 6/6 | 120/120 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Exela Technologies, In | 10 | ? | gemma3:1b, gemma3:1b-it-qat |
| scPharmaceuticals Inc. | 6 | ? | gemma3:1b |

## What this shows

- **Wobble spread: 0%–33% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.6 — Per-share dilution to new investors (compute)

**Corpus:** 5 real IPO prospectus Dilution-section tables, human-validated answers (values range 1.96-32.89). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **80%** | 75% | 0% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 42/100 (42%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **20%** | 92% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **20%** | 88% | 80% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **20%** | 90% | 0% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 94/100 (94%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Civitas Solutions, Inc | 32.89 | ? | llama-3.3-70b, gpt-oss-120b |
| HyreCar Inc. | 2.09 | ? | gemma3:1b, gemma3:1b-it-qat |
| Castle Biosciences, In | 28.82 | ? | gemma3:1b, minimax-m2.5 |
| Veritone, Inc. | 14.9 | ? | gemma3:1b |
| Axcella Health Inc. | 1.96 | ? | gemma3:1b |

## What this shows

- **Wobble spread: 0%–80% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.4 — Fully-diluted vs issued-outstanding basis classification

**Corpus:** 8 real venture financing exhibits + S-1 capitalization tables, human-validated answers (4 Fully-diluted / 4 Issued-outstanding). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 50% | 8/8 | 160/160 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 8/8 | 127/160 (79%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **25%** | 93% | 62% | 8/8 | 160/160 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 152/160 (95%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 8/8 | 160/160 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 8/8 | 159/160 (99%) |

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
| `deepseek-v4-pro` | 4/4 | 4/4 |
| `gemma-4-31b-it` | 4/4 | 4/4 |
| `mistral-large-2512` | 4/4 | 4/4 |
| `minimax-m2.5` | 4/4 | 4/4 |
| `llama-3.3-70b` | 4/4 | 4/4 |
| `gemma3:1b-it-qat` | 4/4 | 1/4 |
| `gemini-3-flash` | 4/4 | 4/4 |
| `claude-haiku-4.5` | 4/4 | 4/4 |
| `gpt-oss-120b` | 4/4 | 4/4 |
| `gpt-5-mini` | 4/4 | 4/4 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | issued-outstanding | ? | gemma3:1b-it-qat |
| Castle Biosciences, In | issued-outstanding | ? | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 7.5 — Named-period revenue figure extraction

**Corpus:** 5 real S-1 Selected/Summary Financial Data tables, human-validated answers (values range 12619-9777079). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **40%** | 91% | 40% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **20%** | 99% | 80% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **60%** | 81% | 100% | 5/5 | 99/100 (99%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **20%** | 93% | 20% | 5/5 | 95/100 (95%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 96/100 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **40%** | 90% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **20%** | 97% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Civitas Solutions, Inc | 1123118 | ? | gemma3:1b, minimax-m2.5, gemma3:1b-it-qat, gpt-oss-120b |
| IGN Entertainment, Inc | 17541 | ? | mistral-large-2512 |
| Emageon Inc. | 12619 | ? | gemma3:1b, minimax-m2.5 |
| HyreCar Inc. | 9777079 | ? | minimax-m2.5, gpt-oss-120b, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–60% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.6 — Cross-citation share-count consistency flag

**Corpus:** 5 real S-1/424B4 filings, paired share-count citations, human-validated answers (values range False-True). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 60% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 80% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **80%** | 85% | 60% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 96/100 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Actelis Networks, Inc. | False | ? | gemma3:1b-it-qat |
| Castle Biosciences, In | False | ? | gemma3:1b-it-qat |
| Castle Biosciences, In | True | ? | gemma3:1b-it-qat |
| IGN Entertainment, Inc | True | ? | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–80% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 6.5 — Post-termination option exercise window extraction

**Corpus:** 5 real SEC-filed option grant agreement exhibits, human-validated answers (values range 180 days-90 days). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 99/100 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **40%** | 87% | 60% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 96/100 (96%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| SIRVA, Inc. | 30 days | ? | gemma3:1b, gemma3:1b-it-qat |
| Covisint Corp. | 85 days | ? | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 7.4 — S-1 risk-factor heading extraction

**Corpus:** 5 real S-1/424B4 Risk Factors sections, human-validated answers (values range Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results.-We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively.). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **80%** | 65% | 0% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 99/100 (99%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **60%** | 71% | 40% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 97/100 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| HyreCar Inc. | Our limited operating history makes it difficult to evaluate our current business and prospects and may increase the risks associated with your investment. | ? | gemma3:1b-it-qat |
| HyreCar Inc. | If we do not respond appropriately, the evolution of the automotive industry towards autonomous vehicles and mobility on demand services could adversely affect our business. | ? | gemma3:1b, gemma3:1b-it-qat |
| HyreCar Inc. | Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results. | ? | gemma3:1b |
| Axcella Health Inc. | If you purchase our common stock in this offering, you will incur immediate and substantial dilution in the net tangible book value of your shares. | ? | gemma3:1b, gemma3:1b-it-qat |
| Axcella Health Inc. | We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively. | ? | gemma3:1b |

## What this shows

- **Wobble spread: 0%–80% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 8.5 — Explicit pro-rata waiver vs grant flag

**Corpus:** 4 real SEC-filed investor rights agreements + waivers, human-validated answers (values range False-True). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **25%** | 99% | 50% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **25%** | 99% | 100% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **25%** | 94% | 25% | 4/4 | 80/80 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 79/80 (99%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 75% | 4/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **25%** | 99% | 100% | 4/4 | 80/80 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Rapid7, Inc. | True | ? | gemma3:1b, llama-3.3-70b, gpt-oss-120b |
| SOS Hydration Inc. | False | ? | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–25% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 7.3 — Primary use of IPO proceeds extraction

**Corpus:** 5 real S-1/424B4 Use of Proceeds sections, human-validated answers (values range advance our current liver programs-working capital and general corporate purposes). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **20%** | 94% | 20% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **20%** | 96% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **40%** | 89% | 100% | 5/5 | 100/100 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **20%** | 93% | 80% | 5/5 | 98/100 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **20%** | 91% | 25% | 4/5 | 80/100 (80%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 97/100 (97%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 80% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **20%** | 99% | 100% | 5/5 | 100/100 (100%) |
| `gpt-5-mini` | hosted (OR) | **40%** | 90% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Castle Biosciences, In | research and development activities | ? | gemma-4-31b-it, gemma3:1b-it-qat |
| Axcella Health Inc. | advance our current liver programs | ? | gemma3:1b, minimax-m2.5, llama-3.3-70b, gpt-5-mini |
| Veritone, Inc. | working capital and general corporate purposes | ? | gemma3:1b-it-qat, gpt-oss-120b |
| Civitas Solutions, Inc | redeem all of the senior notes | ? | minimax-m2.5, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–40% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 1.2.2 — Named investor's individual dollar allocation extraction

**Corpus:** 5 real SEC Schedule 13D/13D-A filings (investor-side), human-validated answers (values range 46715.64-9418200). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **20%** | 96% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 96/100 (96%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **60%** | 81% | 60% | 5/5 | 100/100 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 92/100 (92%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 5/5 | 99/100 (99%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 5/5 | 100/100 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| CAS Medical Systems, I | 9418200 | ? | gemma3:1b, gemma3:1b-it-qat |
| Ocular Therapeutix, In | 1650000 | ? | gemma3:1b-it-qat |
| Navidea Biopharmaceuti | 3000000 | ? | gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–60% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 3.3 — Pre-money option pool price-per-share compute

**Corpus:** 3 real SEC-filed Agreement for Future Equity worked examples (Form C exhibit), human-validated answers (values range 0.24-0.909). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **33%** | 98% | 0% | 3/3 | 60/60 (100%) |
| `deepseek-v4-flash` | hosted, direct | **33%** | 98% | 33% | 3/3 | 60/60 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 67% | 3/3 | 60/60 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **33%** | 90% | 67% | 3/3 | 60/60 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 67% | 3/3 | 60/60 (100%) |
| `minimax-m2.5` | hosted (OR) | **67%** | 80% | 67% | 3/3 | 60/60 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **33%** | 85% | 67% | 3/3 | 60/60 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **67%** | 87% | 33% | 3/3 | 60/60 (100%) |
| `gemini-3-flash` | hosted (OR) | **33%** | 92% | 33% | 3/3 | 60/60 (100%) |
| `claude-haiku-4.5` | hosted, direct API | **33%** | 97% | 33% | 3/3 | 60/60 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **67%** | 65% | 67% | 3/3 | 60/60 (100%) |
| `gpt-5-mini` | hosted (OR) | **33%** | 98% | 33% | 3/3 | 60/60 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Snapwire Media, Inc. ( | 0.909 | ? | gemma3:1b, deepseek-v4-flash, gemma-4-31b-it, minimax-m2.5, gemma3:1b-it-qat, gemini-3-flash, claude-haiku-4.5, gpt-oss-120b |
| Snapwire Media, Inc. ( | 0.6956 | ? | minimax-m2.5, llama-3.3-70b, gemma3:1b-it-qat, gpt-oss-120b, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–67% across the ladder.** Lowest-wobble model: **deepseek-v4-pro** (0% wobble, 67% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 4.4 — Convert-vs-take-preference decision (compute)

**Corpus:** 2 real SEC-filed Agreement for Future Equity worked examples (Form C exhibit), human-validated answers (1 Convert / 1 Take preference). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **0%** | 100% | 50% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **0%** | 100% | 50% | 2/2 | 40/40 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

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
| `deepseek-v4-pro` | 1/1 | 1/1 |
| `gemma-4-31b-it` | 1/1 | 1/1 |
| `mistral-large-2512` | 1/1 | 1/1 |
| `minimax-m2.5` | 1/1 | 1/1 |
| `llama-3.3-70b` | 1/1 | 1/1 |
| `gemma3:1b-it-qat` | 1/1 | 0/1 |
| `gemini-3-flash` | 1/1 | 1/1 |
| `claude-haiku-4.5` | 1/1 | 1/1 |
| `gpt-oss-120b` | 1/1 | 1/1 |
| `gpt-5-mini` | 1/1 | 1/1 |

### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|

## What this shows

- **Wobble spread: 0%–0% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).

---

## Test 4.1 — Per-share value to common after preferred waterfall (compute)

**Corpus:** 4 real SC 13E-3 going-private fairness opinion, human-validated answers (values range 0.39-0.51). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **100%** | 61% | 0% | 4/4 | 80/80 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 4/4 | 75/80 (94%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 75% | 4/4 | 80/80 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **100%** | 81% | 75% | 4/4 | 80/80 (100%) |
| `mistral-large-2512` | hosted (OR) | **25%** | 91% | 75% | 4/4 | 80/80 (100%) |
| `minimax-m2.5` | hosted (OR) | **50%** | 88% | 75% | 4/4 | 80/80 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **75%** | 78% | 25% | 4/4 | 80/80 (100%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **75%** | 95% | 25% | 4/4 | 80/80 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 75% | 4/4 | 76/80 (95%) |
| `claude-haiku-4.5` | hosted, direct API | **50%** | 84% | 0% | 4/4 | 80/80 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **100%** | 78% | 50% | 4/4 | 78/80 (98%) |
| `gpt-5-mini` | hosted (OR) | **100%** | 56% | 50% | 4/4 | 80/80 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Connecture, Inc. | 0.51 | ? | gemma3:1b, gemma-4-31b-it, mistral-large-2512, llama-3.3-70b, claude-haiku-4.5, gpt-oss-120b, gpt-5-mini |
| Connecture, Inc. | 0.42 | ? | gemma3:1b, gemma-4-31b-it, minimax-m2.5, gemma3:1b-it-qat, claude-haiku-4.5, gpt-oss-120b, gpt-5-mini |
| Connecture, Inc. | 0.39 | ? | gemma3:1b, gemma-4-31b-it, minimax-m2.5, llama-3.3-70b, gemma3:1b-it-qat, gpt-oss-120b, gpt-5-mini |
| Connecture, Inc. | 0.44 | ? | gemma3:1b, gemma-4-31b-it, llama-3.3-70b, gemma3:1b-it-qat, gpt-oss-120b, gpt-5-mini |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
- **Wobble is a cliff, not a slope** — small models flip on a large share of items while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.

---

## Test 4.3 — Named preferred series' total waterfall payout (compute)

**Corpus:** 2 real SC 13E-3 going-private fairness opinion, human-validated answers (values range 19.7-58.9). Each model run **20×/item at temp 0.1**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B, local | **100%** | 72% | 50% | 2/2 | 40/40 (100%) |
| `deepseek-v4-flash` | hosted, direct | **0%** | 100% | 100% | 2/2 | 39/40 (98%) |
| `deepseek-v4-pro` | hosted, direct | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gemma-4-31b-it` | 31B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `mistral-large-2512` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `minimax-m2.5` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `llama-3.3-70b` | 70B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 39/40 (98%) |
| `gemma3:1b-it-qat` | 1B QAT, local | **100%** | 43% | 0% | 2/2 | 40/40 (100%) |
| `gemini-3-flash` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `claude-haiku-4.5` | hosted, direct API | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-oss-120b` | 120B, hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |
| `gpt-5-mini` | hosted (OR) | **0%** | 100% | 100% | 2/2 | 40/40 (100%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.


### Which items make models wobble

| Item | True | Difficulty | Models that wobbled |
|---|---|---|---|
| Connecture, Inc. | 58.9 | ? | gemma3:1b, gemma3:1b-it-qat |
| Connecture, Inc. | 19.7 | ? | gemma3:1b, gemma3:1b-it-qat |

## What this shows

- **Wobble spread: 0%–100% across the ladder.** Lowest-wobble model: **deepseek-v4-flash** (0% wobble, 100% accuracy).
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

