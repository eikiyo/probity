"""
Location: leaves/safe_valuation_cap/task.py
Purpose: Leaf 2.1.1 -- extract the VALUATION CAP (bare dollar number) from a YC-style SAFE
         (Simple Agreement for Future Equity). NUMBER-type field: model outputs an integer.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the SAFE document excerpt below and extract the "
    "VALUATION CAP as stated (the cap on the valuation at which the SAFE converts). "
    "Respond with ONLY the bare dollar number, no $ sign, no commas, no decimals."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"safe_valuation_cap": <integer>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "safe_valuation_cap",
    "description": "Extract the valuation cap from a SAFE agreement (2.1.1)",
    "fields": {"safe_valuation_cap": {"type": "number", "op": "EX",
               "description": "the valuation cap in dollars as a bare integer (no $ or commas)"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
