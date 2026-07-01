"""
Location: leaves/price_per_share/task.py
Purpose: Leaf 1.1.3 -- extract the PRICE PER SHARE of preferred stock
         in a priced equity financing round as a bare decimal number.
         NUMBER extraction (not yes/no): the model outputs a decimal.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the PRICE PER SHARE "
    "of the preferred stock in the financing round, as a bare decimal number (e.g., 2.4384, no dollar sign, no commas)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"price_per_share": <decimal>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "price_per_share",
    "description": "Extract the price per share of preferred stock in a financing round (1.1.3).",
    "fields": {"price_per_share": {"type": "number", "op": "EX",
               "description": "the price per share of preferred stock as a bare decimal"}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
