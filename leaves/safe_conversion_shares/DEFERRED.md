# safe_conversion_shares — Deferred Build

**Reason:** Conversion-share computation requires cap-table data not cleanly paired with SAFE documents.

**What was tried:**
- Checked existing safe_valuation_cap and safe_discount_rate leaves (17 SAFEs across both)
- Reviewed SAFE mechanics: shares = purchase_amount / (cap / fully_diluted_shares_at_signing)
- Problem: SAFE documents state the valuation cap and investor purchase amount, but NOT the
  company's fully-diluted share count at the time of SAFE issuance
- Conversion share count cannot be computed without knowing either:
  1. Fully-diluted shares at SAFE signing date, OR
  2. Post-money valuation from a subsequent qualified financing
  
**Current status:** 0 items. **Deferred at 0/6-10 target.**

**Why sourcing is blocked:** SAFEs are issued early-stage (seed/pre-Series-A). Matching a SAFE
to a contemporaneous cap table or subsequent Series A document requires:
- Exact company name matching across multiple filing types (S-1, FORM D, 8-K exhibits)
- Chronological pairing (SAFE issue date → Series A closing date)
- Cap table exhibit that explicitly states shares outstanding at SAFE signing

This level of cross-document reconciliation is rare in public filings.

**Path to completion:** Could search SEC EDGAR for S-1 exhibits that mention SAFEs by name
(e.g., "Convertible SAFE issued [date]") with attached cap tables. Would require targeted
SEC EDGAR fetches + manual document matching. Estimated 40+ minutes with uncertain yield.

Deferred 2026-07-01.
