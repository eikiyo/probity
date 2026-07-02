"""
Location: leaves/preference_stack_payout/task.py
Purpose: Leaf 4.3 -- compute a NAMED preferred series' total payout through the liquidation
         waterfall (base liquidation preference + accrued dividends) from real fairness-opinion
         figures (op CO=compute, stakes 4). Sourced from the same real Connecture, Inc. SC 13E-3
         fairness opinion as the sibling liquidation_waterfall_payout leaf. The target series is
         named explicitly in the window (runner only passes {id, document} through).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are an M&A analyst. Read the real fairness-opinion figures below. Compute the TARGET "
    "SERIES' total payout in the liquidation waterfall: its liquidation preference PLUS its "
    "accrued dividends."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"preference_stack_payout": <decimal>}\n'
    'where decimal is the total payout in $ millions (e.g., 58.9).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nFAIRNESS OPINION FIGURES:\n{clause}\n\nJSON:"


TASK = {
    "name": "preference_stack_payout",
    "description": "Compute a named preferred series' total payout (preference + accrued dividends) (4.3).",
    "fields": {
        "preference_stack_payout": {
            "type": "number",
            "op": "CO",
            "description": "target series' liquidation preference plus accrued dividends, in $ millions"
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
