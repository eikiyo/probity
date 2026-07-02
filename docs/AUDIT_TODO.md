# Probity — Adversarial Audit Todo (all 60 built leaves)

Started 2026-07-02 per Eikiyo's directive: read every leaf individually, hunt for gaps/bugs/
breaking-points/stubs/hardcodes/half-done features, log findings here, fix what's safe to fix
immediately, flag judgment calls for explicit confirmation. Order = engine/registry.json ref
order (1.1.1 -> 8.6). Status counter recounted on every edit.

**Counter: 36/60 done · 0 in-progress · 24 pending · 6 partial** — dated 2026-07-02. Families 1, 2.1, 2.2, 3 (all of 1.1.1-1.7, 2.1.1-2.1.6, 2.2.1-2.2.6, 3.1-3.6) complete.

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

### [x] 1.2.2 per_investor_allocation
- **Verified clean.** N=5 (small, noted not fixed). deepseek-v4f 100%/0%. gemma3-1b 80%/56%
  wobble — its one miss (CAS Medical) extracted a SHARE COUNT (94,182) instead of the dollar
  amount, a genuine shares-vs-dollars confusion, not an oracle bug. Verified all 4 non-QuantRx
  items are primary purchases "from the Issuer" (Roka BioScience, CAS Medical, Navidea) or
  equivalent. **Minor, documented not fixed:** the QuantRx item (Mark Capital, $46,715.64) is a
  SECONDARY purchase of already-issued shares from Goldman Sachs, not a primary financing-round
  investment from the company — a different economic transaction type than the other 4 items,
  though task.py's own framing ("distinct from the round total") is loose enough that this
  still technically fits; both models extracted it correctly regardless (secondary-vs-primary
  didn't cause any measured harm). Also: the oracle's `validating_quote` field truncates before
  reaching the actual dollar figure for this item, but confirmed the full corpus window
  (`corpus/questions/quantrx.txt`) does contain "$46,715.64" — a cosmetic quote-field gap, not
  a missing-window bug like 2.2.4's.

### [x] 1.2.1 round_size
- **CRITICAL bug found + FIXED:** identical failure family to 1.2.1's sibling leaves — both
  models scored an identical 30% accuracy / 0% wobble. Root cause: every one of the 10 Form D
  corpus windows carries BOTH `<totalOfferingAmount>` (issuer's target/ceiling) and
  `<totalAmountSold>` (what actually closed) as adjacent XML fields; oracle consistently uses
  `totalAmountSold`, but the original prompt ("the total dollar amount raised") never
  disambiguated between them, and both models' wrong answers matched `totalOfferingAmount`
  exactly on every miss. Fixed `task.py`'s system prompt to explicitly name the correct field
  and instruct the model to use the amount SOLD when the two differ — commit pending.
  Archived stale pre-fix runs to `_archive_stale_prompt/`, reran clean: **deepseek-v4f now
  100% accuracy / 0% wobble** (was 30%/0%, task-design artifact fully resolved). gemma3-1b
  stayed at 30% accuracy / 50% wobble even with the explicit fix — verified this is now a
  genuine model-capability limitation, not task ambiguity: gemma3-1b's wrong majority answers
  on every failing item still exactly equal `totalOfferingAmount` even after being told not to
  use it, proving the 1B local model simply cannot reliably follow the disambiguation
  instruction. This is the correct, honest outcome — the task is now well-specified and the
  score gap reflects real model capability, not a shared trap.
- **Minor, not fixed:** leaf is absent from `results/RESULTS.md`/README (the `LEAVES` list in
  `results/render.py` is a hand-curated subset, not auto-populated from every leaf with a
  `scored.json`) — a pre-existing publishing gap, not caused by this leaf's fix. Flagging once
  here rather than repeating per-leaf; worth a dedicated pass to decide which of the 60 built
  leaves should be in the public tables.

### [~] 1.3.1 liquidation_preference_multiple — PENDING EIKIYO'S CONFIRMATION
- **DUPLICATE-FILING FINDING (data NOT touched):** 3 of 13 items are exact duplicates counted
  as independent data points. Verified via byte-for-byte diff of `corpus/full/*.txt`:
  `1283259_000149315225016953` / `_027406` (BioVentrix) are the IDENTICAL "First Amendment to
  the Third Amended and Restated Certificate of Incorporation" exhibit text, filed under two
  different accession numbers (same amendment attached to two different periodic filings).
  Same pattern confirmed for `1883085_...24000060` / `_25000050` / `_26000018` (Pagaya, 3x) and
  `1447362_...19009024` / `_19012901` (Castle Biosciences, 2x) via identical `validating_quote`
  strings. True unique-clause count is 10, not 13 — inflates N and double/triple-weights
  whatever each model gets right/wrong on 3 real clauses. **ACTION NEEDED FROM EIKIYO:** drop
  the 3 later-accession duplicates (keep one representative filing per unique clause) and
  rerun at N=10, or leave as-is?
- **Minor, documented not fixed:** none of the 13 oracle items has a `source_url` field
  (unlike every other audited leaf) — verification required reconstructing EDGAR paths from
  the `CIK_ACCESSION`-format `id` and reading `corpus/full/*.txt` directly. Worth adding
  `source_url` for consistency/reproducibility in a later pass; not blocking since the raw
  fetched text is present and verifiable.
- **Minor, cross-leaf naming collision (not a bug, just a trap for future readers):** this
  leaf's enum includes a value literally spelled `"non-participating"` meaning "the clause
  states there is NO liquidation preference at all" — a totally different concept from leaf
  1.3.2 (`participation_type`)'s `"non-participating"`, which means "gets preference OR
  conversion, whichever is greater, but never both." Zero items in this leaf's 13-item corpus
  actually use this value (real class distribution is 4×1x / 5×2x / 4×3x, `"other"` and
  `"non-participating"` both empty), so it hasn't caused a real scoring issue, but a future
  reader cross-referencing both leaves by value name alone would be misled.
- Verified clean otherwise: all 10 unique clauses' multiples spot-checked against real
  `corpus/full/*.txt` filing text, correctly classified.

### [x] 1.3.3 participation_cap
- **Verified clean, both models 100% accuracy / 0% wobble.** All 3 items' cap multiples
  spot-checked against real `corpus/questions/*.txt` text (Jazz Semiconductor's 3.5x confirmed
  verbatim: "received 3.5 times ($3.50) the aggregate face value").
- **Minor, documented not fixed: N=3 is the smallest sample size found so far in this audit**,
  and 2 of the 3 items share the exact same true value (3) that also appears as a worked
  example in the prompt's instruction block ("if the clause says 'up to three (3) times...'
  respond {"participation_cap": 3}"). This did NOT produce a detectable anchor-bias artifact —
  both models also correctly extracted the one differing item (3.5, not the example's 3) — but
  the sample is too small to be confident the task generalizes, and a future re-sourcing pass
  should either grow N or swap the example to a value that doesn't match any real item.

### [x] 1.3.4 preference_seniority
- **Verified clean.** Class balance 6 pari-passu / 5 stacked. Non-trivial, plausible spread
  (gemma3-1b 45% acc/45% wobble, deepseek-v4f 82% acc/0% wobble) — no shared-confusion signal
  like the round_size/post_money_valuation bugs. Spot-checked the one item whose validating
  quote looked ambiguous at a glance (E Centives — mentions "dividends" right next to the
  seniority language): confirmed via full corpus window the real charter clause explicitly
  covers BOTH "dividend rights and rights on liquidation, winding-up and dissolution" in one
  combined seniority statement, so "stacked" is correctly derived from real liquidation-scope
  text, not a dividend/liquidation clause-type mixup.

### [x] 1.4.1 dividend_rate_pct
- **Verified clean.** N=6, both models 100% accuracy / 0% wobble. Checked every corpus window
  for multi-value ambiguity (a second % figure, e.g. a default/step-up rate) that could produce
  a false-easy task — confirmed each of the 6 windows contains exactly ONE percentage figure,
  so the 100% scores reflect a genuinely unambiguous extraction, not an artifact. Sourcing
  documented as reusing already-fetched charters from the sibling `dividend_cumulative` leaf;
  no duplicate companies within this leaf itself.

### [x] 1.4.2 dividend_cumulative
- **Verified clean.** N=16, perfect 8/8 class balance. gemma3-1b 87.5% acc, deepseek-v4f 100%.
  Spot-checked the two Jazz Semiconductor/Jazz Technologies items whose truncated
  `validating_quote` looked like it might be a non-cumulative tell ("payable if and when
  declared") mislabeled cumulative — full quote confirms real charter text explicitly says
  "...payable if and when declared by the Board of Directors ... and are cumulative", a
  genuine, correctly-labeled edge case (declaration-timing-contingent but still cumulative in
  amount) that both models handled correctly, a legitimately good trap item. Verified
  gemma3-1b's 2 actual misses (BioAccelerate, Eiger BioPharmaceuticals) against real source
  text — both oracle labels are unambiguous and correct; genuine model reasoning failures, not
  data bugs.

### [~] 1.5.1 antidilution_type — PENDING EIKIYO'S CONFIRMATION
- **OFF-THESIS DOCUMENT FINDING (data NOT touched):** 1 of 5 items (`763901_...`, labeled
  `"none"`) is **Popular, Inc.** (BPOP) — a large public Puerto Rico bank holding company,
  verified via the real corpus text ("the Bank", TARP-era "April 2010 offering" of depository
  shares) — not a VC/startup preferred-stock financing charter at all, but a bank-regulatory
  rights/warrant anti-dilution clause. This is the SAME contamination class the sibling
  `dividend_rate_pct` leaf's `source.py` explicitly documents removing ("NOT bank-regulatory
  perpetual preferred, which was this leaf's original off-thesis contamination") — but it went
  unnoticed here. The `"none"` label is textually accurate (the clause does say "There will be
  no anti-dilution adjustment..."), so this is NOT a mislabeling bug, but it is off-thesis for
  a benchmark whose stated purpose is VC financing documents. Notably this is also the one
  item gemma3-1b got wrong (guessed `full-ratchet`, 100% consistent) — the document's unusual
  dual-instrument structure (adjusts a separate "Right"/warrant's exercise price via
  full-ratchet-like mechanics while denying anti-dilution for the preferred conversion itself)
  is genuinely confusing text, compounding the thesis-purity concern with a possible difficulty
  distortion. **ACTION NEEDED FROM EIKIYO:** drop this item and re-source a genuine VC-preferred
  "none" example (N drops to 4 immediately), or leave as-is since the label itself is correct?
- **Minor, recurring pattern:** same as 1.3.1 — 2 of the 5 enum classes (`broad-based`,
  `narrow-based`) are unused in this corpus (real distribution: 2 weighted-average / 2
  full-ratchet / 1 none). N=5 is also on the small side. Not fixed, just noted.

### [x] 1.5.2 antidilution_base
- **Verified clean.** N=10, good class balance (4 narrow / 3 broad / 3 n/a). gemma3-1b 70%
  acc/40% wobble, deepseek-v4f 100%/0% — plausible spread, no shared-confusion signal.
  **Shares the same Popular Inc (`763901_...`) off-thesis item already flagged under 1.5.1**
  (same corpus reused across sibling anti-dilution leaves) — not logging as a new separate
  finding, covered by that entry's pending decision. All other 9 items' base classifications
  spot-checked against their `validating_quote`, all textually correct.

### [x] 1.6.1 conversion_ratio
- **Verified clean.** N=5. gemma3-1b 80% acc/20% wobble, deepseek-v4f 100% acc/20% wobble.
  Double-checked the one outlier-looking value (Boston Life Sciences, 8000:1 — unusually high
  vs. the other items' 1x/2x/100x/4.57x) against full corpus text: confirmed a genuine
  PER-SHARE ratio ("Each share of Series E preferred stock is convertible into 8,000 shares"),
  and the math is internally consistent ($10,000 purchase price / $1.25 conversion price =
  8,000 exactly) — not a lot-size/per-share confusion. ids encode the expected ratio in the
  filename (e.g. `boston_life_sciences_8000to1`) but confirmed `build_prompt()` only passes
  `instance["document"]` to the model, never the id — no leakage path.

### [x] 1.6.2 auto_conversion_trigger
- **Bug found + FIXED (low-severity, no rerun needed):** task.py's prompt told the model to
  extract "only the AGGREGATE GROSS PROCEEDS dollar amount," but 3 of 5 real charter clauses
  actually state the QPO threshold as NET proceeds ("net of underwriting discounts and
  commissions") — only 2/5 (Silicon Energy, TerraScend) genuinely say "gross." This did NOT
  cause any measured harm (both models scored 100% on every item including the net-proceeds
  ones, because each document states only ONE candidate dollar figure — no second gross-vs-net
  number to confuse it with, unlike round_size's real two-field trap). Fixed the prompt to say
  "gross or net, whichever the charter itself uses" for correctness/future-proofing. Did NOT
  rerun — existing runs are still valid (the old prompt was never actually exercised wrong),
  and spending API calls to "reprove" an already-100%/100% leaf isn't warranted.
  Commit pending.

### [x] 1.7 redemption_rights
- **Verified clean.** N=10, perfect 5/5 class balance. deepseek-v4f 100% acc/10% wobble.
  gemma3-1b exactly 50% acc — investigated because 50% on a balanced binary task risks being
  chance-level or class-collapse. Confirmed **complete class collapse**: gemma3-1b answered
  "no" on literally all 10 items (got every true-"no" right by luck of the label, missed every
  true-"yes"). Spot-checked 1 of the 5 missed "yes" items (Tenable Holdings) against the real
  quote — unambiguous "the Company shall redeem, out of surplus, all of the shares..." — a
  genuine, clear-cut mandatory-redemption clause. This is a real model behavior pattern (1B
  local model systematically biased toward "no"/non-redeemable), not an oracle bug.

### [x] 2.1.1 safe_valuation_cap
- **Verified clean, no rerun needed.** N=8, deepseek-v4f 100%/0%, gemma3-1b 87.5%/37.5% wobble
  (plausible, no shared-confusion signature). Initially looked suspicious like the round_size
  bug: the corpus genuinely MIXES pre-money-cap SAFEs (4/8) and post-money-cap SAFEs (4/8) —
  but confirmed this is NOT a within-document ambiguity (each SAFE states exactly one "___-Money
  Valuation Cap is $X" figure, so there's never a second candidate number in the same document
  to confuse the model with), and task.py's docstring never falsely claims uniformity. Reads as
  a deliberate design choice (real-world extraction robustness across both YC SAFE template
  variants) rather than a bug. Worth flagging for any DOWNSTREAM consumer though: the 8 raw cap
  values are NOT directly comparable to each other (a $100M post-money cap and a $100M pre-money
  cap represent different actual valuations) — that distinction is leaf 2.1.4's job
  (`safe_pre_vs_post_money`), not this leaf's, so no action needed here.
- Also verified the unusually-high "80% Discount Rate" figures (Maison Luxe, TaoWeave) are real,
  correct YC SAFE template language — some templates define "Discount Rate" as the price-you-pay
  percentage (80% = 20% discount), confirmed via the document's own parenthetical ("representing
  a 20% discount"). Not the field under test in this leaf, but worth noting so a future reader
  doesn't mistake it for a data error.

### [x] 2.1.2 safe_discount_rate
- **Verified clean.** N=9, deepseek-v4f 100%/0%. gemma3-1b 56% acc — a genuine computation task
  (must derive `100 - stated%` when the template phrases "Discount Rate" as the price-paid %,
  vs. take the number as-is when phrased as "100 minus X%" or a plain "fifty percent"), harder
  for a 1B model by design, not a bug.
- **Minor, documented not fixed:** the `sos_50` item (SOS Hydration) contains a genuine
  MULTI-VALUE clause: "Discount Rate is 100 minus 50%, provided that, if prior to July 1, 2021
  the Company raises at least $1,000,000... Discount Rate shall be 100 minus 25%" — i.e. TWO
  different discount rates (50% base / 75% early-financing-incentive) depending on an unresolved
  timing condition the excerpt itself doesn't confirm was met. Oracle uses the base rate (50),
  which matches task.py's OWN worked example verbatim ("If it states 'Discount Rate is 100
  minus 50%', respond with 50") — this is a deliberate, documented convention (default-to-base-
  rate), not an overlooked ambiguity, and empirically doesn't correlate with the one model miss
  on this item (gemma3-1b guessed 20, which isn't even the alternate 75% reading).

### [~] 2.1.3 safe_cap_vs_discount_applies — SEVERE CLASS-IMBALANCE FINDING, PENDING EIKIYO
- **SEVERE, data NOT touched:** class distribution is 10 `both-mfn` / 1 `discount` / **0 `cap`**
  out of 11 items. The `"cap"`-only class (a SAFE with a valuation cap and explicitly NO
  discount rate) is entirely unrepresented — this leaf can never test whether a model can
  correctly identify a cap-only SAFE, one of its own 3 defined taxonomy classes. A trivial
  "always answer both-mfn" strategy would score 90.9% with zero real classification ability —
  currently NOT being exploited (gemma3-1b actually scores 73%, worse than that trivial
  baseline, and deepseek 100% genuinely discriminates), but it's a live gaming risk for any
  future model evaluated against this leaf, and the benchmark can't currently claim to test
  "cap" recognition at all. **ACTION NEEDED FROM EIKIYO:** re-source 2-3 genuine cap-only SAFE
  items (pre-2018 YC SAFE format, before the 2018 post-money-with-MFN standard existed, is the
  most likely place to find them) to make this leaf's 3-way classification meaningful, or accept
  it as effectively a 2-way (`both-mfn` vs `discount`) task and document that explicitly?
- **Minor, not fixed:** `taoweave_both_mfn`'s `id`/filename says "taoweave" but its real content
  (confirmed via corpus text: "UK Corporation Tax Act 2010") is a UK-incorporated SAFE — the
  `company` field correctly says "Manako Labs Ltd" (also UK, consistent), so this is the SAME
  cosmetic filename-vs-real-content mismatch pattern already documented for 1.1.3, not a fresh
  functional bug (the field used at runtime is correct).

### [x] 2.1.4 safe_pre_vs_post_money (leaf dir: `safe_pre_post`)
- **Bug found + FIXED (repo-wide sweep, cheap+safe):** wrote a one-off script to check every
  built leaf's `engine/registry.json` `field` name against its real `task.py` `TASK["fields"]`
  key — confirmed `registry.json` is pure documentation (grepped: **zero** Python code anywhere
  in the repo actually reads it), so any mismatch is a doc-accuracy issue, not a functional bug.
  Found exactly 2 mismatches across all 60 built leaves: this leaf (registry said
  `safe_pre_vs_post_money`, real key is `safe_cap_type`) and leaf 7.2 `form_d_fields` (real key
  `form_d_field_value`, not yet audited on its own merits). Fixed both registry.json entries.
- **Verified clean otherwise.** N=16, class balance 10 post-money / 6 pre-money. Runs 4 models
  (gemma3-1b/llama3.2-3b/gemma4-12b/deepseek-v4f) instead of the current project-wide 2-model
  FAST_SET — this is a Round-1-era leaf whose own `run.py` predates `engine/runner.py` and
  duplicates its own ~80-line run loop (same §0.8 rule-of-two legacy-duplication pattern already
  flagged for 1.3.2's `participation_type`; not re-logging as a separate finding, just noting it
  recurs here). Spot-checked 2 items' real EDGAR text against their labels — clean.

### [x] 2.1.5 safe_mfn_present
- **Verified clean.** N=7, class balance 4 yes / 3 no, both models 100% accuracy (gemma3-1b
  28.6% wobble, deepseek 0%). Two "yes" items (Millennium Blockchain, Inc. / THC Therapeutics,
  Inc.) share both an identical MFN boilerplate `validating_quote` AND a filename prefix
  ("mblc") — checked this isn't a hidden duplicate: different accession suffixes (`-004207` vs
  `-004955`), i.e. two genuinely different SAFE instruments, most likely from the same company
  under an earlier/later name (Millennium Blockchain appears to have later operated as THC
  Therapeutics) — legitimately independent data points that happen to share standard MFN
  template language, not a counted-twice bug like the 1.1.2/1.3.1 findings.

### [x] 2.1.6 safe_pro_rata_side_letter
- **Verified clean.** N=15, class balance 9 yes / 6 no. gemma3-1b 93.3% acc/20% wobble,
  deepseek-v4f 100%/0%. All 9 "yes" items share byte-identical `validating_quote` boilerplate
  ("...pany will execute a Pro Rata Rights Agreement, unless the Investor is") — verified this
  reflects genuinely standard YC SAFE template language (not a corpus copy-paste bug); the
  actual test is yes-vs-no discrimination against the 6 "no" items where the clause is
  genuinely absent, which both models handle well. Repeat-company pairs (SNM Global Holdings
  ×2, SOS Hydration ×2) verified as different accession numbers / different SAFE instruments,
  consistent with the already-established "legitimately independent, same company over time"
  pattern from 1.1.2/2.1.5, not duplicates.

**Family 2.1 (SAFEs, 2.1.1-2.1.6) now fully audited.**

### [x] 2.2.1 note_principal
- **Verified clean, both models 100%/0% wobble.** N=7. Noted a source-concentration pattern:
  5 of 7 items (`minerco_ciarello/schmidt/msf/rios/pacific_isle`) all come from the SAME
  accession number (`0001213900170072`) — one Minerco Inc. filing disclosing 5 DIFFERENT
  promissory notes to 5 different noteholders/dates. Confirmed these are genuinely independent
  facts (different principal amounts $12,500/$12,500/$350,000/$100,000/$250,000, different
  dates Feb–Aug 2016), not a duplicate-filing bug — the two $12,500 notes (Ciarello, Schmidt)
  are a real coincidence, 2 weeks apart. Not fixed since it's not wrong data, just flagging
  that 71% of this leaf's N=7 traces to one company/filing — low source diversity, worth
  broadening in a future re-sourcing pass even though it isn't causing measurable score harm
  today (both models already 100%).

### [x] 2.2.2 note_interest_rate
- **Verified clean.** N=6, deepseek-v4f 100%/0%, gemma3-1b 83.3%/0%. Checked the one
  outlier-looking value (Acology, 0.28% — unusually low for a note) against full corpus text:
  confirmed genuine, explicitly explained in the document itself ("twenty-eight hundredths of
  one percent (0.28%) per annum [to be the Applicable Federal Rate for 1-year loans]") — some
  notes are deliberately pegged to the minimal IRS Applicable Federal Rate, not an error.
  `greenfieldrobotics_8p00`'s id/filename doesn't match its `company` field ("Golden Matrix
  Group, Inc.") — same recurring cosmetic filename-vs-company-field pattern as 1.1.3/2.1.3, the
  tested 8% figure itself is textually solid regardless.

### [x] 2.2.3 note_maturity_date
- **Verified clean.** N=4 (small — flagging low-N, not fixing). deepseek-v4f 100%/0%,
  gemma3-1b 50%/50%. Both of gemma3-1b's misses verified as genuine date-field confusion, not
  oracle bugs: Gardenburger's clause reads "...MATURITY DATE...together with interest thereon
  calculated from Sept[ember]..." — gemma appears to have latched onto the nearby interest-
  accrual-start date instead of the explicit "MATURITY DATE" label. Acology's miss is a clean
  off-by-one-year (2014 vs 2015), also a plausible extraction slip, not a labeling error.
  task.py's design allows a "literal relative date text" fallback (e.g. "60 months from
  Closing") for notes without a fixed calendar date, but 0/4 real items exercise that path —
  an untested code path, not a bug, just unexercised.

### [x] 2.2.4 note_valuation_cap
- **CRITICAL bug found + FIXED:** `exyn_technologies`'s corpus window (built by `source.py`'s
  `window_on(text, anchor, before=420, after=900)`) anchored on "the quotient resulting from
  dividing the Valuation Cap by the number of fully diluted shares" — a formula clause that USES
  the term "Valuation Cap" but never states its dollar value. Verified via the real EDGAR filing
  (CIK 1960355, Exyn Technologies Inc., accession `0001104659-26-032156`,
  `tm2525579d10_ex10-26.htm`) that the actual defining sentence — `"Valuation Cap" means
  $90,000,000.` — sits ~3,500 characters LATER in the same document, far outside the anchor's
  `after=900` reach. The model-facing window genuinely never contained the ground truth —
  deepseek-v4f's pre-fix "100% accuracy" on this item was necessarily a lucky/plausible guess,
  not real extraction (confirmed: it produced 90000000 with 100% run-to-run consistency despite
  the number not being in its input, which is itself a small red flag for guess-vs-extraction
  auditing in general). Fixed by re-anchoring on the actual defining sentence (grounded against
  the real filing, not guessed) and regenerating the window via `source.py`. Reran clean:
  deepseek-v4f still 100%/0% (now genuinely reading the value), **gemma3-1b now shows its real,
  previously-hidden performance: 75% acc/50% wobble** (was 50%/50% under the old, unanswerable
  window) — an honest score increase since the task became answerable, not a data-quality
  regression.
- Verified the other 3 items (`damon_tranche_19to22`, `realpha_cap_definition`,
  `greenfield_robotics`) all cleanly anchor on the actual literal dollar-figure sentence, no
  similar windowing gap.

### [x] 2.2.5 note_discount
- **Bug found + FIXED, confirmed real via rerun:** `_SYSTEM` prompt used "20%"/"25%" as
  illustrative discount examples, and `_INSTRUCTION` separately CONTRADICTED `_SYSTEM` on the
  no-discount case (`_SYSTEM` said answer the literal string `"NONE"`, `_INSTRUCTION` said use
  JSON `null`) — fixed both. The example-number issue was real, not just theoretical: pre-fix,
  gemma3-1b answered exactly `"20.0"` on ALL 4 items with 100% run-to-run consistency each time
  (a clean anchor-bias signature — it copied the prompt's own first example number regardless
  of document content), scoring a misleading 25% (1/4, matching by luck on the one item whose
  true value happened to be 20%). Swapped the worked examples to 33.0/62.5 (neither matches any
  real item) and reran: **gemma3-1b's honest score is 0% accuracy** — it cannot do this
  extraction+transformation task at all, previously masked by the anchor coincidence. deepseek-
  v4f stayed 100%/0% throughout (never affected). No item exercises the no-discount/null path
  (0/4), so that half of the fix is documented-but-unexercised, same as 2.2.3's status.

### [x] 2.2.6 note_qualified_financing_threshold — N=2, SMALL-SAMPLE FINDING (not fixed)
- **Bug found + FIXED (preventive, not measured-harmful):** identical example-number issue —
  `_SYSTEM`'s worked examples were literally `'10000000' or '40000000'`, and this leaf's ONLY 2
  real items are exactly $10,000,000 and $40,000,000. Unlike note_discount, this did NOT
  measurably affect scores either before or after the fix (gemma3-1b and deepseek-v4f both
  100%/0% wobble pre- AND post-fix) — but with only 2 items and both examples being the literal
  true answers, the leaf carried near-zero true discriminative signal regardless of the
  observed clean scores. Fixed the examples to 15000000/75000000 anyway (cheap, safe,
  confirmed harmless via rerun) for future-proofing.
- **Minor, NOT fixed — needs re-sourcing, flagging for Eikiyo:** N=2 is the smallest sample
  size found in the entire audit so far. Two items cannot support any real statistical claim
  about model capability on this field; both current scores (100%/100%) should be read as "no
  evidence of failure on 2 examples," not "the model has mastered this task." Worth a
  re-sourcing pass to grow N, no code changes needed to act on this.

### [x] 3.1 current_ownership_pct
- **Verified clean.** N=9, all from Uber's S-1 (single-source concentration, like 2.2.1's
  Minerco pattern — noted, not fixed, since all 9 are genuinely different real shareholders'
  independently-computed percentages, not repeats). Checked for the most concerning possible
  bug on a COMPUTE-type task — leakage of the pre-computed answer into the model-facing window
  — by direct inspection of `corpus/questions/uber_ryan_graves.txt`: confirmed the window shows
  ONLY the raw share count and total (33,184 / 1,362,500 thousand), never the "2.4%" result;
  that percentage only exists in the oracle's own `validating_quote` metadata field, which
  `build_prompt()` never reads. Verified the math independently on 2 items (Ryan Graves:
  33,184/1,362,500×100 = 2.44% → 2.4% ✓; all-directors group: 462,351/1,362,500×100 = 33.93% →
  33.9% ✓). gemma3-1b scores a genuine 0% acc / 100% wobble — total failure at 2-operand
  division+rounding, an honest, expected result for a 1B model on an arithmetic task, not a bug.

### [x] 3.2.1 founder_ownership_pct, 3.2.2 investor_ownership_pct, 3.2.3 employee_pool_pct
- **SOURCE-CONCENTRATION FINDING across all of family 3.2 (data NOT touched, math verified
  correct):** all three leaves' entire corpora are drawn from the SAME single Uber Technologies
  S-1 filing already used by leaf 3.1. 3.2.1's 3 items (Garrett Camp, Travis Kalanick, Ryan
  Graves) and 3.2.2's 4 items (SB Cayman, Benchmark, PIF, Alphabet) are the SAME people/numbers
  already present in 3.1's 9-item set, just re-labeled "founder"/"investor" — i.e. these two
  leaves currently test ZERO new computations beyond what 3.1 already covers, just a taxonomic
  relabeling of the same 7 of 9 facts. 3.2.3 (`employee_pool_pct`) has only **N=1** — the single
  smallest leaf in the entire audit, unable to support any claim at all. Scores are internally
  consistent with 3.1 (gemma3-1b 0%/100% wobble on all three — same total division-arithmetic
  failure; deepseek-v4f 100%/0% on all three), confirming these aren't independently-scored new
  signal. Verified the math is correct on 3.2.1/3.2.2 (same S-1 table, already checked in 3.1).
  **ACTION NEEDED FROM EIKIYO:** re-source family 3.2 from additional, independent S-1 filings
  (not just Uber) to make these three leaves test something 3.1 doesn't already cover, or fold
  them into 3.1 explicitly and retire the sub-split?

### [x] 3.3 option_pool_shuffle
- **Verified clean, both models genuinely struggle (gemma3-1b 0%, deepseek-v4f 33%) — a hard,
  legitimate multi-step cap-table computation.** N=3, all 3 items sourced from ONE real SEC
  filing (Snapwire Media's Form C Regulation Crowdfunding exhibit, CIK 1680084) — but this
  exhibit is specifically a WeFunder standard-template "Appendix II" containing 3 WORKED
  ILLUSTRATIVE EXAMPLES of the option-pool-shuffle math, not 3 independent real financing
  events. This is a real but already self-documented limitation (task.py's own docstring calls
  out the provenance as "a WeFunder AFE template's Appendix II" and notes this leaf was already
  rebuilt once from a broken field-name state) — flagging for awareness, not re-litigating a
  decision that was already made deliberately. Spot-verified the math setup is internally
  coherent (price-per-share figures match the stated share-count/dollar-amount pairs in each
  worked example).

### [x] 3.4 fully_diluted_basis
- **Verified clean.** N=8, perfect 4/4 class balance, genuinely diverse sourcing (Actelis,
  Sybari, Emageon, IGN Entertainment, HyreCar, Castle Biosciences). Good adversarial design:
  Actelis and IGN Entertainment each contribute TWO items (`_ex` vs `_body`) with DIFFERENT
  labels — one clause from an exhibit defining fully-diluted basis, one from the same company's
  main filing body just stating a plain issued/outstanding share count — testing whether the
  model can distinguish capitalization convention even within one company's own paperwork,
  correctly NOT a duplicate. deepseek-v4f 100%/0%. gemma3-1b 50% acc/100% wobble — verified
  this is a clean class-collapse (got all 4 "fully-diluted" items right, all 4
  "issued-outstanding" items wrong), a real model bias, not chance or a data bug.

### [x] 3.6 multi_round_stacked_dilution
- **Verified clean.** N=5, deepseek-v4f 100%/0%, gemma3-1b 0%/80% wobble (genuinely hard
  2-input arithmetic with a distractor number in every window). Leaf already carries its own
  honest "REDEFINITION NOTE" in task.py documenting a prior, deliberate re-scoping (the
  original Series A/B/C stacked-ownership-cascade spec was unsourceable from real filings, so
  it was redefined to the equivalent real construct — IPO Dilution-section math) — a
  transparent design decision, not a bug. Checked the most likely failure mode for a COMPUTE-
  type leaf — the final answer being leaked as literal text in the window — by direct
  inspection of `corpus/questions/civitas.txt`: the window shows only the 4 raw input rows
  (offering price $21.50, historical NTBV -$24.99, increase/share $13.60, pro forma NTBV
  -$11.39), never the "Dilution per share = $32.89" summary line itself. Verified the math
  independently: 21.50 − (−11.39) = 32.89 ✓, matches the oracle exactly. gemma3-1b's civitas
  miss (answered 13.6) is exactly the "increase per share" distractor row, not a data bug — a
  genuine wrong-row-grabbed reasoning failure.

**Family 3 (cap tables, 3.1-3.6) now fully audited.**

### [x] 4.3 preference_stack_payout
- **Verified clean.** N=2 (small, noted). deepseek-v4f 100%/0%, gemma3-1b 50%/100% wobble.
  Good design: both items' windows show the SAME full Series A + Series B figures (from the
  Connecture SC 13E-3 fairness opinion already used by 4.1), differing only in a "TARGET
  SERIES:" header — genuinely tests whether the model selects the right series' numbers, not
  just extracts a lone figure. Verified the math independently: Series A $52.0M pref +
  $6.9M accrued dividends = $58.9M ✓; Series B $17.5M + $2.2M = $19.7M ✓. No leakage — neither
  final total (58.9/19.7) appears as literal text in either window.

### [x] 4.4 convert_vs_preference_decision
- **Verified clean.** N=2 (small, noted), perfect 1/1 class balance (the best achievable at
  N=2). deepseek-v4f 100%/0%. gemma3-1b 50%/0% wobble — verified this is a clean 2-item binary
  chance pattern (answers the same class consistently every run, correct on exactly one of the
  two by construction), not a bug. Same Snapwire Media WeFunder AFE-template source as leaf
  3.3, already flagged there — not re-logging as a fresh finding.

**Family 4 (waterfall, 4.1/4.3/4.4) now fully audited.**

## Next leaf: 5.1 board_seats_investor
