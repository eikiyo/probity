# flag_founder_hostile_vesting — DEFERRED (ref 8.4, type: bool, op: FL=flag)

**Status:** Deferred pending hand-verified sourcing of founder-hostile vs. standard vesting documents.

**Task Definition:**

Flag whether a real vesting/equity-award document's terms are "founder-hostile" (true) or standard/founder-friendly (false).

**Hostile Indicators:**
- No acceleration on termination-without-cause
- Unusually long cliffs re-imposed on refresh grants
- Board-discretion clawback of vested shares
- Forfeiture of vested shares on termination

**Standard/Friendly Indicators:**
- Single-trigger or double-trigger acceleration on termination
- Typical 4-year vest with 1-year cliff
- No clawback provisions
- Retained vesting credit for partial service

**Sourcing Challenge:**

While abundant vesting documents exist in existing corpora:
- `leaves/vesting_acceleration/` (114 docs)
- `leaves/acceleration_trigger/` (24 docs)
- `leaves/cliff_present/` (54 docs)

**None were hand-read and classified** for the specific hostile-vs.-friendly distinction required by this leaf. This is a **binary classification task** that requires careful oracle work:

1. Read each source document (or window extract).
2. Hand-classify as hostile or standard based on the criteria above.
3. Extract a validating_quote substring proving the classification.
4. Verify the quote is a real substring in the source document (no paraphrase).

A premature build with unverified items risks:
- Misclassification (a document with both hostile AND friendly terms assigned to the wrong class).
- Boilerplate trap (a "universal clause" that appears in both hostile and standard documents, making the classification invalid).
- False validating_quotes (invented language that matches no real source).

**Recommendation:**

Defer until a dedicated hand-read pass can:
1. **Sample 20-30 documents** from the existing corpora.
2. **Classify each document** against the hostile-vs.-friendly rubric.
3. **Identify boilerplate collisions** (do "hostile" and "standard" candidates use the same language?).
4. Build 8-12 clean, non-boilerplate items with real validating_quotes.

**0 items, 0 oracle records** — honest deferred status until sourcing can verify the binary task is solvable.
