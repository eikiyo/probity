"""
Location: leaves/dividend_rate_pct/task.py
Purpose: Leaf 1.4.1 -- extract the ANNUAL DIVIDEND RATE PERCENTAGE stated in a preferred-stock
         charter's dividend clause. NUMBER extraction (not yes/no): the model outputs a bare number
         with NO percent sign (e.g. 8 or 8.5, never "8%").
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the ANNUAL "
    "DIVIDEND RATE PERCENTAGE stated in the preferred stock charter's dividend clause."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"dividend_rate_pct": <number>}\n'
    '\nRespond with ONLY the number (e.g. 8 or 8.5), with NO percent sign and NO other text.'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "dividend_rate_pct",
    "description": "Extract the annual dividend rate percentage from preferred stock charter (1.4.1).",
    "fields": {"dividend_rate_pct": {"type": "number", "op": "EX",
               "description": "the annual dividend rate percentage (e.g. 8 or 8.5, no % sign)"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
