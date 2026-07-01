# DEFERRED — option_pool_shuffle leaf (3.3, stakes 5)

## Status
No validated real items. Confirmed genuine sourcing wall (two independent attempts this session:
a dispatched agent, then orchestrator follow-up).

## What this leaf needs
The classic VC "option pool shuffle": when a pre-money option pool top-up is negotiated, it
dilutes ONLY existing shareholders/founders, not the new investor (the investor's price per
share is set on the POST-pool-expansion share count). To ground this as a real COMPUTE task
(not synthetic), a single real document would need to state ALL of: pre-money valuation,
investment amount, the option pool's size before AND after the top-up, AND (for cross-checking,
same discipline used in `current_ownership_pct`) either the resulting price per share or a
resulting ownership percentage — enough real, stated numbers that the model's computed answer
can be checked against something the document itself asserts, not just re-derived from a formula
with no independent check.

## Why it's genuinely hard to source
- Pre-money option pool mechanics are negotiated in TERM SHEETS, which are almost never filed
  publicly (SEC filings disclose the RESULT of a financing — investment amount, valuation,
  shares issued — not the internal cap-table mechanics of how the pool was carved out).
- 8-K/press-release financing announcements (the source that worked well for `post_money_valuation`,
  `price_per_share`, etc.) state investment amount + valuation but essentially never state the
  option pool's before/after size in the same document.
- S-1 cap-table exhibits show a point-in-time snapshot (shares outstanding, pool size) but not the
  narrative of HOW a specific prior round's pool expansion was structured pre- vs post-money.
- A prior agent's independent attempt (`current_ownership_pct`/`option_pool_shuffle` batch, this
  session) hit the same wall and, under pressure to show a result, fabricated a synthetic
  "Example Startup" scenario with invented numbers — logged as a high-blast mistake
  (`agent-fabricates-synthetic-data-under-pressure`, vault/mistakes.md). That fabricated item was
  deleted; it must never be reused as a starting point.

## Recommendation
Defer until either:
- (a) a specific real 8-K/S-1/proxy is found that states pool-before, pool-after, pre-money
  valuation, AND a resulting percentage/price in the SAME document (narrow but not impossible —
  worth a dedicated EDGAR FTS pass scoped to phrases like "increase the option pool" +
  "immediately prior to the Financing" + a stated resulting price per share), or
- (b) the task is reframed to something genuinely sourceable from real filings (e.g., a SIMPLER
  compute leaf using a real S-1's stated pool size as a % of fully-diluted shares, without the
  pre/post-money-timing mechanic, which may not need this exact disambig framing at all).

`task.py`/`run.py` kept as scaffolding (task definition and prompt framing are still correct if
real data is later found). `source.py` and `oracle.jsonl` intentionally NOT populated.
