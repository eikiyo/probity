# Probity

**A reliability + accuracy benchmark for LLMs on real fundraising documents.**

Probity measures how trustworthy a language model is when it reads the legal and financial
documents that decide who owns what in a startup financing — term sheets, charters, SAFEs,
convertible notes, cap tables. It reports two numbers that are usually conflated and shouldn't be:

- **Wobble** (the core metric) — does the model give the *same* answer when you ask it the same
  question 20 times at temperature 0.7? A model whose answer flips run to run cannot be trusted in
  a workflow that touches money, even when it is often right. This is label-free: it needs no
  ground truth, only repetition.
- **Accuracy** — does the model get the answer *right*, graded against a validated answer that a
  human extracted from the source document (not authored by an AI)?

These are scored separately and never averaged into one headline — a model can be perfectly
consistent and consistently wrong. Models are run across a **size ladder** (1B → 12B local, plus a
hosted model) to test whether wobble falls as capability rises. Heavier models (a 27B local model
and hosted frontier models) are reserved for a single comprehensive sweep once every test is built.

## Benchmark results

<!-- BENCHMARK:START -->
*6 tests so far. Each model run 20×/item at temp 0.7. **Wobble** = % of items answered inconsistently across runs. During build-out a leaf is run on the fast set (gemma3:1b + deepseek); the heavier rows (llama3.2 3B, gemma4:12b, and hosted frontier models) are filled in by one comprehensive sweep once every leaf exists, which is why newer leaves show fewer rows for now.*

**Test 1.3.2 — Preferred-stock liquidation participation** — 18 clauses (5 part / 8 non-part / 5 capped), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | part | non-part | capped |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **61%** | 90% | 39% | 0/5 | 7/8 | 0/5 |
| `llama3.2:latest` | 3B | **72%** | 84% | 44% | 0/5 | 7/8 | 1/5 |
| `gemma4:12b` | 12B | **0%** | 100% | 72% | 2/5 | 6/8 | 5/5 |
| `deepseek-v4-flash` | hosted | **6%** | 98% | 67% | 1/5 | 6/8 | 5/5 |

**Test 2.1.4 — SAFE valuation cap: pre-money vs post-money** — 16 clauses (10 post / 6 pre), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | post | pre |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **6%** | 98% | 62% | 10/10 | 0/6 |
| `llama3.2:latest` | 3B | **56%** | 88% | 81% | 10/10 | 3/6 |
| `gemma4:12b` | 12B | **0%** | 100% | 100% | 10/10 | 6/6 |
| `deepseek-v4-flash` | hosted | **19%** | 99% | 100% | 10/10 | 6/6 |

**Test 1.4.2 — Preferred dividends: cumulative vs non-cumulative** — 16 clauses (8 cumulative / 8 non-cum), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | cumulative | non-cum |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 88% | 7/8 | 7/8 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 8/8 | 8/8 |

**Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger** — 13 clauses (6 single / 7 double), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | single | double |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 97% | 85% | 4/6 | 7/7 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 7/7 |

**Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked** — 11 clauses (6 pari-passu / 5 stacked), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | pari-passu | stacked |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **45%** | 97% | 45% | 0/6 | 5/5 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 82% | 4/6 | 5/5 |

**Test 8.1 — Risk flag: off-market liquidation preference (>1x)** — 10 clauses (5 off-market(>1x) / 5 standard(1x)), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | off-market(>1x) | standard(1x) |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 95% | 40% | 3/5 | 1/5 |
| `deepseek-v4-flash` | hosted | **10%** | 99% | 90% | 5/5 | 4/5 |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **the right-hand class columns** — accuracy **within** each true class (correct / total), so a model can't score well by always guessing the most common class.
<!-- BENCHMARK:END -->

Full per-item breakdown — including which clauses make each model wobble — in
[`results/RESULTS.md`](results/RESULTS.md).

## Why the answers are trustworthy

Most LLM benchmarks in niche domains are built from synthetic data with synthetic answers. That has
a hidden flaw: if an AI writes both the question and the answer key, the answer key can be wrong in
exactly the ways the model under test is wrong. Probity avoids this with a strict **oracle layer**:

1. **Source a real document** that contains the ground truth in its own authoritative text — for
   example, a Certificate of Incorporation filed with the SEC that states, in legally precise
   language, whether its preferred stock is participating.
2. **A human separates the question from the answer.** The model sees only the clause (the question).
   The validated label, plus the exact quote that proves it, is stored in a separate oracle file the
   model never sees. Items whose answer cannot be determined with confidence are *excluded*, not guessed.
3. **Run only the question** through each model, N times, and score the majority answer against the
   validated label.

Synthetic instantiation is used only to *multiply* difficulty (varying numbers, off-market terms,
ambiguous phrasing) on top of a real, human-validated seed — never as the sole source of truth.

## The test map

Probity's full test backlog is a structured map of fundraising-reasoning capabilities
(`engine/registry.json`) — 67 atomic checks across priced equity, convertibles, cap-table math,
exit waterfalls, investor rights, founder equity, regulatory filings, and off-market risk flags.
Each check is built one at a time, to depth, against real sourced documents.

## Structure

```
engine/    the model-agnostic core: clients, run harness, normalizer, reliability+accuracy scorers
leaves/    one folder per test, each with its real-document corpus, its separated oracle, and its runner
results/   the living benchmark table
```

## Running a test

```bash
cd leaves/<test_name>
python3 run.py          # runs the corpus through gemma + DeepSeek, scores accuracy + reliability
```

Models default to a local Ollama model (`gemma4:12b`, zero egress) and DeepSeek (`deepseek-v4-flash`).
API keys are read from the environment, never committed.

## License

MIT — see [LICENSE](LICENSE).
