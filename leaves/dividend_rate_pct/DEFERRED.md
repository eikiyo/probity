# DEFERRED — dividend_rate_pct leaf (1.4.1)

Audit (2026-06-30): agent sourced 8 "dividend rate" items, but ALL 8 are off-thesis — Freddie Mac
and Bank of America perpetual bank-regulatory-capital preferred stock, not venture-financing
preferred. This benchmark's corpus is venture-financing legal documents (the sibling leaf
`dividend_cumulative` correctly used Jazz Semiconductor / Fitbit / Zoom / Teladoc / biotech VC
charters). Bank perpetual preferred uses standardized boilerplate very different from negotiated
VC Series A-D clauses and would bias this leaf's results in a way incomparable to every other leaf.
Also caught one mislabeled company name (real filer for "exhibit46" is Citizens Financial Group,
labeled generically instead).

One reusable item confirmed: `dividend_cumulative`'s MELINTA THERAPEUTICS document
(1461993_000119312517361673) states "at the rate of 8%, compounding per annum" -- genuine VC
preferred, can be re-anchored for this leaf without re-fetching.

Needs: 4-6 more genuine VC-charter dividend-rate clauses (reuse dividend_cumulative's other fetched
documents where possible, or fresh EDGAR FTS scoped to the same corpus style) before this can ship.
source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated from the bad ITEMS dict.
