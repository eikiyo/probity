# DEFERRED — participating_vs_nonpart_payout leaf (4.2)

**Audit (2026-07-01):** reviewed participation_type corpus (43 real charters already classified as participating/non-participating/capped) searching for items that state:
- A specific liquidation preference multiple (e.g., "1x", "2x", "3x") 
- A real, concrete exit/liquidation event value (e.g., "$100M exit", "IPO at $50 per share", "acquisition for $X")
- Enough information to compute participating vs non-participating payout difference

**Finding:** The participation_type leaf classifies clauses correctly (e.g., "greater-of structure = non-participating"), but the charters themselves do NOT state hypothetical or actual exit values. They describe the legal terms: "liquidation preference of 2x, participating in pro-rata excess", but do not include worked examples like "if the company is sold for $100M, holders receive...".

**Root cause:** Venture charters describe the terms (the "what") but almost never include worked payoff calculations (the "how much"). A company would need to calculate its own cap table waterfall at the time of exit; this is not disclosed in the public charter filing itself.

**Needs:** 2-4 real charters or exhibits that state:
- A specific liquidation preference multiple (from the charter)
- A real stated exit/liquidation event with a concrete dollar amount (from the same document or a cap-table exhibit)

Sources: S-4s (which recap cap tables at merger), proxy statements on acquisitions (which state exit price), or Form S-1 "Capitalization" sections that may include historical cap table data with exit values.

**Alternative:** Defer until documents that include both charter terms AND cap-table excerpts or historical exit data are available in the corpus.

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.
