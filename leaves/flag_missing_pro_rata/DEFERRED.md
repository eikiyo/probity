# flag_missing_pro_rata — DEFERRED (ref 8.5, type: bool, op: FL=flag)

**Status:** Deferred pending verification that "grants pro-rata" and "denies pro-rata" are not the same boilerplate clause.

**Task Definition:**

Flag whether a real financing document **EXPLICITLY** grants pro-rata investment rights to an investor (false = pro-rata IS granted) or **EXPLICITLY** omits/denies them (true = pro-rata IS MISSING).

**Critical Constraint from Earlier Session Failure:**

Earlier this session, a similar flag task hit a documented failure: *a modern YC SAFE's "Includes X / Excludes X" bullets looked like two classes but were actually one universal clause appearing in every document*. This rendered the binary classification invalid — there was no true distinction between the two classes.

**Sourcing Status:**

Existing pro_rata_rights corpus (75 documents) contains documents classified as "yes" (pro-rata present) but:
1. **No parallel "no" class** with documents that explicitly DENY pro-rata rights.
2. **Unclear whether explicit denial exists** vs. silence/absence-by-omission (which the task explicitly excludes: "not silence/absence-by-omission, which is not gradeable").

**Boilerplate Trap Check Required:**

Before building, must verify:
1. **Sample 10-15 documents** that claim to "include" pro-rata rights.
2. **Sample 10-15 documents** that claim to "exclude" pro-rata rights (if findable).
3. **Compare the language** — are the "Includes" and "Excludes" sections on the SAME page/clause with identical boilerplate?
4. **If yes:** The binary task is unsolvable; one universal clause with conditional bullets. Recommend re-scoping to a different task (e.g., "pro-rata present vs. absent", not "explicitly granted vs. explicitly denied").

**Recommendation:**

Defer until a dedicated audited pass can:
1. **Verify that "explicitly grant" and "explicitly deny" classes exist** as DISTINCT documents/clauses, not as two branches of one universal template.
2. **Build 8-12 clean items** at high confidence, with real company names and real validating_quotes from real documents.

**0 items, 0 oracle records** — honest deferred status pending boilerplate-trap verification.

**Orchestrator follow-up (2026-07-01):** grepped all 75 real fetched documents in
`leaves/pro_rata_rights/corpus/full/` for explicit-denial language (`no pro.rata`, `not
entitled to.*pro.rata`, `waive.*pro.rata`, `does not (have|grant|include).*pro.rata`) — zero
matches. Confirms: this corpus (sourced to find pro-rata GRANTS) contains no explicit-denial
counterexamples, and explicit denial of a right that could simply be absent-by-omission is
inherently rare in real financing documents (parties don't usually write clauses to state a
right they're NOT giving). A real "no" class would need a dedicated EDGAR FTS pass for denial
phrasing specifically, separate from the existing grant-oriented corpus.
