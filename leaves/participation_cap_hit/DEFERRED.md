# DEFERRED — participation_cap_hit leaf (4.5)

**Audit (2026-07-01):** Quick scan (5 min) — asks: does a participating preferred holder hit their cap and stop receiving additional proceeds?

Requires:
- Charter stating participation + cap (e.g., "2x cap")
- Liquidation preference multiple
- Exit value
- Computed payout to show whether cap is hit

**Finding:** No documents with all required pieces.

**Needs:** Documents with charter + exit value (S-4 most likely).

source.py/task.py/run.py kept as scaffolding; oracle.jsonl NOT generated.

---

**Follow-up audit (2026-07-02):** Re-attempted sourcing per Eikiyo's "finish all 22 pending"
directive. Tried a fresh document type not searched before: DEFM14A/merger-agreement exhibits
(EDGAR FTS for "Series A Per Share Merger Consideration"). Found a real, on-point candidate --
Ulthera, Inc.'s acquisition of Cabochon Aesthetics, Inc. (2014 Agreement and Plan of Merger,
CIK 1345889) -- with real defined terms for Series A/B/C Per Share Merger Consideration.
However, the agreement's actual formula routes all real dollar amounts through a referenced
"Consideration Spreadsheet" exhibit, which is NOT itself part of the publicly filed document
(private M&A allocation spreadsheets are customarily prepared and distributed to
stockholders directly, not filed with the SEC). This confirms the original finding structurally:
real M&A agreements disclose the waterfall MECHANISM but not concrete numbers inline; the
worked numbers live in an unfilled/unfiled exhibit. Remains a genuine sourcing wall.
