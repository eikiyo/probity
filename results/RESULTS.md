# Probity — Benchmark Results

**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a human-validated answer extracted from the source document. They are reported separately and never averaged — a model can be perfectly consistent and consistently wrong.

Models span a size ladder (1B → 27B local + a hosted model) to test whether wobble falls as capability rises. Local via Ollama (zero egress); hosted = deepseek-v4-flash.

---

## Test 1.3.2 — Preferred-stock liquidation participation

**Corpus:** 18 real SEC-filed charter clauses, human-validated answers (8 non-participating / 5 participating / 5 capped). Each model run **20×/item at temp 0.7**.

### Headline — WOBBLE (the core metric)

*Wobble = % of items where the model gave more than one answer across its 20 runs. A model that wobbles cannot be trusted in a money workflow even when it is often right.*

| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **61%** | 90% | 39% | 18/18 |
| `llama3.2:latest` | 3B | **72%** | 84% | 44% | 18/18 |
| `gemma4:12b` | 12B | **0%** | 100% | 72% | 18/18 |
| `deepseek-v4-flash` | hosted | **6%** | 98% | 67% | 18/18 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's 20 runs (how often they matched that item's most common answer). It differs from Wobble: an item that flips even once is counted as wobble, yet can still be (say) 90% consistent. Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **non-part / part / capped** — accuracy **within** each true class (correct / total: non-participating · participating · capped), so a model can't score well by always guessing the most common class.


### Accuracy by class (majority vote)

| Model | non-participating | participating | capped |
|---|---|---|---|
| `gemma3:1b` | 7/8 | 0/5 | 0/5 |
| `llama3.2:latest` | 7/8 | 0/5 | 1/5 |
| `gemma4:12b` | 6/8 | 2/5 | 5/5 |
| `deepseek-v4-flash` | 6/8 | 1/5 | 5/5 |

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

---

## What this shows

- **Wobble has a cliff, not a slope.** The 1B and 3B models flip their answer on 61-72% of items
  across 20 runs at temp 0.7 - unusable in a workflow that touches money. At 12B wobble collapses
  to 0%; the hosted model sits at 6%. The usable/unusable boundary is between 3B and 12B, not a
  smooth gradient. (N=5 hid this entirely - both mid/hosted models looked perfectly stable.)
- **A local 12B model beats a hosted frontier-cheap model here.** gemma4:12b: 0% wobble, 72%
  accuracy. deepseek-v4-flash: 6% wobble, 67%. Bigger-and-hosted is not automatically better.
- **Participating preferred is the universal blind spot.** Even the best models get only 1-2 of 5
  participating clauses right; the small models get 0. The "preference AND THEN also share with the
  common" structure is systematically misread as capped or non-participating. The genuinely-hard,
  validated structure - not random noise - is where every model fails.
- **Small models can't classify the hard classes at all** (1B: 0/5 participating, 0/5 capped) -
  they collapse everything to non-participating.

## Models and scope

Per leaf during the build-out, Probity runs the **fast set** (1B/3B/12B local via Ollama, zero
egress, plus deepseek-v4-flash) so a leaf costs minutes. The **heavy comprehensive run**
(qwen3.5:27b and hosted frontier models - Gemini, Haiku, etc. - at N=20+) is deferred to a single
sweep across all leaves once the full benchmark exists.

## Reproduce

```bash
cd leaves/participation_type
python3 source.py && python3 source_more.py   # fetch real SEC charter clauses
python3 run.py                                # run the model ladder, N=20
python3 ../../results/render.py
```

Corpus: real SEC EDGAR charter exhibits; answers human-validated from each clause's own legal text
(`leaves/participation_type/oracle.jsonl`, with the validating quote + difficulty per item).
Genuinely mixed-series or ambiguous clauses are excluded, not guessed.

