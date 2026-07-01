# DEFERRED — safe_note_conversion_impact leaf (3.5)

**Audit (2026-07-01):** Quick scan (5 min) of safe_valuation_cap corpus found SAFEs with valuation cap + discount rate mechanics, but no documents that show:
- A real SAFE note with specific cap/discount
- A real priced round with announced price per share
- The resulting conversion shares, stated in the document

**Finding:** SAFE mechanics describe the *formula* (valuation cap vs discount), but concrete worked examples of conversion impact (e.g., "SAFE cap was $10M, priced round at $1M/$X per share, holder gets Y shares") are not present in the documents scanned.

**Needs:** 2-3 real documents showing both SAFE terms AND the priced round's outcome with stated conversion shares.

Alternative sources: S-1s of post-SAFE-funded companies (Canva, Stripe, etc. if public filings exist) that may recap SAFE conversions in the capitalization section.

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.
