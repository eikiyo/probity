# Probity

[![CI](https://github.com/eikiyo/probity/actions/workflows/ci.yml/badge.svg)](https://github.com/eikiyo/probity/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

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

## Quickstart

No install needed to read the results — every leaf's scored output is already committed:

```bash
git clone https://github.com/eikiyo/probity.git
cd probity
make setup     # runs the test suite + regenerates results/RESULTS.md + this README's tables from disk
```

That's it — zero third-party dependencies, pure Python 3 stdlib, no network call, no API key.
(No `make`? `python3 -m unittest discover -s tests && python3 results/render.py` does the same thing.)

To **re-run a test yourself** against live models (needs [Ollama](https://ollama.com) running
`gemma3:1b` locally + a DeepSeek API key — see [`.env.example`](.env.example)):

```bash
cp .env.example .env && set -a && source .env && set +a
cd leaves/vesting_schedule       # or any other leaf under leaves/
python3 source.py                # fetch the real SEC documents into corpus/
python3 run.py                   # run the model ladder, N=20 each, writes scored.json
python3 ../../results/render.py  # regenerate the tables with your fresh numbers
```

## Benchmark results

<!-- BENCHMARK:START -->
*60 tests so far. Each model run 20×/item at temp 0.7. **Wobble** = % of items answered inconsistently across runs. During build-out a leaf is run on the fast set (gemma3:1b + deepseek); the heavier rows (llama3.2 3B, gemma4:12b, and hosted frontier models) are filled in by one comprehensive sweep once every leaf exists, which is why newer leaves show fewer rows for now.*

**Test 1.3.2 — Preferred-stock liquidation participation** — 18 clauses (6 part / 7 non-part / 5 capped), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | part | non-part | capped |
|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **72%** | 89% | 33% | 312/360 (87%) | 0/6 | 6/7 | 0/5 |
| `deepseek-v4-flash` | hosted | **11%** | 98% | 67% | 342/360 (95%) | 1/6 | 6/7 | 5/5 |

**Test 2.1.4 — SAFE valuation cap: pre-money vs post-money** — 16 clauses (10 post / 6 pre), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | post | pre |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **6%** | 98% | 62% | 128/320 (40%) | 10/10 | 0/6 |
| `llama3.2:latest` | 3B | **56%** | 88% | 81% | 320/320 (100%) | 10/10 | 3/6 |
| `gemma4:12b` | 12B | **0%** | 100% | 100% | 320/320 (100%) | 10/10 | 6/6 |
| `deepseek-v4-flash` | hosted | **19%** | 99% | 100% | 320/320 (100%) | 10/10 | 6/6 |

**Test 1.4.2 — Preferred dividends: cumulative vs non-cumulative** — 16 clauses (8 cumulative / 8 non-cum), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | cumulative | non-cum |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 88% | 320/320 (100%) | 7/8 | 7/8 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 320/320 (100%) | 8/8 | 8/8 |

**Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger** — 13 clauses (6 single / 7 double), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | single | double |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 97% | 85% | 259/260 (100%) | 4/6 | 7/7 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 260/260 (100%) | 6/6 | 7/7 |

**Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked** — 11 clauses (6 pari-passu / 5 stacked), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | pari-passu | stacked |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **45%** | 97% | 45% | 215/220 (98%) | 0/6 | 5/5 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 82% | 220/220 (100%) | 4/6 | 5/5 |

**Test 8.1 — Risk flag: off-market liquidation preference (>1x)** — 10 clauses (5 off-market(>1x) / 5 standard(1x)), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | off-market(>1x) | standard(1x) |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 95% | 40% | 197/200 (98%) | 3/5 | 1/5 |
| `deepseek-v4-flash` | hosted | **10%** | 99% | 90% | 200/200 (100%) | 5/5 | 4/5 |

**Test 1.7 — Redemption rights: redeemable vs non-redeemable** — 10 clauses (5 redeemable / 5 non-redeem), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | redeemable | non-redeem |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 97% | 50% | 200/200 (100%) | 0/5 | 5/5 |
| `deepseek-v4-flash` | hosted | **10%** | 96% | 100% | 200/200 (100%) | 5/5 | 5/5 |

**Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)** — 12 clauses (6 drag(obligated) / 6 co-sale(right)), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | drag(obligated) | co-sale(right) |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 99% | 42% | 238/240 (99%) | 4/6 | 1/6 |
| `deepseek-v4-flash` | hosted | **8%** | 97% | 100% | 240/240 (100%) | 6/6 | 6/6 |

**Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent** — 12 clauses (6 rofr/cosale / 6 absent/other-right), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | rofr/cosale | absent/other-right |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 98% | 67% | 238/240 (99%) | 6/6 | 2/6 |
| `deepseek-v4-flash` | hosted | **17%** | 94% | 92% | 240/240 (100%) | 6/6 | 5/6 |

**Test 5.4 — Pro-rata right on future financings: granted vs not** — 12 clauses (6 pro-rata / 6 absent/waived), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | pro-rata | absent/waived |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 94% | 100% | 101/240 (42%) | 6/6 | 6/6 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 240/240 (100%) | 6/6 | 6/6 |

**Test 6.2 — Vesting schedule: cliff present vs absent** — 12 clauses (6 cliff / 6 no-cliff), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | cliff | no-cliff |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 96% | 67% | 239/240 (100%) | 6/6 | 2/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 240/240 (100%) | 6/6 | 5/6 |

**Test 5.2 — Protective provisions: investor class-veto right present vs absent** — 12 clauses (6 veto-right / 6 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | veto-right | absent |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 97% | 58% | 239/240 (100%) | 6/6 | 1/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 240/240 (100%) | 6/6 | 6/6 |

**Test 5.3 — Information rights: live financial-reporting obligation vs absent** — 12 clauses (6 info-rights / 6 absent/waived), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | info-rights | absent/waived |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 95% | 50% | 233/240 (97%) | 6/6 | 0/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 240/240 (100%) | 5/6 | 6/6 |

**Test 5.7 — Vesting acceleration: granted on trigger vs absent** — 9 clauses (6 accelerates / 3 no-acceleration), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | accelerates | no-acceleration |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 67% | 174/180 (97%) | 4/6 | 2/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 180/180 (100%) | 6/6 | 3/3 |

**Test 1.3.1 — Liquidation preference multiple: 1x vs 2x vs 3x vs other** — 9 clauses (0 non-part / 3 1x / 3 2x / 3 3x / 0 other), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | non-part | 1x | 2x | 3x | other |
|---|---|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **56%** | 94% | 0% | 144/180 (80%) | - | 0/3 | 0/3 | 0/3 | - |
| `deepseek-v4-flash` | hosted | **33%** | 92% | 67% | 180/180 (100%) | - | 2/3 | 1/3 | 3/3 | - |

**Test 5.1 — Board seats: number an investor has the right to designate** — 9 clauses (values range 1-9), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 92% | 78% | 176/180 (98%) |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 78% | 180/180 (100%) |

**Test 2.1.6 — SAFE pro-rata side letter: granted vs absent** — 15 clauses (9 pro-rata / 6 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | pro-rata | absent |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 96% | 93% | 134/300 (45%) | 9/9 | 5/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 300/300 (100%) | 9/9 | 6/6 |

**Test 1.1.2 — Priced round basis: pre-money vs post-money** — 19 clauses (13 pre / 6 post), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | pre | post |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 83% | 68% | 363/380 (96%) | 7/13 | 6/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 95% | 380/380 (100%) | 13/13 | 5/6 |

**Test 8.2 — Risk flag: full-ratchet anti-dilution present vs absent** — 7 clauses (4 full-ratchet / 3 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | full-ratchet | absent |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 98% | 57% | 130/140 (93%) | 4/4 | 0/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 140/140 (100%) | 4/4 | 3/3 |

**Test 1.1.1 — Post-money valuation extraction** — 4 clauses (values range 5000000-275000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 25% | 60/80 (75%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 80/80 (100%) |

**Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none** — 5 clauses (2 full-ratchet / 2 weighted-avg / 0 broad-based / 0 narrow-based / 1 none), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | full-ratchet | weighted-avg | broad-based | narrow-based | none |
|---|---|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 99% | 40% | 98/100 (98%) | 2/2 | 0/2 | - | - | 0/1 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) | 2/2 | 2/2 | - | - | 1/1 |

**Test 8.3 — Risk flag: uncapped participating-preferred present vs absent** — 13 clauses (4 uncapped / 9 capped/none), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | uncapped | capped/none |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **8%** | 99% | 31% | 195/260 (75%) | 4/4 | 0/9 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 85% | 260/260 (100%) | 2/4 | 9/9 |

**Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent** — 7 clauses (4 MFN / 3 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | MFN | absent |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 95% | 100% | 93/140 (66%) | 4/4 | 3/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 140/140 (100%) | 4/4 | 3/3 |

**Test 1.3.3 — Participation cap multiple extraction** — 3 clauses (values range 3-3.5), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 58/60 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 60/60 (100%) |

**Test 6.4 — Stock option exercise (strike) price extraction** — 7 clauses (values range 0.03-11.0), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 86% | 71% | 133/140 (95%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 140/140 (100%) |

**Test 2.1.1 — SAFE valuation cap extraction** — 8 clauses (values range 15000000-150000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 96% | 88% | 144/160 (90%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 160/160 (100%) |

**Test 2.2.1 — Convertible note principal amount extraction** — 7 clauses (values range 12500-17364375), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 138/140 (99%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 140/140 (100%) |

**Test 2.1.2 — SAFE discount rate extraction** — 9 clauses (values range 10-50), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 89% | 56% | 160/180 (89%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 180/180 (100%) |

**Test 2.2.4 — Convertible note valuation cap extraction** — 4 clauses (values range 25000000-125000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 91% | 75% | 72/80 (90%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 80/80 (100%) |

**Test 1.6.1 — Preferred-stock conversion ratio extraction** — 5 clauses (values range 1-8000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 92% | 80% | 99/100 (99%) |
| `deepseek-v4-flash` | hosted | **20%** | 98% | 100% | 100/100 (100%) |

**Test 1.5.2 — Anti-dilution weighted-average base: broad-based vs narrow-based vs n/a** — 10 clauses (3 broad / 4 narrow / 3 n/a), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | broad | narrow | n/a |
|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 96% | 70% | 199/200 (100%) | 3/3 | 4/4 | 0/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 200/200 (100%) | 3/3 | 4/4 | 3/3 |

**Test 1.6.2 — Automatic conversion (QPO) proceeds threshold extraction** — 5 clauses (values range 30000000-100000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 100/100 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) |

**Test 2.2.2 — Convertible note interest rate extraction** — 6 clauses (values range 0.28-10.0), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 83% | 113/120 (94%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 120/120 (100%) |

**Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)** — 13 clauses (2 cap / 1 discount / 10 both-mfn), each model run 17×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | cap | discount | both-mfn |
|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 90% | 77% | 158/260 (61%) | 2/2 | 0/1 | 8/10 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 221/260 (85%) | 2/2 | 1/1 | 10/10 |

**Test 1.1.3 — Priced-round price-per-share extraction** — 8 clauses (values range 0.2-1000.0), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 92% | 62% | 156/160 (98%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 62% | 147/160 (92%) |

**Test 2.2.3 — Convertible note maturity date extraction** — 4 clauses (values range 2005-03-31-2026-12-31), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 94% | 50% | 75/80 (94%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 80/80 (100%) |

**Test 2.2.5 — Convertible note conversion-discount rate extraction** — 4 clauses (values range 5.0-50.0), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **25%** | 94% | 0% | 46/80 (57%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 80/80 (100%) |

**Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction** — 2 clauses (values range 10000000-40000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 97% | 100% | 37/40 (92%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 40/40 (100%) |

**Test 6.1 — Equity vesting schedule extraction + normalization** — 9 clauses (values range 1.5yr/no-cliff-4yr/no-cliff), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 38% | 65/180 (36%) |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 100% | 180/180 (100%) |

**Test 3.1 — Cap-table current ownership percentage (compute)** — 9 clauses (values range 2.4-33.9), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 16% | 0% | 146/180 (81%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 179/180 (99%) |

**Test 3.2.1 — Named founder's ownership percentage (compute)** — 3 clauses (values range 2.4-8.6), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 18% | 0% | 60/60 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 60/60 (100%) |

**Test 3.2.2 — Named institutional investor's ownership percentage (compute)** — 4 clauses (values range 5.2-16.3), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 38% | 0% | 80/80 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 80/80 (100%) |

**Test 3.2.3 — Employee option pool size as % of total shares (compute)** — 1 clauses (values range 9.5-9.5), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 47% | 0% | 17/20 (85%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 20/20 (100%) |

**Test 7.1 — Securities Act exemption classification** — 10 clauses (6 506(b) / 4 506(c) / 0 504 / 0 Reg A / 0 other), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | 506(b) | 506(c) | 504 | Reg A | other |
|---|---|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 86% | 100% | 170/200 (85%) | 6/6 | 4/4 | - | - | - |
| `deepseek-v4-flash` | hosted | **30%** | 96% | 100% | 200/200 (100%) | 6/6 | 4/4 | - | - | - |

**Test 7.2 — Form D field extraction (Total Amount Sold)** — 2 clauses (values range 2,366,532-70,227,931.85), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 16/40 (40%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 40/40 (100%) |

**Test 1.2.1 — Total financing round size extraction** — 10 clauses (values range 3728926-21272455), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 87% | 30% | 199/200 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 200/200 (100%) |

**Test 1.4.1 — Annual dividend rate percentage extraction** — 6 clauses (values range 6-10), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% | 23/120 (19%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 120/120 (100%) |

**Test 3.6 — Per-share dilution to new investors (compute)** — 5 clauses (values range 1.96-32.89), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **80%** | 49% | 0% | 96/100 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) |

**Test 3.4 — Fully-diluted vs issued-outstanding basis classification** — 8 clauses (4 Fully-diluted / 4 Issued-outstanding), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | Fully-diluted | Issued-outstanding |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 64% | 50% | 152/160 (95%) | 4/4 | 0/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 160/160 (100%) | 4/4 | 4/4 |

**Test 7.5 — Named-period revenue figure extraction** — 5 clauses (values range 12619-9777079), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 86% | 20% | 97/100 (97%) |
| `deepseek-v4-flash` | hosted | **20%** | 97% | 100% | 100/100 (100%) |

**Test 8.6 — Cross-citation share-count consistency flag** — 5 clauses (values range False-True), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 60% | 99/100 (99%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) |

**Test 6.5 — Post-termination option exercise window extraction** — 5 clauses (values range 180 days-90 days), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 87% | 80% | 96/100 (96%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) |

**Test 7.4 — S-1 risk-factor heading extraction** — 5 clauses (values range Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results.-We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively.), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 24% | 0% | 97/100 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) |

**Test 8.5 — Explicit pro-rata waiver vs grant flag** — 4 clauses (values range False-True), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 93% | 50% | 79/80 (99%) |
| `deepseek-v4-flash` | hosted | **25%** | 96% | 100% | 80/80 (100%) |

**Test 7.3 — Primary use of IPO proceeds extraction** — 5 clauses (values range advance our current liver programs-working capital and general corporate purposes), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 68% | 20% | 83/100 (83%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 100/100 (100%) |

**Test 1.2.2 — Named investor's individual dollar allocation extraction** — 5 clauses (values range 46715.64-9418200), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 91% | 80% | 97/100 (97%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 80/100 (80%) |

**Test 3.3 — Pre-money option pool price-per-share compute** — 3 clauses (values range 0.24-0.909), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 62% | 0% | 60/60 (100%) |
| `deepseek-v4-flash` | hosted | **67%** | 91% | 33% | 44/60 (73%) |

**Test 4.4 — Convert-vs-take-preference decision (compute)** — 2 clauses (1 Convert / 1 Take preference), each model run 18×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate | Convert | Take preference |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 50% | 37/40 (92%) | 1/1 | 0/1 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 27/40 (68%) | 1/1 | 1/1 |

**Test 4.1 — Per-share value to common after preferred waterfall (compute)** — 4 clauses (values range 0.39-0.51), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 17% | 0% | 77/80 (96%) |
| `deepseek-v4-flash` | hosted | **25%** | 99% | 100% | 62/80 (78%) |

**Test 4.3 — Named preferred series' total waterfall payout (compute)** — 2 clauses (values range 19.7-58.9), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate |
|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 52% | 50% | 40/40 (100%) |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 24/40 (60%) |

**What the columns mean:**

- **Wobble** (headline, lower is better) — the share of items where the model gave **more than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money workflow even when it's often right.
- **Consistency** — the *average* agreement **within** each item's runs (how often they matched that item's most common answer). Wobble counts *whether* an item flipped; Consistency measures *how much*.
- **Accuracy** — the share of items whose majority answer matched the human-validated truth.
- **Response rate** — the share of the model's attempted runs that returned a parseable answer at all (parsed / attempted). A run can fail to parse for two different reasons: the model emitted malformed/non-JSON output, or the API call itself errored (rate limit, timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a low response rate is a distinct reliability signal, not folded into either headline number — a model can look perfectly consistent and accurate while silently failing to answer a meaningful share of the time.
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

See the [Quickstart](#quickstart) above for the full clone → run → reproduce path.

## Contributing

Bug reports, new leaves, and sourcing improvements are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md). Security issues: see [SECURITY.md](SECURITY.md), never a
public issue.

## License

MIT — see [LICENSE](LICENSE).
