"""
Location: leaves/participation_cap/task.py
Purpose: Leaf 1.3.3 -- extract the NUMBER (cap multiple) for a capped participating-preferred clause
         from a liquidation/distribution section of a Shareholders' Agreement, Charter, or Certificate
         of Incorporation. NUMBER extraction: the model outputs a bare number like 3 or 2.5.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the NUMBER of "
    "times the Original Issue Price at which the preferred stockholders' participation rights are capped. "
    "This is a capped participating-preferred clause where the preferred stockholders participate in "
    "distributions beyond their liquidation preference, but only up to a maximum multiple of the Original Issue Price."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"participation_cap": <bare number>}\n'
    '\n'
    'Example: if the clause says "up to three (3) times the Original Issue Price", respond {"participation_cap": 3}\n'
    'Example: if the clause says "capped at 3.5x OIP", respond {"participation_cap": 3.5}\n'
    'Do NOT include an "x" suffix or any other text.'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "participation_cap",
    "description": "Extract the cap multiple for a capped participating-preferred clause (1.3.3).",
    "fields": {"participation_cap": {"type": "number", "op": "EX",
               "description": "the numeric cap multiple (e.g., 3 or 2.5) for the preferred stock's participation rights"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
