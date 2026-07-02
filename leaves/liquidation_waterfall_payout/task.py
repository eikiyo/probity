"""
Location: leaves/liquidation_waterfall_payout/task.py
Purpose: Leaf 4.1 -- compute the per-share value remaining for common stockholders after a
         real multi-series preferred stock liquidation waterfall (op CO=compute, stakes 5).
         Sourced from a real SC 13E-3 going-private fairness opinion (Connecture, Inc., 2018 --
         the document itself uses the internal deal codename "Cure" throughout; the real filer
         is confirmed via SEC EDGAR CIK 1211759 = CONNECTURE INC. This is normal confidentiality
         practice in banker fairness-opinion decks, not a data error -- see source.py for detail).
         The source document discloses a full real bridge: Total Enterprise Value -> minus
         Severance -> minus Debt -> minus total Preferred Stock liquidation preference (Series A
         + Series B + accrued dividends) -> Total Equity Value -> divided by shares outstanding
         -> per-share value to common. Formula: (enterprise_value - severance - debt -
         preferred_liquidation) / shares_outstanding.
Functions: build_prompt(), TASK
Calls: engine/runner.py (via run.py shim) -- build_prompt() is invoked once per (instance, run)
       pair inside harness._execute_run(); TASK is read once by runner._load_task() to discover
       the field name/type and the prompt builder.

WHY this leaf exists (the "so what"): this is the single hardest compute task in the benchmark
(stakes=5) -- it requires the model to hold 5 real numbers in context AND correctly apply a
4-step subtraction-then-division formula, rather than just extracting one stated fact. It is the
leaf with the widest observed model gap in the whole suite: gemma3:1b scores 0% accuracy / 100%
wobble (cannot reliably do the arithmetic at all), deepseek-v4-flash scores high accuracy on the
runs that actually complete (see the KNOWN ISSUE below -- a meaningful slice of "failures" here
are DeepSeek API 503s, not reasoning failures). That gap is the empirical proof point for this
whole benchmark's thesis: model size/tier matters MORE for multi-step financial computation than
for single-fact extraction.

KNOWN ISSUE (found on adversarial audit, 2026-07-02, not yet fixed -- see vault/mistakes.md):
this leaf's DeepSeek run showed a 22.5% "parse failure" rate (18/80 runs), of which 17/18 (94%)
were verified to be raw `HTTP 503 Service Unavailable` from the DeepSeek API itself (engine/
models.py's DeepSeekClient has no retry logic on transient errors), NOT genuine model reasoning
or JSON-formatting failures. The published wobble/consistency/accuracy numbers in scored.json and
the README do not currently disclose this parse-failure rate at all (results/render.py never
surfaces engine/scorer.py's own parse_failure_rate field) -- so a reader sees "100% accuracy, 99%
consistency" with no visibility into the fact that DeepSeek silently failed to answer on nearly 1
in 4 attempts. This is a project-wide gap (same root cause found on 4 other leaves), tracked for
a fix; anyone re-running this leaf should expect the deepseek numbers to shift once the retry
logic + parse_failure_rate reporting are fixed.
"""

_SYSTEM = (
    "You are an M&A analyst. Read the real fairness-opinion figures below (in $ millions except "
    "shares and per-share). Compute the resulting per-share value to common stockholders after "
    "the full liquidation waterfall: (Total Enterprise Value - Severance Payment - Total Debt - "
    "Preferred Stock Liquidation Preference) / Shares Outstanding."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"liquidation_waterfall_payout": <decimal>}\n'
    'where decimal is the per-share dollar value (e.g., 0.51).\n'
)


def build_prompt(instance: dict) -> str:
    """
    What: assembles the exact text sent to the model for one benchmark item.
    Why: the harness calls this once per (instance, run) pair -- keeping prompt construction
         here (not inline in the harness) means every leaf can have its own system framing
         and instruction wording while the harness/runner code stays leaf-agnostic (reuse-first).
    Input: instance -- a dict with key "document" holding this item's real-document text window
           (built once by source.py and cached to corpus/questions/<id>.txt).
    Output: a single string -- system framing + JSON-only instruction + the real document window
            + a trailing "JSON:" cue to bias the model toward emitting JSON immediately.
    Success criteria: the returned prompt, when sent to a capable model, should be answerable
            SOLELY from the numbers in `clause` -- no external knowledge or the model's own
            training-data memory of this real M&A deal should be needed (verified in source.py's
            build: the window never contains the disclosed per-share answer itself).
    """
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nFAIRNESS OPINION FIGURES:\n{clause}\n\nJSON:"


# TASK is the leaf's public contract with engine/runner.py -- runner._load_task() reads this
# dict directly (via importlib) to learn: what field to score ("fields"), what TYPE that field
# is (drives which normalize.canonical() branch + which scorer._SCORABLE check applies), and
# which function builds the prompt. Any leaf that wants to plug into the shared runner/scorer/
# harness MUST expose exactly this shape -- this is the leaf/engine interface contract.
TASK = {
    "name": "liquidation_waterfall_payout",
    "description": "Compute per-share value to common after a real multi-series preferred liquidation waterfall (4.1, stakes=5).",
    "fields": {
        "liquidation_waterfall_payout": {
            "type": "number",
            "op": "CO",  # CO = compute: the model must derive this value, it is never stated verbatim in the prompt.
            "description": "per-share value to common stockholders, as a bare decimal"
        }
    },
    "stakes_weight": 5,  # 1-5 scale, project-wide convention: 5 = hardest/most consequential leaf class.
    "build_prompt": build_prompt,
}
