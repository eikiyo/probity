# DESIGN — temperature 0.1 sweep (paired against 0.7)

> **This is a POINTER, not the document.** The canonical design doc lives at
> [`docs/wip/DESIGN-temperature-sweep-t01.md`](../../docs/wip/DESIGN-temperature-sweep-t01.md),
> per Kage root `CLAUDE.md` §0.9 (Kage OS v2 doc lifecycle: docs are born in `docs/wip/`, carry a
> machine-parseable `> STATUS:` header, and `git mv` to `docs/done/` when shipped AND verified).
>
> This stub exists only because `~/.claude/hooks/decision-gate.sh` predates the v2 layout: it walks
> up from the file being written looking for `DESIGN.md` or `Support Docs/Product Design/DESIGN-*.md`
> and does not know about `docs/wip/`. A project that correctly follows §0.9 is therefore blocked
> from writing any code. Logged for a proper gate fix (add `docs/wip/DESIGN-*.md` to the hook's
> search); until then this pointer keeps the gate honest without duplicating the content.

## Summary (full detail in the canonical doc)

A second complete results matrix at **temperature 0.1**, mirroring the existing **0.7** matrix
(11 models x 60 leaves x n=20), so the two compare as a paired difference with no adjustment.

- **Parity contract:** 8 axes held identical between arms (model id, routing, prompts/corpus,
  scorer, n=20, request payload, runtime, calendar window). Axes 3 and 4 verified byte-identical
  via git; 5 enforced by a fail-closed coverage assert; 7 and 8 fixed by running both local arms on
  Kaggle T4 and both hosted arms in the same window (Plan B).
- **No adaptive sampling.** Every cell gets n=20. No screening, escalation, or early stopping.
- **Three arms on disk**, never overwriting: historical `scored.json` (0.7, published),
  `scored_t07.json` (fresh 0.7 control), `scored_t01.json` (the new matrix).
- **Sad-path table** (10 rows) seeded from the guardrail catalog, headed by the defect this work
  uncovered: a per-leaf cost guard silently truncated 5 cells in the 0.7 arm, and because a missing
  item can never be counted as flipping, missing data biases wobble **downward** (models look more
  reliable than they are). Fixed by asserting recorded calls against `items x n_runs` read from
  `oracle.jsonl`, an independently declared source.
- **Statistics:** Wilson score intervals (never Wald: several models sit near 3%); Newcombe paired
  intervals for the 0.7-vs-0.1 delta; explicit "statistically indistinguishable" grouping where
  intervals overlap.
- **Constraints:** pure stdlib, no new dependencies, every published number regenerable from disk.
