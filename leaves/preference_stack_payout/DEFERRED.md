# DEFERRED — preference_stack_payout leaf (4.3)

**Audit (2026-07-01):** reviewed preference_seniority corpus (12 real docs classifying seniority as pari-passu or stacked) searching for items that state:
- A multi-series stack (Series A > Series B > common, with stated preference multiples)
- A real stated exit/liquidation value
- Enough data to compute one series' payout through the waterfall

**Finding:** Similar to participating_vs_nonpart_payout, the charters classify seniority correctly but do not include worked payout examples. The mechanics are stated ("Series A has priority, Series B has priority over common"), but not a concrete exit scenario with dollar amounts.

**Root cause:** As with leaf 4.2, payout calculations are computed at time of exit by management/legal, not pre-computed and disclosed in the charter itself.

**Needs:** 2-3 real documents (S-4s, proxy statements, or S-1s with cap-table exhibits) that show:
- Multi-series stack with stated preference multiples (from charter)
- A real stated or implied exit value (from M&A or IPO filings)

**Alternative:** Source from documents that include both charter terms and cap-table/exit data (S-4s are most likely to have this).

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
