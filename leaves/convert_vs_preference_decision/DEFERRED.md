# DEFERRED — convert_vs_preference_decision leaf (4.4)

**Audit (2026-07-01):** Quick scan (5 min) — this leaf asks: should a holder convert to common or take their preference in an exit scenario?

The decision depends on:
- Preference multiple (from charter)
- As-converted ownership % (from cap table)
- Exit price (from transaction)
- Computed payouts under each path

**Finding:** No documents found that state all four pieces of data needed to make this decision and verify the answer.

**Needs:** Documents showing charter + cap table + exit price (S-4 is most likely).

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.
