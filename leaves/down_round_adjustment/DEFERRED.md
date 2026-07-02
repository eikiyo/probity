# DEFERRED — down_round_adjustment leaf (1.5.3)

**Audit (2026-07-01):** scanned flag_full_ratchet (14 docs) and antidilution_base (10 docs) for documents containing:
- A prior round's conversion price or ratio (Series A at price $X)
- A down round's lower price (Series B at price $Y, where Y < X)
- An explicit full-ratchet adjustment formula with concrete numbers
- A resulting adjusted Series A conversion price, stated or derivable from the document

**Finding:** None of the 24 documents scanned contain a worked example of a full-ratchet anti-dilution adjustment with real numbers. The documents all contain the legal machinery (clauses defining the adjustment formula), but none state:
- "Series A was originally at price $5.00"
- "Series B issued at $2.00"
- "Series A conversion price was adjusted to $2.00 per full ratchet"

Zix Corporation 8-K (0000950134-02-011491) came closest, showing Series A at $3.92 and Series B at $3.60, but this was the initial issuance (no historical prior round to adjust from), and no worked adjustment was stated.

**Root cause:** Full-ratchet adjustments are rare in practice and rarer still in public documents. Most venture charters describe the machinery but do not include worked examples with concrete numbers suitable for grading an LLM's computational reasoning.

**Needs:** 2-3 real charter exhibits or 8-K Item 1.01 excerpts that show a down-round scenario with:
- Explicit statement of prior round's conversion price
- Explicit statement of new round's lower price
- Explicit statement of the resulting adjusted conversion price
OR a cap-table or financial statement that includes historical round data that can be cross-checked against the charter's stated terms.

**Recommendation:** Source is not available in the current corpus. Defer or source from a different corpus (e.g., detailed proxy statements or S-4s that recap historical cap tables).

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.

---

**Follow-up audit (2026-07-02):** Re-attempted sourcing per Eikiyo's "finish all 22 pending"
directive. Found a real, complete, worked "conversion price was adjusted from $X to $Y"
example -- Great Basin Scientific, Inc. 8-K (2016-08-08, CIK 1512138): "The conversion price
was adjusted from $1.34 to $0.47" and a second adjustment "from $0.47 to $0.39". Real,
concrete, verified numbers. HOWEVER: on inspection this is a variable-rate/toxic convertible
note whose conversion price resets to a MARKET-PRICE FORMULA at each amortization date, not a
fixed-price VC preferred-stock full-ratchet anti-dilution adjustment triggered by a NEW
PRICED ROUND. There is no "prior round price vs. new round price" comparison here -- the
adjustment mechanism is fundamentally different from the task's intended VC financing
construct (a market-price convertible note reset would test a different, potentially
uncomputable-from-the-document skill: reproducing an external market-price lookup, not
applying a stated ratchet formula). Using it would risk the same
`keyword-is-candidate-not-oracle` task-design mismatch already caught twice this session.
Not used; remains deferred.
