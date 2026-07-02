# Probity — Adversarial Audit Todo (all 60 built leaves)

Started 2026-07-02 per Eikiyo's directive: read every leaf individually, hunt for gaps/bugs/
breaking-points/stubs/hardcodes/half-done features, log findings here, fix what's safe to fix
immediately, flag judgment calls for explicit confirmation. Order = engine/registry.json ref
order (1.1.1 -> 8.6). Status counter recounted on every edit.

**Counter: 20/60 done · 0 in-progress · 36 pending · 4 partial** — dated 2026-07-02. Families 1 (1.1.1-1.7) + 2.1 SAFEs (2.1.1-2.1.6) complete.

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

## Next leaf: 2.2.1 note_principal
