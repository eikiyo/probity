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

---

**Follow-up audit (2026-07-02, broader-search round):** Per Eikiyo's explicit pushback ("did you
check public companies? there are thousands") did a much wider EDGAR search across SC 13E-3
going-private fairness opinions, DEFM14A merger proxies, and DEF 14C information statements --
this round DID succeed for 3 sibling exit_waterfall leaves (liquidation_waterfall_payout,
preference_stack_payout via Connecture Inc.'s real fairness opinion; convert_vs_preference_decision
via a real WeFunder Agreement for Future Equity worked example). For THIS leaf specifically:
found real companies with genuine multi-series "participating preferred" cap tables (Cogent
Communications Group's DEF 14C: Series G-1 through G-13, K, L Participating Convertible
Preferred Stock) and real fairness-opinion dollar bridges (Connecture) -- but never BOTH in the
same document. Fairness opinions net out ALL preferred as one combined liquidation-preference
deduction (never splitting out which series are participating vs non-participating, or what
their post-preference participation adds); charters/DEF 14C filings state the participating
mechanism in full legal detail but never attach a worked numeric example of the resulting
payout split. Confirmed as a real, still-standing gap after broader search, not narrow-search
laziness.
