# DEFERRED — financial_statement_qa leaf (7.5)

## Status
Never attempted this session. `engine/registry.json` itself flags this leaf as
`"uncertain": "needs a labeled financial-statement set"` -- meaning the task's own design is
incomplete, not just its sourcing.

## Why it's not buildable yet
"Financial statement Q&A" as a field name doesn't specify WHICH question against WHICH
statement (income statement line item? balance sheet ratio? cash-flow figure?), nor what
"correct" means without a labeled question-answer set to draw from. Building this leaf
requires a DESIGN decision (what specific financial-statement fact is being tested, and
against which real filing type -- 10-K, S-1 selected financial data, etc.) before any
sourcing work can start; sourcing real documents without that decision risks inventing the
task's scope on the fly, which is how contamination happens.

## Path to completion
Needs a design pass (similar to how `option_pool_shuffle`'s disambig note or
`current_ownership_pct`'s compute framing were decided) to pick one concrete, well-scoped
financial-statement fact to test, THEN real-document sourcing against that concrete spec.

No source.py/task.py/run.py ever written for this leaf.
