"""
Location: leaves/dividend_cumulative/task.py
Purpose: Leaf 1.4.2 — classify a preferred-stock charter's DIVIDEND clause as cumulative or
         non-cumulative. Single enum; the model reads the real dividend article and maps it.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock DIVIDEND provision below and "
    "classify whether the preferred dividends are CUMULATIVE or NON-CUMULATIVE."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"cumulative\": unpaid preferred dividends ACCRUE and carry forward whether or not the board "
    "declares them — they accumulate and must be paid (often with the liquidation preference or on "
    "conversion) before common gets anything. Tell-tale language: dividends 'shall accrue', 'whether "
    "or not declared', 'shall be cumulative', accruing daily/annually regardless of declaration.\n"
    "- \"non-cumulative\": preferred dividends are payable ONLY WHEN, AS AND IF DECLARED by the board; "
    "if the board does not declare a dividend in a period, no dividend accrues for that period and it "
    "is gone. Tell-tale language: 'non-cumulative', 'shall not be cumulative', 'when, as and if "
    "declared', 'no right to any accrued or accumulated dividends'.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"dividend_cumulative": "cumulative" | "non-cumulative"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDIVIDEND PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "dividend_cumulative",
    "description": "Classify preferred-stock dividends as cumulative or non-cumulative (1.4.2).",
    "fields": {"dividend_cumulative": {"type": "enum", "values": ["cumulative", "non-cumulative"],
               "description": "Whether preferred dividends are cumulative or non-cumulative."}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
