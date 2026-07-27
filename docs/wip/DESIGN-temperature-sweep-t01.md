> STATUS: WIP · eikiyo · opened 2026-07-27

# DESIGN — temperature 0.1 sweep (paired against 0.7)

## Problem

Probity's published matrix is 11 models x 60 leaves x n=20 at **temperature 0.7**. For the paper we
need a second complete matrix at **temperature 0.1** that can be compared to the first as a paired
difference with **no adjustment**. Uniformity beats cleverness: the run design is deliberately
un-optimised so the only thing separating the two arms is the temperature value.

## Goal / non-goals

- **Goal:** a defensible paired comparison. Every cell measured the same way, both arms.
- **Non-goal:** efficiency. No adaptive sampling, no screening, no early stopping, no
  "skip if no variance". Conditioning n on observed behaviour introduces selection bias and breaks
  the item-count weighting that both aggregate tables rely on.

## Decisions taken (Eikiyo, 2026-07-27)

| # | Decision | Rationale |
|---|---|---|
| 1 | Gemini stays on **OpenRouter** for both arms | Keeps routing identical to the 0.7 baseline. Direct Gemini would confound routing with temperature on that one row |
| 2 | Backfill the 5 guard-truncated 0.7 cells | ~$0.40, append-only, makes the published 0.7 arm a true 660/660 |
| 3 | Local models (`gemma3:1b`, `gemma3:1b-it-qat`) run on **Kaggle T4**, both arms | Standing no-laptop-compute law. Running only 0.1 on Kaggle would confound runtime with temperature |
| 4 | **Plan B**: re-run 0.7 in full, concurrently with 0.1 | The two published arms would otherwise be 25 days apart on preview models behind a rotating gateway. Same-window measurement eliminates provider drift instead of estimating it |
| 5 | Phase 4 OpenRouter-vs-direct control uses **claude-haiku-4.5** | Available on both paths at identical list price; the direct client already exists |

## Arms on disk

Three arms, never overwriting each other:

| Arm | Artifacts | Purpose |
|---|---|---|
| historical 0.7 (2026-07-02/03) | `scored.json`, `runs_<label>.jsonl` | The published baseline. Untouched except the 5 backfilled cells |
| fresh 0.7 (now) | `scored_t07.json`, `runs_t07_<label>.jsonl` | Same-window control arm |
| fresh 0.1 (now) | `scored_t01.json`, `runs_t01_<label>.jsonl` | The new matrix |

The paper's paired table is **fresh 0.7 vs fresh 0.1**. historical-vs-fresh 0.7 is reported
separately as a 25-day drift measurement, which is a finding in its own right.

## Parity contract (the whole point)

Eight axes must be identical between the two published arms. Any change to one is a defect.

| # | Axis | How it is held |
|---|---|---|
| 1 | Model id | Same 11 ids, read from `scored.json[label]["model"]` |
| 2 | Routing layer | Same client class per label, both arms. Pinned by test |
| 3 | Prompts / corpus / oracle | Byte-identical; verified by git (no commit or working-tree change since `4bd8896`) |
| 4 | Scorer / normalizer | Unchanged. Both fresh arms run the same code |
| 5 | n = 20 per item | Enforced by `engine/coverage.py`, fail-closed, both arms |
| 6 | Request payload (`max_tokens`, thinking mode, caching, retries) | Pinned by `tests/test_parity.py`. Meta capture reads the **response** only; the request is byte-identical |
| 7 | Runtime | Local models on Kaggle T4 for both arms |
| 8 | Calendar window | Both fresh arms run in the same window (Plan B) |

## Reuse manifest (§0.8)

| Piece | Verdict |
|---|---|
| Per-call retry / backoff | **REUSED** `models._post_with_retry` |
| Run loop, checkpointing, resume, staleness check | **REUSED** `harness.run_harness` (already takes `temperature` + `checkpoint_file`) |
| Scoring (wobble, accuracy, parse-failure) | **REUSED** `scorer.score_runs` / `score_accuracy`, untouched |
| Leaf fan-out, guard wiring, manifest write | **EXTENDED** `runner.run_leaf` / `run_model` (+`temperature`, +artifact suffix) |
| Whole-model sweep driver | **EXTENDED** `run_hosted_sweep.py` (+`--temperature`) |
| Per-call provider metadata | **NEW** `engine/routing.py`. Searched `models.py`, `harness.py`, `manifest.py`: nothing captures response metadata; `manifest.data_version` hashes run records, not routing |
| Coverage assertion | **NEW** `engine/coverage.py`. Searched `render.py`, `scorer.py`, `scorecard.py`: the only existing count is `valid + parse_failures`, both derived from records that exist, so it cannot see a call that was never made |
| Confidence intervals, paired deltas | **NEW** `results/stats.py`. Searched the repo and `tools/REGISTRY.md`: no stats code, and the repo has zero third-party deps (stdlib only, kept that way) |

## Sad-path table (§0.7, seeded from the guardrail catalog by surface)

| # | Symptom | Cascade if unblocked | Mitigation | Layer |
|---|---|---|---|---|
| 1 | Guard trips mid-leaf on a cost cap | Cell silently truncates; items get <20 runs; **missing items count as "never flipped" so wobble is biased DOWN**; table reads more reliable than reality | Per-leaf caps derived from `items x 20 x per-call cost` instead of a flat $0.20; corrected per-model cost table; `coverage.py` fails closed on any short cell | Verify |
| 2 | A never-made call is invisible to the response-rate column | "333/333 (100%)" on a cell owing 360. Self-referential denominator (the exact PMP `earned === max` failure) | Coverage asserts against `items x 20` read from `oracle.jsonl`, an independently declared source | Verify |
| 3 | Resume trusts a partially-written cell | Re-run silently no-ops; the fix never lands | Cell is complete only when recorded == expected; a partial cell re-runs its missing keys. Checkpoint "done" keys already mean attempted, so failed rows are dropped before a retry pass | Architecture |
| 4 | Provider silently clamps or ignores temp 0.1 | Both arms sample identically; the whole paper measures nothing | Log `temperature_requested` and `temperature_honoured` per call; report honoured as `null` where the provider does not echo it, never as "confirmed" | Verify |
| 5 | OpenRouter routes to a different backend or quantization between arms | Delta attributed to temperature is really a routing artifact | Capture `provider` per call; Phase 4 runs one model both paths; Plan B keeps both arms in one window | Architecture |
| 6 | Mid-run quota wall (402 / `insufficient_quota`) | N-1 spent calls wasted, no clean resume marker | Balance probed before launch; raw 429 body read to distinguish rate-limit from quota; run is resumable per cell | Deploy |
| 7 | Reasoning model returns empty completion (budget exhausted) | Counted as a parse failure, mismeasured as model unreliability | `max_tokens` held at the 0.7 value (16384). Empty completions counted and reported separately in `RUN_LOG.md`, not folded into wobble | Verify |
| 8 | A number in a results table is hand-edited or stale | Paper ships an unregenerable figure | Every table regenerates from disk via the render step; `RUN_LOG.md` records actual spend, retries, wall-clock | Report |
| 9 | Wilson CI applied to a rate near 0 using the normal approximation | Interval crosses zero or is nonsensical; several models sit at 3% | Wilson score interval, never Wald. Paired deltas use Newcombe's method for correlated proportions | Report |
| 10 | CIs overlap but the table implies a ranking | Reader infers an ordering the data does not support | Explicit "statistically indistinguishable" grouping in the output; no rank column where intervals overlap | Report |

## Statistics

- **Wobble** is a per-item binary (did this item's answer flip across its runs). Aggregated across
  leaves it is a plain binomial proportion over the item count, so **Wilson score intervals** apply
  directly at model and category level.
- **Paired 0.7 vs 0.1** shares the same items, so the arms are correlated. The delta interval uses
  **Newcombe's score-based method for paired proportions** (MOVER-R), stdlib-implementable, rather
  than treating the arms as independent.
- **Indistinguishable grouping:** models whose intervals overlap are reported as one band with no
  implied ordering.

## Definition of done

- [ ] 660 cells complete at 0.1, asserted against `items x 20`, no holes averaged over
- [ ] 660 cells complete at fresh 0.7, same assertion
- [ ] 5 historical 0.7 cells backfilled; historical arm reaches 660/660
- [ ] `results/RESULTS_T01.md` full per-leaf breakdown
- [ ] Paired table with CIs on every delta
- [ ] Appendix: requested vs honoured temperature + routing layer, per model
- [ ] OpenRouter vs direct control with CI on the delta
- [ ] Coverage matrix printed and asserted full
- [ ] `RUN_LOG.md`: calls, failures, retries, actual USD, wall-clock
- [ ] Every number regenerable by re-running the render step; zero hand-edited values
- [ ] Tests green before and after; no new third-party dependency
