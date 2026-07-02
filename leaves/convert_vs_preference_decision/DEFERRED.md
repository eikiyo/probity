# DEFERRED — convert_vs_preference_decision leaf (4.4)

**Audit (2026-07-01):** Quick scan (5 min) — this leaf asks: should a holder convert to common or take their preference in an exit scenario?

The decision depends on:
- Preference multiple (from charter)
- As-converted ownership % (from cap table)
- Exit price (from transaction)
- Computed payouts under each path

**Finding:** No documents found that state all four pieces of data needed to make this decision and verify the answer.

**Needs:** Documents showing charter + cap table + exit price (S-4 is most likely).

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
