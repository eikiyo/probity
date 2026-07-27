# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
<!-- Group entries under: Added · Changed · Deprecated · Removed · Fixed · Security -->

## [1.3.0] - 2026-07-27

### Added
- **Temperature 0.1 arm.** Every model in the lineup is now measured at BOTH 0.7 and 0.1 over the
  identical tests, items, prompts and scorer, so the two arms compare as a paired difference with
  temperature as the only variable. 12 models x 60 leaves x 20 runs = 112,800 calls per arm.
- **Parse-failure table** in the paired report -- unparseable-run counts, tests dropped, and the
  item count each arm's wobble is actually computed over, with a ⚠️ on any model whose two arms
  are NOT scored over the same number of items. Wobble is a rate, and the scorer drops a test for
  a model when >30% of its runs are unparseable, so a model that stops answering its hardest tests
  looks *more* consistent while having answered less. deepseek-v4-flash is the live case: 0% parse
  failures on seven leaves at 0.7, 30-75% at 0.1, those leaves dropped, 470 items scored at 0.7
  against 426 at 0.1. The PAIRED table is unaffected (common item set); the suite tables are not,
  and now say so.
- **Paired comparison report** (`results/PAIRED_legacy_vs_t01.md`) -- per-model wobble delta with
  Tango (1998) score intervals for paired proportions, plus a Verdict column that says "no
  difference established" rather than leaving a reader to infer direction from a sign.
- `deepseek-v4-pro` added to the lineup at both temperatures (thinking disabled), taking the
  published table from 11 models to 12.
- **Kaggle track** (`kaggle-arm/`) -- runs the two local models on a T4 at both temperatures in one
  session, so their 0.7 baseline is machine-matched to their 0.1 arm rather than compared across
  hardware. Cross-machine control: gemma3:1b-it-qat reproduced the Mac-measured 0.7 wobble to
  within 0.14 points.
- **Peer-review data dump** (`results/datadump.py`) -- 244,400 run records across three arms with a
  STANDALONE `verify_dump.py` that reimplements wobble and accuracy importing nothing from this
  repo, and reproduces every published number from the raw records.
- **Browsable per-item corpus** (`results/raw_tree.py`) -- 12,220 files laid out
  `<model>/<temperature>/<test>/item-NNN.json`, each carrying the exact prompt sent, the expected
  answer with its supporting quote, all 20 answers received, and a summary.
- `engine/backfill.py` -- fills coverage holes without re-billing complete cells.
- `engine/run_arm.py` -- sequential arm driver, cheapest model first, with a fail-closed balance
  gate calibrated from measured spend rather than list price.

### Changed
- `make render` now regenerates EVERY published surface (both arms' tables, the paired report, and
  both README blocks), and a test asserts that regenerating changes nothing -- a published number
  that no longer matches the data now fails the suite.
- README states the benchmark runs at two temperatures, names the 60-of-67 built/backlog split
  explicitly, and carries a GENERATED temperature-comparison block (no hand-typed figures).

### Fixed
- **Cost estimates ignored reasoning tokens**, which bill as output but never appear in the
  completion. gpt-5-mini cost 2.35x its list estimate. The balance gate now calibrates per-label
  from measured ledger rows.
- **`compare.py --arms` took floats**, so `--arms 0.7 0.1` selected the t07 namespace (two local
  models only) and would have produced a 2-model report that looked finished. `legacy` is now an
  accepted arm value.
- **`compare.py` and `render.py` both defaulted to `results/RESULTS_T01.md`** for two different
  documents; whichever ran second silently replaced the other.
- **The paired report rendered a model that was still being measured** -- 336 item-pairs beside
  models with 470, formatted identically. A model must now be complete in BOTH arms to be paired,
  and any exclusion is named rather than dropped.
- **The dump verifier disagreed with the paper** because it did not know the benchmark drops a leaf
  for a model when >30% of that leaf's runs are unparseable. It now applies the rule AND prints
  every excluded cell, so a reviewer judges the choice instead of inheriting it invisibly.
- **`scored_*.json` is shared across model labels**, so extracting a remote archive over it would
  have deleted the hosted arm's scoring for all 60 leaves. Shared files are now MERGED by label.
- Internal `None` arm sentinel leaked into report headings ("paired against None").
- Badge colour could contradict its own printed label (84.97% and 85.02% both print "85%").

## [1.2.0] - 2026-07-02

### Added
- Brake-pedal runtime guard (`engine/guard.py`) -- caps a run's model-call steps and estimated
  spend, tripping BEFORE the call that would breach the cap (fail closed). Wired into the actual
  `harness.run_harness()` call-site, not just a config value. Exposed as `probity-bench run <leaf>
  --max-steps N --max-cost X`.
- Scorecard report (`results/scorecard.py`, terminal + HTML) -- refuses to render a green
  headline on 0 scored tasks, and always shows scored/errored/total explicitly rather than
  silently narrowing the denominator. Auto-written as `scorecard.html` next to each leaf's
  `scored.json`.
- Reproducibility manifest (`engine/manifest.py`) -- `manifest_<model>.json` per run, content-hash
  keyed to the exact recorded run data so a re-score from the same data is provably identical.
- A container image, published to `ghcr.io/eikiyo/probity` on every GitHub release
  (`.github/workflows/docker-publish.yml`) -- `docker run ghcr.io/eikiyo/probity --help`.

## [1.1.0] - 2026-07-02

### Added
- `pip install probity-bench` — a real distributable package (`probity_cli/`) shipping the full
  pipeline (`engine/`, all 60 leaves' code + oracles + prior results, `demo/`) minus the raw SEC
  corpus documents and, obviously, no model weights.
- `probity-bench onboard` — an interactive setup wizard (documents to fetch, models to benchmark,
  API key collection) modeled on the OpenClaw/Claude-CLI onboarding pattern: step-by-step prompts,
  local Ollama auto-detection, a secret-ref mode (store an env var *name* instead of the raw key),
  and a live verification call before trusting any stored key — fails closed with an actionable
  message rather than silently accepting an invalid one.
- `probity-bench demo` / `results` / `list` / `run <leaf>` — zero-to-low-config commands; `demo`
  needs no install-time setup at all (replays real recorded model runs, pure stdlib).
- Config + secrets live at `~/.probity/` (`config.json` + `.env`, chmod 600) — never inside the
  repo, never committed, mirroring the existing `secrets/.env` convention.
- README hero GIFs (`demo/demo.gif`, `demo/onboard.gif`), recorded with VHS from real runs.

## [1.0.0] - 2026-07-02

### Added
- Initial public release: 60 real, SEC-EDGAR-sourced benchmark leaves across 8 fundraising-document
  families (SAFEs, priced rounds, liquidation preferences, vesting, SAFEs, regulatory disclosures,
  and more), each with a hand-validated oracle and a shared, field-agnostic evaluation engine
  (`engine/harness.py`, `engine/scorer.py`, `engine/runner.py`).
- **Wobble** (run-to-run consistency, N=20 @ temp 0.7) reported as the headline metric alongside
  (never averaged with) accuracy against the human-validated oracle.
- A full adversarial self-audit of all 60 leaves (`docs/AUDIT_TODO.md`) — every leaf independently
  re-verified against its real source document; 9 code bugs and 9 data-quality findings fixed with
  before/after reruns recorded.
- Repro pipeline: `python3 source.py` (fetch real documents) → `python3 run.py` (run the model
  ladder) → `python3 results/render.py` (regenerate the results tables) per leaf.

[Unreleased]: https://github.com/eikiyo/probity/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/eikiyo/probity/releases/tag/v1.1.0
[1.0.0]: https://github.com/eikiyo/probity/releases/tag/v1.0.0
