# DEFERRED — liquidation_waterfall_payout leaf (4.1)

**Audit (2026-07-01):** Quick scan (5 min) of liquidation/exit-related corpora found charters with waterfall mechanics but no documents showing:
- A real exit/liquidation value (e.g., "$100M M&A")
- A complete cap table (all series, share counts)
- The resulting payout to each series, calculated step-by-step

**Finding:** This is the most complex payout computation in the registry. Charters describe the waterfall (Series A paid first, then Series B, then common), but computing actual payouts requires both the charter terms AND real numbers (exit value + cap table), which are not co-located in single documents.

**Root cause:** Waterfall calculations are done by financial advisors / M&A counsel at time of transaction, not pre-computed in public filings.

**Needs:** S-4 proxies or acquisition press releases that state exit price AND include cap-table exhibits showing all series' shares and resulting payouts.

This is a rare and high-value item if sourced correctly (tests LLM's arithmetic on complex multi-step logic).

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.
