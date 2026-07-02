# Probity — Adversarial Audit Todo (all 60 built leaves)

Started 2026-07-02 per Eikiyo's directive: read every leaf individually, hunt for gaps/bugs/
breaking-points/stubs/hardcodes/half-done features, log findings here, fix what's safe to fix
immediately, flag judgment calls for explicit confirmation. Order = engine/registry.json ref
order (1.1.1 -> 8.6). Status counter recounted on every edit.

**Counter: 3/60 done · 1 in-progress · 56 pending · 0 partial** — dated 2026-07-02.

## Legend
- `[x]` audited + resolved (bugs fixed, or verified clean)
- `[~]` audited, one finding still pending Eikiyo's confirmation (not a code bug — a judgment call)
- `[ ]` not yet audited

## Findings log

### [x] 1.1.1 post_money_valuation
- **CRITICAL bug found + FIXED (project-wide):** `engine/harness.py` checkpoint-resume logic
  keyed purely on positional `instance_idx`, with no way to detect `oracle.jsonl` being edited
  after a checkpoint was written. Proved real via cross-model exact-value-match signature (both
  gemma3:1b and deepseek-v4f scored the same wrong answer, which exactly matched a *neighboring*
  item's truth). Root-caused: this leaf's oracle shrank 6->4 items, stale checkpoint never
  cleared. Fixed `_validate_checkpoint_freshness()` (fail-closed, raises `StaleCheckpointError`
  on any position-range or item-id mismatch) — commit `ba322a7`. Repo-wide sweep found 2 more
  affected leaves (`flag_full_ratchet`, `securities_exemption`) — see their entries below.
  Reran clean (Eikiyo authorized delete+rerun) — commit `cd270fa`. Now: deepseek-v4f 0%
  wobble/100% acc (was falsely 50%); gemma3:1b 0% wobble/25% acc with a genuine, internally
  consistent ~10x magnitude extraction error (real model behavior, not a data bug).
- **Minor:** 2 orphaned `corpus/questions/*.txt` files not referenced by any oracle item — both
  verified as CORRECTLY excluded (one duplicate filing, one genuine multi-value ambiguity). Not
  a bug, just noted; could tidy into a `rejected/` subfolder later (not done, low priority).

### [x] 1.3.2 participation_type
- **Verified clean:** class balance correct (8/5/5), zero answer leakage across 18 items,
  IESI Corp (hard/participating) spot-checked clean against real filing text.
- **[~] DISPUTED LABEL, still pending Eikiyo's confirmation:** Pfenex Inc. item (oracle's own
  flagged hardest/"TRAP" item) labeled `non-participating`. Full re-derivation using real dollar
  figures ($1.00/share Original Issue Price, 8% simple annual dividend, $2.50/share "Maximum
  Participation Amount" threshold) shows the greater-of override needs ~18.75 years of accrued
  dividends to trigger — meaning in nearly every realistic exit this instrument functions as
  ordinary uncapped PARTICIPATING preferred, not non-participating. Counter-analysis appended to
  the oracle entry's own `note` field (label itself left unchanged) — commit `5d6a76b`.
  **ACTION NEEDED FROM EIKIYO:** flip to `participating`, keep as `non-participating`, or
  exclude the item as too ambiguous?
- Flagged (not fixed): this leaf's `run.py` predates `engine/runner.py` and duplicates ~90 lines
  of now-centralized logic (§0.8 rule-of-two violation) — worth a dedicated migration pass
  across all Round-1-era leaves, not a one-off fix. `source_more.py` was missing the mandatory
  file header — fixed.

### [x] 4.1 liquidation_waterfall_payout
- **CRITICAL bug found + FIXED (project-wide):** `results/render.py` never surfaced
  `parse_failure_rate` anywhere in the public README/RESULTS.md — DeepSeek's real 22.5%
  non-response rate (18/80 runs, 94% of which were raw HTTP 503s from the API, not model
  failures) was completely hidden behind a headline "100% accuracy, 99% consistency" figure.
  Added a "Response rate" column + explanation to both RESULTS.md and README tables — commit
  `b55cd7a`.
- **CRITICAL bug found + FIXED (project-wide root cause):** `engine/models.py`'s
  `DeepSeekClient.generate()` had zero retry logic on transient HTTP errors. Added a 3-attempt
  exponential-backoff retry (5xx/429/network errors only, never 4xx) — commit `b55cd7a`. Added
  4 new unit tests covering the retry decision logic.
- **Verified clean:** all 4 EV/per-share figures cross-checked byte-for-byte against the real
  SC 13E-3 filing text, no answer leakage, item counts consistent (no stale oracle edit), no
  stubs/TODOs.
- **Minor, documented not fixed:** `validating_quote` uses a hand-written "..." ellipsis instead
  of a literal substring (unlike leaves built via `corpus_utils.window_on()`). Real source
  document never says "Connecture" (uses deal codename "Cure") — verified correct via SEC EDGAR
  CIK 1211759, documented in source.py so a future reader doesn't mistake it for an error.

### [~] 1.1.2 pre_vs_post_money
- **Verified clean:** gemma3:1b's 71% accuracy coincidentally equals the majority-class baseline
  (15/21 pre-money) but per-class breakdown proves it's NOT class-collapse (9/15 pre-money, 6/6
  post-money correct — genuine mixed performance). Explicit "pre-money"/"post-money" wording in
  11/21 corpus windows is legitimate real-document signal for this extraction task, not leakage
  (unlike an enum leaf where the class NAME itself appearing would be leakage).
- **[~] DUPLICATE-FILING FINDING, PENDING EIKIYO'S CONFIRMATION (data NOT touched):** 2 of the
  21 items are the same underlying Cytosorbents Corp convertible-note transaction, each counted
  twice — once via the 8-K body (`..._v195191_8k` / `..._v212119_8k`) and once via its own
  Exhibit 10.1 (`..._v195191_ex10-1` / `..._v212119_ex10-1`), same accession number each pair,
  near-identical boilerplate text ("$750,000... pre-money basis at or below $35 million...").
  This inflates N from a true 19 unique transactions to 21, and double-counts whatever the model
  gets right/wrong on those 2 real facts. Confirmed NOT a pattern for the other same-company
  pairs (Hague Corp, Oculus Innovative Sciences) — those have different accession numbers/years,
  genuinely independent transactions. **ACTION NEEDED FROM EIKIYO:** drop the 2 `_8k` duplicate
  entries (keeping the more complete `_ex10-1` full-text versions) and rerun this leaf at 19
  items, or leave as-is?

### [~] 1.1.3 price_per_share — SEVERE FINDING, PENDING EIKIYO'S CONFIRMATION
- This leaf has documented history (STATE.md batch 3: "9 of 11 items had a company name entirely
  disconnected from the real filer... labeled as famous companies" — independently audited and
  supposedly fixed before commit, dropped to 9 clean items). Current state DOES have correct
  `company` field values, but the item IDs/filenames still carry the OLD misleading famous-name
  artifacts as a residue (`energy_recovery`, `equifax_series_b`, `interdigital_offering`,
  `washington_group` are filenames, not the real company) — cosmetic confusion, not a functional
  bug (the `company` FIELD used at runtime is correct), but worth a rename for clarity.
- **NEW, MORE SEVERE FINDING (not previously caught): 5 of 9 items (56%) are WRONG INSTRUMENT
  TYPE.** task.py explicitly requires "the PRICE PER SHARE of the preferred stock in the
  financing round." Verified via direct grep: `abwn_offering`, `auraind_warrant`,
  `energy_recovery`, `equifax_series_b`, `interdigital_offering` contain **zero** mentions of
  "preferred" anywhere in their model-facing windows — they are penny-stock COMMON STOCK private
  placements and warrant exercises (Reg D Rule 506 offerings), not preferred-stock financing
  rounds. `equifax_series_b`'s window alone contains 4+ DIFFERENT prices for different security
  types ($0.10/unit, $0.05/share, $0.20/unit, $0.085/share) with no "preferred" stock in sight,
  despite the id implying a "Series B" preferred round. Only 4/9 items (`gelesis_certificate`,
  `landing_page_series`, `mobile_systems_s1`, `washington_group`) verified genuinely clean —
  real Series A/B/F preferred stock rounds with an unambiguous stated price.
  **This likely explains the leaf's mediocre accuracy (56-67%, both models)** — the model is
  being asked a preferred-stock question about documents with no preferred stock in them, an
  ill-posed task for those 5 items, not a genuine model reasoning failure.
  **ACTION NEEDED FROM EIKIYO:** (a) drop the 5 wrong-instrument items and re-source real
  preferred-stock rounds to replace them (leaf shrinks to 4 items immediately, needs new
  sourcing to reach a reasonable N again), OR (b) reframe the task/taxonomy to "price per share
  in an equity financing round" (dropping the preferred-stock specificity) if testing common-
  stock private placements is intentionally in scope, OR (c) leave as-is. Oracle.jsonl NOT
  touched pending this decision.

## Next leaf: 1.2.1 round_size
