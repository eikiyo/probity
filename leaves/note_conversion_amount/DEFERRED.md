# note_conversion_amount — Deferred Build

**Reason:** Conversion computation requires data not cleanly stated in individual notes.

**What was tried:**
- Checked existing note_principal corpus (7 convertible notes)
- Reviewed note_discount, note_valuation_cap leaves for conversion mechanics
- Found conversion-price formulas (e.g., "50% of current market price") but not executable:
  * Acology: "50% of Current Market Price" — requires knowing market price at conversion date (not in note)
  * Most notes with valuation caps lack the fully-diluted share count or qualified-financing price needed to compute resulting shares
  * Many notes rely on future VACP (Valuation Cap) + Qualified Financing price (not known until financing closes)

**Current status:** 0 items. **Deferred at 0/6-10 target.**

**Why full-corpus sourcing is hard:** Conversion-amount computation requires either:
1. A note + a fully-diluted cap-table showing shares at signing, OR
2. A note + subsequent financing document showing the qualified-financing price per share

These pairs are rare in SEC filings (notes often precede equity documents by months). Would require matching note IDs across multiple document types/filings.

**Path to completion:** Could search for founder/angel convertible notes (likely to have smaller cap tables) or find pairs of FORM D + S-1 exhibits covering the same note. Estimated effort: 30+ minutes with uncertain success rate.

Deferred 2026-07-01.
