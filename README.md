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
*60 tests so far. Each model run 20×/item at temp 0.7. **Wobble** = % of items answered inconsistently across runs. During build-out a leaf is run on the fast set (gemma3:1b + deepseek); the heavier rows (llama3.2 3B, gemma4:12b, and hosted frontier models) are filled in by one comprehensive sweep once every leaf exists, which is why newer leaves show fewer rows for now.*

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

**Test 1.7 — Redemption rights: redeemable vs non-redeemable** — 10 clauses (5 redeemable / 5 non-redeem), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | redeemable | non-redeem |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 97% | 50% | 0/5 | 5/5 |
| `deepseek-v4-flash` | hosted | **10%** | 96% | 100% | 5/5 | 5/5 |

**Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)** — 12 clauses (6 drag(obligated) / 6 co-sale(right)), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | drag(obligated) | co-sale(right) |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 99% | 42% | 4/6 | 1/6 |
| `deepseek-v4-flash` | hosted | **8%** | 97% | 100% | 6/6 | 6/6 |

**Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent** — 12 clauses (6 rofr/cosale / 6 absent/other-right), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | rofr/cosale | absent/other-right |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 98% | 67% | 6/6 | 2/6 |
| `deepseek-v4-flash` | hosted | **17%** | 94% | 92% | 6/6 | 5/6 |

**Test 5.4 — Pro-rata right on future financings: granted vs not** — 12 clauses (6 pro-rata / 6 absent/waived), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | pro-rata | absent/waived |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 94% | 100% | 6/6 | 6/6 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 100% | 6/6 | 6/6 |

**Test 6.2 — Vesting schedule: cliff present vs absent** — 12 clauses (6 cliff / 6 no-cliff), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | cliff | no-cliff |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 96% | 67% | 6/6 | 2/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 6/6 | 5/6 |

**Test 5.2 — Protective provisions: investor class-veto right present vs absent** — 12 clauses (6 veto-right / 6 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | veto-right | absent |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 97% | 58% | 6/6 | 1/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 6/6 |

**Test 5.3 — Information rights: live financial-reporting obligation vs absent** — 12 clauses (6 info-rights / 6 absent/waived), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | info-rights | absent/waived |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **17%** | 95% | 50% | 6/6 | 0/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 92% | 5/6 | 6/6 |

**Test 5.7 — Vesting acceleration: granted on trigger vs absent** — 9 clauses (6 accelerates / 3 no-acceleration), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | accelerates | no-acceleration |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 93% | 67% | 4/6 | 2/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 6/6 | 3/3 |

**Test 1.3.1 — Liquidation preference multiple: 1x vs 2x vs 3x vs other** — 13 clauses (0 non-part / 4 1x / 5 2x / 4 3x / 0 other), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | non-part | 1x | 2x | 3x | other |
|---|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **46%** | 91% | 0% | - | 0/4 | 0/5 | 0/3 | - |
| `deepseek-v4-flash` | hosted | **46%** | 87% | 62% | - | 3/4 | 1/5 | 4/4 | - |

**Test 5.1 — Board seats: number an investor has the right to designate** — 9 clauses (values range 1-9), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 92% | 78% |
| `deepseek-v4-flash` | hosted | **11%** | 97% | 78% |

**Test 2.1.6 — SAFE pro-rata side letter: granted vs absent** — 15 clauses (9 pro-rata / 6 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | pro-rata | absent |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 96% | 93% | 9/9 | 5/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 9/9 | 6/6 |

**Test 1.1.2 — Priced round basis: pre-money vs post-money** — 21 clauses (15 pre / 6 post), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | pre | post |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **86%** | 84% | 71% | 9/15 | 6/6 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 95% | 15/15 | 5/6 |

**Test 8.2 — Risk flag: full-ratchet anti-dilution present vs absent** — 7 clauses (4 full-ratchet / 3 absent), each model run 28×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | full-ratchet | absent |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 57% | 4/4 | 0/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 86% | 4/4 | 2/3 |

**Test 1.1.1 — Post-money valuation extraction** — 4 clauses (values range 5000000-275000000), each model run 30×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **25%** | 96% | 25% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 50% |

**Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none** — 5 clauses (2 full-ratchet / 2 weighted-avg / 0 broad-based / 0 narrow-based / 1 none), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | full-ratchet | weighted-avg | broad-based | narrow-based | none |
|---|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 40% | 2/2 | 0/2 | - | - | 0/1 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 2/2 | 2/2 | - | - | 1/1 |

**Test 8.3 — Risk flag: uncapped participating-preferred present vs absent** — 13 clauses (4 uncapped / 9 capped/none), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | uncapped | capped/none |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **8%** | 99% | 31% | 4/4 | 0/9 |
| `deepseek-v4-flash` | hosted | **8%** | 100% | 85% | 2/4 | 9/9 |

**Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent** — 7 clauses (4 MFN / 3 absent), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | MFN | absent |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **29%** | 95% | 100% | 4/4 | 3/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 3/3 |

**Test 1.3.3 — Participation cap multiple extraction** — 3 clauses (values range 3-3.5), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 6.4 — Stock option exercise (strike) price extraction** — 7 clauses (values range 0.03-11.0), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **71%** | 87% | 57% |
| `deepseek-v4-flash` | hosted | **29%** | 90% | 43% |

**Test 2.1.1 — SAFE valuation cap extraction** — 8 clauses (values range 15000000-150000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **38%** | 96% | 88% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.2.1 — Convertible note principal amount extraction** — 7 clauses (values range 12500-17364375), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.1.2 — SAFE discount rate extraction** — 9 clauses (values range 10-50), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **44%** | 89% | 56% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.2.4 — Convertible note valuation cap extraction** — 4 clauses (values range 25000000-125000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 88% | 50% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 1.6.1 — Preferred-stock conversion ratio extraction** — 5 clauses (values range 1-8000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 92% | 80% |
| `deepseek-v4-flash` | hosted | **20%** | 98% | 100% |

**Test 1.5.2 — Anti-dilution weighted-average base: broad-based vs narrow-based vs n/a** — 10 clauses (3 broad / 4 narrow / 3 n/a), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | broad | narrow | n/a |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 96% | 70% | 3/3 | 4/4 | 0/3 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 3/3 | 4/4 | 3/3 |

**Test 1.6.2 — Automatic conversion (QPO) proceeds threshold extraction** — 5 clauses (values range 30000000-100000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.2.2 — Convertible note interest rate extraction** — 6 clauses (values range 0.28-10.0), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 83% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)** — 11 clauses (0 cap / 1 discount / 10 both-mfn), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | cap | discount | both-mfn |
|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **18%** | 98% | 73% | - | 0/1 | 8/10 |
| `deepseek-v4-flash` | hosted | **9%** | 100% | 100% | - | 1/1 | 10/10 |

**Test 1.1.3 — Priced-round price-per-share extraction** — 9 clauses (values range 0.0031-1.5), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **22%** | 95% | 56% |
| `deepseek-v4-flash` | hosted | **22%** | 94% | 67% |

**Test 2.2.3 — Convertible note maturity date extraction** — 4 clauses (values range 2005-03-31-2026-12-31), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 94% | 50% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.2.5 — Convertible note conversion-discount rate extraction** — 4 clauses (values range 5.0-50.0), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 25% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction** — 2 clauses (values range 10000000-40000000), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 6.1 — Equity vesting schedule extraction + normalization** — 9 clauses (values range 1.5yr/no-cliff-4yr/no-cliff), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 25% |
| `deepseek-v4-flash` | hosted | **22%** | 95% | 89% |

**Test 3.1 — Cap-table current ownership percentage (compute)** — 9 clauses (values range 2.4-33.9), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 16% | 0% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 3.2.1 — Named founder's ownership percentage (compute)** — 3 clauses (values range 2.4-8.6), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 18% | 0% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 3.2.2 — Named institutional investor's ownership percentage (compute)** — 4 clauses (values range 5.2-16.3), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 38% | 0% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 3.2.3 — Employee option pool size as % of total shares (compute)** — 1 clauses (values range 9.5-9.5), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 47% | 0% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 7.1 — Securities Act exemption classification** — 10 clauses (6 506(b) / 4 506(c) / 0 504 / 0 Reg A / 0 other), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | 506(b) | 506(c) | 504 | Reg A | other |
|---|---|---|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **40%** | 87% | 90% | 6/6 | 3/4 | - | - | - |
| `deepseek-v4-flash` | hosted | **30%** | 96% | 100% | 6/6 | 4/4 | - | - | - |

**Test 7.2 — Form D field extraction (Total Amount Sold)** — 2 clauses (values range 2,366,532-70,227,931.85), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 90% | 0% |
| `deepseek-v4-flash` | hosted | **50%** | 95% | 100% |

**Test 1.2.1 — Total financing round size extraction** — 10 clauses (values range 3728926-21272455), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 30% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 30% |

**Test 1.4.1 — Annual dividend rate percentage extraction** — 6 clauses (values range 6-10), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 100% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 3.6 — Per-share dilution to new investors (compute)** — 5 clauses (values range 1.96-32.89), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **80%** | 49% | 0% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 3.4 — Fully-diluted vs issued-outstanding basis classification** — 8 clauses (4 Fully-diluted / 4 Issued-outstanding), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Fully-diluted | Issued-outstanding |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 64% | 50% | 4/4 | 0/4 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 4/4 | 4/4 |

**Test 7.5 — Named-period revenue figure extraction** — 5 clauses (values range 12619-9777079), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 86% | 20% |
| `deepseek-v4-flash` | hosted | **20%** | 97% | 100% |

**Test 8.6 — Cross-citation share-count consistency flag** — 5 clauses (values range False-True), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 60% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 6.5 — Post-termination option exercise window extraction** — 5 clauses (values range 180 days-90 days), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **60%** | 87% | 80% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 7.4 — S-1 risk-factor heading extraction** — 5 clauses (values range Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results.-We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively.), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 24% | 0% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 8.5 — Explicit pro-rata waiver vs grant flag** — 4 clauses (values range False-True), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **50%** | 93% | 50% |
| `deepseek-v4-flash` | hosted | **25%** | 96% | 100% |

**Test 7.3 — Primary use of IPO proceeds extraction** — 5 clauses (values range advance our current liver programs-working capital and general corporate purposes), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **80%** | 73% | 20% |
| `deepseek-v4-flash` | hosted | **60%** | 92% | 80% |

**Test 1.2.2 — Named investor's individual dollar allocation extraction** — 5 clauses (values range 46715.64-9418200), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **20%** | 91% | 80% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

**Test 3.3 — Pre-money option pool price-per-share compute** — 3 clauses (values range 0.24-0.909), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 62% | 0% |
| `deepseek-v4-flash` | hosted | **67%** | 91% | 33% |

**Test 4.4 — Convert-vs-take-preference decision (compute)** — 2 clauses (1 Convert / 1 Take preference), each model run 18×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Convert | Take preference |
|---|---|---|---|---|---|---|
| `gemma3:1b` | 1B | **0%** | 100% | 50% | 1/1 | 0/1 |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% | 1/1 | 1/1 |

**Test 4.1 — Per-share value to common after preferred waterfall (compute)** — 4 clauses (values range 0.39-0.51), each model run 19×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 17% | 0% |
| `deepseek-v4-flash` | hosted | **25%** | 99% | 100% |

**Test 4.3 — Named preferred series' total waterfall payout (compute)** — 2 clauses (values range 19.7-58.9), each model run 20×/item:

| Model | Size | **Wobble** ↓ | Consistency | Accuracy |
|---|---|---|---|---|
| `gemma3:1b` | 1B | **100%** | 52% | 50% |
| `deepseek-v4-flash` | hosted | **0%** | 100% | 100% |

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
