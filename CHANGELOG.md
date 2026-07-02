# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
<!-- Group entries under: Added · Changed · Deprecated · Removed · Fixed · Security -->

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
