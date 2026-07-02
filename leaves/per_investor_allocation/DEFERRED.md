# DEFERRED — per_investor_allocation leaf (1.2.2)

## Status
Confirmed sourcing-wall deferral from an earlier session (2026-07-01, batch 3). No oracle
was ever generated for this leaf.

## What happened
A prior agent pass sourced candidate documents for this leaf but a fabricated/placeholder
item was caught and rejected before any model ran (see this project's STATE.md WIP-pointer
note: "1 confirmed sourcing-wall this session: `per_investor_allocation`"). No real,
clean candidate set was ever assembled.

## Why it's hard
This field asks for a SPECIFIC investor's slice of a larger multi-investor financing round
(as distinct from `round_size` 1.2.1, which asks for the round TOTAL). Real 8-K/press-release
financing announcements typically state the round total and the lead investor's name, but
rarely break out each individual investor's specific dollar allocation within the round --
that detail usually lives in a subscription agreement or side letter, which is not
separately, cleanly filed in a way that ties back to a public round-total announcement.

## Path to completion
Would need a real financing announcement that explicitly states BOTH the round total AND at
least one specific investor's individual allocation within it (not just "led by X" with no
dollar figure for X specifically), or a subscription-agreement exhibit with a stated
per-investor dollar amount cross-referenced to a public round announcement for the same
company/date.

source.py/task.py/run.py never built for this leaf; oracle.jsonl never generated.

---

**Follow-up audit (2026-07-02):** Re-attempted sourcing per Eikiyo's "finish all 22 pending"
directive. Tried real 8-K financing-announcement searches (Pressure Biosciences, OriginClear)
for a NAMED investor's specific dollar allocation within a larger multi-investor round; both
real candidates only disclosed the ROUND TOTAL across "certain accredited investors," never
broken out per-name (Pressure Biosciences' tiered dividend rate is keyed to purchase-price
BANDS, not a specific investor's actual amount). Confirms the original finding: individual
investor allocations within a round are not routinely disclosed in company-side filings.
Schedule 13D/13G (investor-side filings) were considered as an alternate real source but not
yet fetched/verified this session -- a real, not-yet-exhausted lead for a future attempt.
