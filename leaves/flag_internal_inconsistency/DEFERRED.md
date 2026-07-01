# DEFERRED — flag_internal_inconsistency leaf (8.6)

## Status
Never attempted this session. `engine/registry.json` itself flags this leaf as
`"uncertain": "needs a cross-field consistency spec"` -- meaning the task's own design is
incomplete, not just its sourcing.

## Why it's not buildable yet
"Flag internal inconsistency" needs a precise spec for WHICH two (or more) fields/clauses in
a document are being cross-checked for contradiction (e.g. a stated share count in one
section vs. a different share count in another; a stated exemption type vs. terms that don't
match that exemption's requirements). Without that concrete spec, sourcing would mean
inventing what counts as "inconsistent" on the fly per document -- exactly the kind of
judgment call that produced this session's contamination incidents when made informally
under time pressure rather than decided up front.

## Path to completion
Needs a design pass to pick one concrete, well-scoped cross-field consistency check (e.g.
"does the cover-page aggregate offering amount match the sum of per-investor amounts stated
elsewhere in the same Form D"), THEN real-document sourcing against that concrete spec, with
both the "consistent" and "inconsistent" classes drawn from real documents (not authored).

No source.py/task.py/run.py ever written for this leaf.
