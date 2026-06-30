"""
Location: leaves/conversion_ratio/task.py
Purpose: Leaf 1.6.1 -- extract the NUMBER representing the conversion ratio from a
         preferred-stock charter. How many shares of common stock each preferred share
         converts into. NUMBER extraction: model outputs only the bare number.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract "
    "the CONVERSION RATIO stated in the preferred-stock charter — how many shares of "
    "common stock each share of preferred stock converts into at issuance."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"conversion_ratio": <number>}\n'
    'Examples: 1, 1.5, 2\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "conversion_ratio",
    "description": "Extract the conversion ratio from a preferred-stock charter (1.6.1).",
    "fields": {"conversion_ratio": {"type": "number", "op": "EX",
               "description": "the conversion ratio (shares of common stock per preferred share at issuance)"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
