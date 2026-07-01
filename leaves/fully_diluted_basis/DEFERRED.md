# DEFERRED — fully_diluted_basis leaf (3.4)

Audit (2026-07-01): a prior sibling-agent pass staged 10 items (8 "fully-diluted" / 2
"issued-outstanding") anchored on the phrases "Includes the Unissued Option Pool" /
"Excludes the Unissued Option Pool". Independent audit against the real fetched text found
TWO fatal problems:

1. **6 of the 8 "fully-diluted" items are near-duplicate boilerplate from ONE company**
   (Easterly Government Properties, Inc. REIT earnings releases, same "Fully diluted basis
   assumes the exchange of all outstanding common units representing limited partnership
   interests..." sentence repeated verbatim across 6 filings). Worse, this is REIT
   OP-unit/FFO earnings-release language, not venture-financing cap-table language at all —
   off-thesis, same failure class as the round_size (Occidental Petroleum) and
   dividend_rate_pct (Freddie Mac/BofA) deferrals: wrong document type entirely.

2. **The task's binary premise is broken.** Every genuinely on-thesis SAFE document checked
   (creciinc, rentberry, and 8 fresh EDGAR-FTS candidates: Neo Aeronautics, Oracle Health,
   Maison Luxe, Salspera, Complete Solaria, Ideanomics, AMC Robotics, Beyond Commerce, plus
   both Amass notes) is the SAME standard Y Combinator Post-Money SAFE "Capitalization"
   definition, and **every single one contains BOTH the "Includes the Unissued Option Pool"
   bullet AND the "Excludes the Unissued Option Pool" bullet in the same clause** (include the
   CURRENT pool as of signing; exclude FUTURE increases to it). There is no per-document
   fully-diluted-vs-issued-outstanding split in this corpus — the "issued-outstanding" label
   assigned to the two Amass notes was an artifact of which bullet a human window happened to
   center on, not a real distinguishing fact about that document. Confirmed by fetching the
   full text of all 10 candidates and grepping both anchor phrases in each: 10/10 contain both.

This is a task-design flaw, not a sourcing gap (§keyword-is-candidate-not-oracle: the anchor
phrase was treated as the oracle instead of read in the full clause). Fixing this needs either:
(a) a different real distinguishing fact (e.g. an older/non-YC-template charter that computes
ownership strictly on issued-and-outstanding shares with NO as-converted/option-pool language
at all, contrasted against a genuine as-converted/fully-diluted charter definition — check the
priced_equity charter corpus already fetched for participation_type/dividend_cumulative), or
(b) reframing the task entirely (e.g. extract the SPECIFIC clause's option-pool-increase
treatment as a 3-way distinction: current-pool-only / current-pool-excluded / silent).

source.py/task.py/run.py kept as scaffolding; oracle.jsonl left on disk but NOT run through
models and NOT promoted — do not trust its labels, they are the artifact described above.
