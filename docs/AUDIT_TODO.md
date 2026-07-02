# Probity — Adversarial Audit Todo (all 60 built leaves)

Started 2026-07-02 per Eikiyo's directive: read every leaf individually, hunt for gaps/bugs/
breaking-points/stubs/hardcodes/half-done features, log findings here, fix what's safe to fix
immediately, flag judgment calls for explicit confirmation. Order = engine/registry.json ref
order (1.1.1 -> 8.6). Status counter recounted on every edit.

**Counter: 60/60 leaves audited · 52 fully resolved · 8 have a pending judgment call** — dated
2026-07-02. **ALL 60 BUILT LEAVES NOW AUDITED, leaf-by-leaf, in registry order.** 9 code bugs
found and fixed (with reruns where the fix could change scores); 8 findings need Eikiyo's
confirmation before any oracle.jsonl data is touched.

## Legend
- `[x]` audited + resolved (bugs fixed, or verified clean)
- `[~]` audited, one finding still pending Eikiyo's confirmation (not a code bug — a judgment call)
- `[ ]` not yet audited

## Pending-your-call summary (8 items — oracle.jsonl NOT touched on any of these)
1. **1.1.2 pre_vs_post_money** — 2/21 items are the same Cytosorbents transaction counted
   twice (8-K body + its own Exhibit 10.1). Drop the 2 duplicates and rerun at N=19, or leave?
2. **1.1.3 price_per_share — SEVERE** — 5/9 items (56%) are wrong instrument type (common-stock
   private placements, not preferred-stock rounds the task requires). Drop+re-source, reframe
   the taxonomy, or leave?
3. **1.3.1 liquidation_preference_multiple** — 3/13 items are exact duplicate clauses (same
   amendment text, different accession numbers) — true N is 10, not 13. Drop the 3 duplicates?
4. **1.5.1 antidilution_type** — 1/5 items (Popular Inc, a bank holding company) is off-thesis
   (TARP-era bank rights, not VC financing) though its label is textually correct. Re-source or
   leave?
5. **2.1.3 safe_cap_vs_discount_applies — SEVERE** — class distribution is 10 both-mfn / 1
   discount / 0 cap-only — one of the leaf's own 3 taxonomy classes is completely untestable.
   Re-source 2-3 genuine cap-only SAFEs, or accept as an effective 2-way task?
6. **6.1 vesting_schedule — SEVERE** — the World Heart Corp item is labeled "3yr/no-cliff" but
   the text explicitly says "one-year cliff" twice and describes 1/48-monthly vesting (textbook
   4yr/1yr-cliff). Sibling leaf 6.2 independently confirms the underlying schedule has a cliff.
   Evidence strongly favors relabeling to `4yr/1yr-cliff` — confirm?
7. **6.4 option_strike_409a — SEVERE, confirmed real harm** — 4/7 items' windows show a whole
   bulleted list of ~7 different real option grants with no target-grant marker, confirmed as
   the actual cause of deepseek-v4f scoring WORSE than gemma3-1b on this leaf (an inversion from
   every other leaf). Needs a window-redesign decision (narrow the window vs. add a "TARGET
   GRANT" marker like leaves 4.3/6.5/7.5 already use correctly).
8. **7.3 s1_use_of_proceeds — SEVERE, scoring methodology** — nearly every scored "miss" is a
   semantically-correct paraphrase marked wrong by exact-string-match scoring, while the prompt
   itself invites paraphrase ("as a short phrase"). Reported 20%/80% accuracy likely both
   understate true ~100% semantic accuracy. Needs either fuzzy/semantic scoring for free-text
   string fields, or a prompt change to request verbatim extraction (like the working 7.4
   pattern) — which approach?

9 code bugs found + fixed this session (all with reruns confirming the fix, except 2.2.5's
no-discount-string path and 2.2.3's relative-date path, which are documented-but-unexercised):
`engine/harness.py` checkpoint staleness (project-wide, 3 leaves affected) · `results/render.py`
+ `engine/models.py` DeepSeek retry logic (project-wide) · 1.2.1 round_size prompt ambiguity ·
1.6.2 auto_conversion_trigger gross/net wording · 2.2.4 note_valuation_cap missing-window
anchor · 2.2.5 note_discount NONE/null contradiction + anchor-bias example numbers · 2.2.6
note_qualified_financing_threshold anchor-bias example numbers · `engine/registry.json` 2
field-name mismatches (2.1.4, 7.2) · 7.2 form_d_fields wrong field type (string vs number).

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

### [x] 5.1 board_seats_investor
- **Verified clean.** N=9, genuinely diverse sourcing. Both models tied at 77.8% acc. Checked
  the multi-item-per-company pairs for duplicate-vs-legitimate: Cinemark/MDP has 2 items
  (`mdp`=5, `mdp_old`=9) from explicitly DIFFERENT agreements (a prior vs current designation
  right, before/after a renegotiation) — legitimate, not duplicated; Emergent Capital and Ute
  Energy each have 2 items with DIFFERENT named designators (PJC/Opal Sheppard,
  Quantum/Tribal) sharing one accession number — same "multiple distinct facts in one filing"
  pattern already established as fine in 2.2.1. Both models share the SAME one miss
  (Ute Energy "Tribal" item, both confidently answer 1 vs truth 2) — investigated as a possible
  shared oracle bug, but the real clause is a genuine trap: "Two (2) nominees... provided,
  however, that the right... shall be reduced from two (2) to one (1) at such time that the
  Tribal Stockholders cease to hold at least 25%..." — a BASE right of 2 with a CONDITIONAL
  reduction to 1. Oracle correctly uses the base/unconditional right (2), consistent with the
  established base-rate convention (2.1.2). Both models being fooled by the same conditional
  clause is a genuine, interesting shared difficulty signal, not a data bug.

### [x] 5.2 protective_provisions
- **Verified clean.** N=12, perfect 6/6 class balance, diverse sourcing. deepseek-v4f 100%/0%.
  gemma3-1b 58.3% — investigated because it's below the 50% chance floor plus one; confirmed a
  clean class-bias pattern (5/6 "no" items wrong, all mispredicted as "yes"; all 6 "yes" items
  correct) — a real model bias toward assuming a veto right exists, not a data bug. Trident
  Bancshares (a bank holding company labeled "no") looked like it might repeat the antidilution
  Popular Inc off-thesis pattern, but this leaf's own taxonomy explicitly scopes "no" to include
  non-VC document types ("a Letter of Intent... generic Articles of Incorporation with only
  default majority-of-all-stock voting") — in-scope by the task's own design, not contamination.

### [x] 5.3 information_rights
- **Verified clean.** N=12, perfect 6/6 class balance. deepseek-v4f 91.7% (1 miss), gemma3-1b
  50%. Task.py's own taxonomy documents a deliberate trap (waiver-of-delivery-obligation ->
  "no"); spot-checked deepseek's one miss (Bell Microproducts, true "yes", predicted "no") since
  it looked like exactly that trap firing backwards — confirmed via full text it's actually a
  SUBTLER, correctly-labeled variant: the clause waives PAST DEFAULTS for late delivery and
  extends the deadline, but explicitly keeps the underlying delivery obligation alive with new
  dates (Dec 2008/Mar 2009/Jun 2009) — a waiver of default/timing, not a waiver of the right
  itself, genuinely distinct from the taxonomy's documented "no" trap. Oracle's "yes" label is
  correct; deepseek likely pattern-matched the word "waives" without parsing what was waived.

### [x] 5.4 pro_rata_rights
- **Verified clean, both models 100%.** N=12, perfect 6/6 class balance. Notably this leaf's
  own `company` field already writes "Manako Labs (via TaoWeave filing)" for the item sharing
  the cross-leaf id/filename mismatch flagged under 2.1.3 — confirms whoever built this leaf
  was already aware of and correctly handled that naming quirk. Other repeat companies (SOS
  Hydration, Cantabio, Millennium Blockchain, Greenfield Robotics) all consistent with
  already-verified real-entity findings elsewhere in the audit — no new issue.

### [x] 5.5 rofr_cosale
- **Verified clean.** N=12, perfect 6/6 class balance. deepseek-v4f 91.7% (1 low-consistency
  miss, 55%), gemma3-1b 66.7%. Well-designed leaf: task.py's own docstring documents deliberate
  hard negatives (a company's own repurchase right on unvested stock, and a pro-rata future-
  financing right, both use adjacent vocabulary to a real investor RoFR/co-sale but aren't one)
  — deepseek's one miss (MotivNation, low-consistency "yes" vs true "no") is consistent with
  exactly this documented trap firing, not a data bug.

### [x] 5.6 drag_along
- **Verified clean.** N=12, perfect 6/6 class balance, deepseek-v4f 100%. gemma3-1b 41.7%
  (below chance) — checked per-instance breakdown: 4/6 "yes" correct, 1/6 "no" correct, a mild
  yes-leaning bias but genuinely mixed (not total collapse) — consistent with real difficulty on
  the OBLIGATION-vs-RIGHT legal distinction this leaf is designed to test, not a data bug.

### [x] 5.7 vesting_acceleration
- **Verified clean.** N=9, class balance 6 yes / 3 no (mild 2:1 imbalance, noted but not
  severe — the minority class still functions). deepseek-v4f 100%. gemma3-1b 66.7% happens to
  equal the trivial "always yes" baseline exactly, so checked per-instance: genuinely mixed
  (4/6 yes correct, 2/3 no correct, including one real "yes" miss) — not baseline-matching
  class collapse, an honest score.

**Family 5 (governance, 5.1-5.7) now fully audited.**

### [~] 6.1 vesting_schedule — SEVERE LABEL FINDING, PENDING EIKIYO'S CONFIRMATION
- **SEVERE, oracle NOT touched:** the `0001104659-09-054183_a09-26145_18k` (World Heart Corp)
  item is labeled `"3yr/no-cliff"`, but the ENTIRE model-facing window contains zero textual
  support for either "3 years" or "no cliff" — it explicitly says, twice, "**one-year cliff**"
  ("waiver of one-year cliff vesting requirement for any options that have not reached the
  one-year vesting cliff date") and describes a "credit for vesting... equal to **1/48th** of
  the option shares [per] full month" — 1/48 monthly is the textbook implementation of a
  4-year/1-year-cliff schedule (25% at the 1-year mark, 1/48 monthly thereafter), which is
  EXACTLY what task.py's own taxonomy defines `"4yr/1yr-cliff"` to mean. deepseek-v4f answered
  `"4yr/1yr-cliff"` with 100% consistency (i.e. it read the clause correctly and was marked
  WRONG by a mislabeled oracle) — this single item is very likely the direct cause of deepseek's
  only miss on this leaf (88.9% instead of 100%). Difficulty is marked `"hard"` in the oracle,
  which may reflect an intent to test something subtle, but nothing in the visible window
  supports the stated label. **ACTION NEEDED FROM EIKIYO:** the evidence strongly points to the
  correct label being `4yr/1yr-cliff` (matching the text and matching deepseek's actual answer)
  — confirm the relabel, or explain what source outside this window justifies `3yr/no-cliff`
  before I touch oracle.jsonl?
- **Cross-leaf confirmation (see 6.2 below):** the SIBLING leaf `cliff_present` sources this
  EXACT SAME document and correctly labels it `"no"` (cliff not currently in effect) precisely
  BECAUSE its own taxonomy defines a deliberate trap for "an excerpt whose operative text is a
  WAIVER of a cliff requirement" — i.e. cliff_present's own design confirms the underlying
  schedule genuinely HAS a cliff (that's what's being waived), which is the opposite of what
  6.1's "3yr/no-cliff" label claims. Two independently-built leaves reading the same real text
  disagree about its most basic structural fact — strong evidence 6.1's label, not the model
  answers, is the error.
- Otherwise verified clean: 8/9 other items' normalized formats spot-checked against real clause
  text, all correct. gemma3-1b's 25% (well below the 44% majority-class baseline) confirms it's
  not gaming class imbalance — a genuinely hard free-form-normalization task for a 1B model.

### [x] 6.2 cliff_present
- **Verified clean, well-designed leaf.** N=12, perfect 6/6 class balance. deepseek-v4f 91.7%,
  gemma3-1b 66.7%. Both models' one shared miss is the World Heart Corp "waiver of a cliff"
  trap item (both answer "yes", correct answer is "no" per the deliberate trap design) — a
  genuine, hard, correctly-designed adversarial item, and its correct labeling here directly
  helped confirm the 6.1 `vesting_schedule` mislabel above.

### [x] 6.3 acceleration_trigger
- **Verified clean.** N=13, balanced 7 double / 6 single, diverse sourcing. deepseek-v4f 100%.
  gemma3-1b 84.6%, both misses are single-trigger items mispredicted double-trigger — a mild,
  plausible bias (double-trigger is the more common real-world convention), not a data issue.

### [~] 6.4 option_strike_409a — SEVERE MULTI-VALUE AMBIGUITY, PENDING EIKIYO'S CONFIRMATION
- **SEVERE, oracle NOT touched, real measured harm confirmed:** at least 4 of 7 items
  (all the Medecision, Inc. ones, same source filing) have windows built by `source.py`'s
  `window_on(anchor, before, after)` that capture a WHOLE BULLETED LIST of many different real
  option grants at many different strike prices, with ZERO disambiguating marker for which
  bullet is "the" target grant. E.g. `0001125282-06-006236_0p03`'s window shows SEVEN different
  exercise prices in sequence ($0.25, $0.25, $0.03, $0.25, $0.60/$0.25/$1.00, $0.25, ...) with
  no "TARGET GRANT" header (unlike leaf 4.3's `preference_stack_payout`, which explicitly
  labels which series is being asked about). This is NOT hypothetical — it's the confirmed
  cause of deepseek-v4f's unusually poor 42.9% (worse than gemma3-1b's 57.1%, an inversion from
  every other leaf in this audit): on every Medecision miss, deepseek's 100%-consistent wrong
  answer is a DIFFERENT REAL price from the SAME window (0.03→guessed 0.25; 1.25→guessed 11.0;
  11.0→guessed 0.25; the 2.0 item's wrong 22.0 answer looks like a share-count/price digit
  merge from the same crowded bullet list) — i.e. deepseek is reading correctly and picking a
  plausible-but-wrong candidate from a genuinely ambiguous window, not hallucinating. Unlike
  2.2.4's `exyn_technologies` fix (a wrong anchor missing the value entirely, a mechanical fix),
  this needs a DESIGN decision — narrow `window_on()`'s `before`/`after` to isolate just the one
  target bullet, or add an explicit target-date/price marker to the window — not something to
  guess unilaterally. **ACTION NEEDED FROM EIKIYO:** which remediation approach, and should the
  fix apply project-wide to any leaf using a similarly wide window on a bulleted/list-style
  source document?
- WhiteGlove Health's 2 items (`0p61`, `7p5`) come from a DIFFERENT, cleaner-windowed source and
  both models get them right — confirming the bug is specific to the Medecision bulleted-list
  documents, not the leaf's whole design.

### [x] 6.5 exercise_window
- **Verified clean, and a useful positive contrast to 6.4's finding.** N=5, deepseek-v4f 100%,
  gemma3-1b 80%. This leaf's own docstring explicitly anticipates the exact multi-scenario-per-
  document problem found broken in 6.4, and solves it correctly: confirmed via
  `corpus/questions/sirva.txt` that every window opens with a literal "TARGET SCENARIO: ..."
  header disambiguating which of the document's several termination-window clauses to answer
  for — the same design pattern already verified working in leaf 4.3. Good reference example
  for whatever remediation approach gets chosen for 6.4.

**Family 6 (vesting, 6.1-6.5) now fully audited.**

### [x] 7.1 securities_exemption
- **Confirms the earlier checkpoint-staleness fix (commit `ba322a7`/`cd270fa`) landed clean.**
  This was one of the 2 sibling leaves the repo-wide sweep found affected by the same bug as
  1.1.1; already fixed + rerun earlier this session. Current state: N=10, deepseek-v4f and
  gemma3-1b both 100% accuracy (0.3/0.4 wobble — some run-to-run flips but always converging to
  the right majority answer). Class balance 6×506b / 4×506c; `504` is a defined taxonomy value
  with zero real items — same class-coverage-gap pattern as 1.3.1/1.5.1, noted not fixed.

### [x] 7.2 form_d_fields
- **CRITICAL bug found + FIXED, confirmed via rerun:** task.py declared
  `"type": "string"` for `form_d_field_value`, but the value is a dollar amount.
  `engine/normalize.py`'s `canonical()` routes `"string"` fields through `_canonical_enum()`
  (NFKD + casefold + trim only — no `$`/comma stripping), while `"number"` fields route
  through `_canonical_number()` (which strips `$`, commas, whitespace before parsing). Both
  models were extracting the semantically CORRECT figure every time — gemma3-1b answered
  `"$2,366,532"` (with a `$`) vs oracle's stored `"2,366,532"`, and `"70227931.85"` (no commas)
  vs oracle's `"70,227,931.85"` — genuinely right values, scored 0/2 (0%) purely because the
  `"string"` comparison path never normalized away the punctuation difference. Changed the
  field type to `"number"` (verified `engine/scorer.py` only branches on `fspec["type"]`, "op"
  is documentation-only, and `_canonical_number` correctly parses comma-formatted string values
  like the oracle's own stored `"2,366,532"`). Reran: **gemma3-1b jumped from 0%/50% wobble to
  a genuine 100%/0%** — deepseek-v4f, which happened to answer in oracle-matching format by
  luck, stayed 100%/0% throughout, so this bug was silently deflating ONLY gemma3-1b's score.
  Same registry field-name-mismatch leaf already flagged in 2.1.4's repo-wide sweep entry.

### [~] 7.3 s1_use_of_proceeds — SEVERE SCORING-METHODOLOGY FINDING, PENDING EIKIYO
- **Verified sourcing clean, and this leaf's own docstring already documents a serious past
  fix** (a prior version shipped 59 items sourced from the WRONG document type — SEC comment
  letters ABOUT a Use of Proceeds section, not the section itself — since fully rebuilt from
  real S-1/424B4 prospectus bodies).
- **SEVERE, NOT fixed (needs a design decision, not a mechanical patch):** nearly every scored
  "miss" on this leaf is a model giving a SEMANTICALLY CORRECT paraphrase marked wrong by pure
  exact-string-match scoring. Examples, all with the SAME meaning as truth: gemma3-1b
  "research & development" vs truth "research and development activities" (WRONG);
  "working capital & general corporate purposes" vs truth "working capital and general
  corporate purposes" (WRONG, differs only by "&" vs "and"); "redemption of senior notes" vs
  truth "redeem all of the senior notes" (WRONG); deepseek-v4f "advance liver programs" vs
  truth "advance our current liver programs" (WRONG, missing 2 filler words). Root cause: the
  `"string"` field type routes through `_canonical_enum()` (NFKD + casefold + trim only, no
  fuzzy/semantic comparison), but the prompt EXPLICITLY invites paraphrase ("extract... as a
  short phrase (the main category or purpose named)") rather than asking for a verbatim quote.
  gemma3-1b's reported 20% and deepseek-v4f's reported 80% both understate real semantic
  accuracy, likely close to 100% for both. **This is a task-methodology question, not a bug I
  can fix unilaterally:** (a) switch scoring to semantic-similarity/fuzzy match for free-text
  string fields, or (b) tighten the prompt to request a literal verbatim substring instead of a
  paraphrased "short phrase" so exact-match becomes the right tool, or (c) accept current
  strictness as intentional. **ACTION NEEDED FROM EIKIYO** — likely affects 7.4
  `s1_risk_factors` too (same field-type + free-text-paraphrase pattern), will check there next.

### [x] 7.4 s1_risk_factors
- **Verified clean — a useful contrast to 7.3's finding.** Unlike 7.3, this leaf's prompt
  correctly requests VERBATIM extraction ("extract ONLY the heading sentence... the exact
  heading sentence"), so exact-match scoring is the right tool here and the leaf does NOT share
  7.3's scoring-methodology issue. gemma3-1b's real 0% is a genuine model failure: checked its
  actual answers and it consistently either truncates the true sentence mid-way (drops the
  second clause) or collapses it into a short bolded title-style paraphrase instead of copying
  the full literal sentence — real small-model long-span-copying weakness, not a bug.
  deepseek-v4f 100% (genuinely verbatim-copies correctly).

### [x] 7.5 financial_statement_qa
- **Verified clean.** N=5, correct `"type": "number"` (no repeat of 7.2's bug). Uses the
  already-validated "TARGET PERIOD specified at the top" disambiguation pattern (same family as
  4.3/6.5). deepseek-v4f 100%. gemma3-1b 20% — its wrong answers are all plausible OTHER real
  numbers from the same dense multi-period Selected Financial Data table (a genuinely hard
  table-reading task for a 1B model), not obviously wrong/hallucinated figures.

**Family 7 (regulatory/disclosure, 7.1-7.5) now fully audited.**

### [x] 8.1 flag_offmarket_liqpref
- **Verified clean.** N=10, perfect 5/5 balance. deepseek-v4f 90% (1 miss), gemma3-1b 40%
  (mixed both directions — 2 real "yes" missed, 4 real "no" missed, not simple collapse).
  Taxonomy explicitly documents a trap ("accrued dividends added on TOP of a 1x preference do
  NOT make it >1x"); spot-checked deepseek's one miss (Workday) — its real clause reads "an
  amount equal to their original issue price per share, plus any declared but unpaid
  dividends," exactly the documented 1x-plus-dividends "no" case — a genuine reasoning error on
  the intended trap, not a data bug. Most of gemma3-1b's false-"yes" misses are the same
  cumulative-dividend companies already verified in leaf 1.4.2 (Fitbit, Akouos, BioAccelerate),
  consistent with the same trap firing repeatedly.

### [x] 8.2 flag_full_ratchet
- **Confirms the earlier checkpoint-staleness fix (commit `ba322a7`/`cd270fa`) landed clean —
  this was the other sibling leaf found affected alongside 1.1.1 and 7.1.** Current state: N=7,
  class balance 4 yes / 3 no, deepseek-v4f 100%/0%, gemma3-1b 57.1%/28.6% wobble — plausible,
  no shared-confusion signal remaining post-fix.

### [x] 8.3 flag_uncapped_participation
- **Verified clean.** N=13, class balance 9 no / 4 yes (mild imbalance, noted). gemma3-1b
  30.8% is BELOW the 69.2% trivial "always no" baseline — confirms genuine struggle, not
  baseline-gaming. deepseek-v4f 84.6%, both misses are real "yes" items (scPharmaceuticals,
  Akouos) called "no" — the harder minority class, consistent with the nuanced
  uncapped-vs-capped-vs-non-participating distinction this leaf tests; both companies already
  independently verified elsewhere in this audit (1.3.2, 1.4.2), no new concern.

### [x] 8.5 flag_missing_pro_rata
- **Verified clean.** N=4 (small, noted), correct `"type": "bool"` (no repeat of 7.2's bug),
  perfect 2/2 class balance. deepseek-v4f 100%. This leaf's own docstring documents an
  exceptional prior self-audit (found the original "no" class was noise/unrelated exhibits,
  fixed by re-sourcing 2 genuine real explicit-waiver documents) — a good historical example of
  this exact audit process working. All 4 companies (Xcyte Therapies, Rapid7, Greenfield
  Robotics, SOS Hydration) already independently verified as real, distinct entities elsewhere
  in this audit — no new concern.

### [x] 8.6 flag_internal_inconsistency
- **Verified clean — independently re-derived all 5 labels from the raw citation pairs shown to
  the model, all correct:** Actelis 94,318,590 vs 94,318,590 → match → False ✓; Castle Bio
  (consistent) 17,203,496 vs 17,203,496 → match → False ✓; Castle Bio (inconsistent) 17,203,496
  vs 17,360,096 → differ → True ✓; HyreCar 12,191,508 vs 12,331,348 → differ → True ✓; IGN
  Entertainment 20,392,610 vs 20,824,068 → differ → True ✓. Good deliberate design: the two
  Castle Bio items share the same Citation A but a different-dated Citation B, a clean
  contrastive near-duplicate pair (not a bug) testing the same underlying number against two
  different real comparison points. deepseek-v4f 100%, gemma3-1b 60%.

**Family 8 (risk flags, 8.1/8.2/8.3/8.5/8.6) now fully audited. ALL 60 BUILT LEAVES AUDITED.**
