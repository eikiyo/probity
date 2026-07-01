# exercise_window — DEFERRED (ref 6.5, type: string, op: EX=extract)

**Status:** Deferred pending rich sourcing of post-termination option exercise windows.

**Sourcing Challenge:**

Post-termination option exercise windows (e.g., "90 days", "12 months", "until the option's original expiration date") are a specific, fact-dense extraction target that requires:

1. **Real SEC-filed equity award / stock option plan documents** containing explicit exercise period language (not just vesting schedules or acceleration terms).
2. **Clear, standalone statements** of the post-termination window (e.g., "following termination, the employee shall have ninety (90) days to exercise any vested options").
3. **High-confidence hand-verified oracle data** — extracting the window from the real document and validating it matches the actual language.

**Reuse-First Check:**

Searched existing corpora:
- `leaves/vesting_acceleration/` (114 docs) — contains termination acceleration language, NOT post-termination exercise windows.
- `leaves/acceleration_trigger/` (24 docs) — double-trigger and single-trigger acceleration, NOT exercise windows.
- `leaves/cliff_present/` (54 docs) — cliff presence/absence, NOT exercise windows.

None contain focused exercise window language suitable for clean extraction items.

**Honest Assessment:**

- Fetching fresh EDGAR documents for option plans would require multi-document crawl + careful manual hand-verification of each window claim (fabrication risk is high if rushed).
- A 3-item leaf built hastily with real but unverified documents defeats the oracle layer's purpose (Guardrail #1: every validating_quote must be a real substring).

**Recommendation:**

Defer until a future pass can:
1. **Batch-fetch real stock option plans** from SEC EDGAR (FTS search: "option plan" + "exercise" + "termination").
2. **Hand-verify each oracle item** by re-grepping the validating_quote against the raw fetched document.
3. Build with 8-12 clean items at high confidence.

**0 items, 0 oracle records** — this leaf will be added in a future Probity session with rich sourcing.

**Orchestrator follow-up (2026-07-01):** ran 3 EDGAR FTS phrase searches ("days following your
termination of Continuous Service", "days after the date of such termination to exercise",
"post-termination exercise period") and fetched+checked 6 real candidate documents (PROS
Holdings, ZARS Pharma, GCM Grosvenor, Autodesk, Zoetis, plus the ServiceSource hit) for a stated
exercise-window duration. None contained a clean, standalone post-termination exercise-window
statement — hits were either 83(b)-election deadlines (unrelated), lockup periods (unrelated),
or the phrase appeared only in a definitions cross-reference with no stated number. Confirms
the deferral; a real batch-fetch pass (dozens of candidates, not a handful) would likely be
needed to find enough clean, on-topic items.
