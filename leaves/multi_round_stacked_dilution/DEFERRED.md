# DEFERRED — multi_round_stacked_dilution leaf (3.6)

**Audit (2026-07-01):** Quick scan (5 min) of cap-table-related corpora found many charters but no documents showing:
- Series A issued at $X with Y% founders' stake
- Series B issued at lower $Z with computed dilution of founders
- Series C issued at further dilution
- All with real, verifiable numbers

**Finding:** Charters don't compute dilution; cap-table exhibits or S-1 capitalization sections do. None found in current corpus that show multiple rounds with share counts + ownership %.

**Needs:** S-1 Capitalization sections or S-4/proxy exhibits that show multi-series cap-table with pre- and post-dilution ownership percentages.

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.
