"""
Location: leaves/safe_discount_rate/task.py
Purpose: Leaf 2.1.2 -- extract the DISCOUNT RATE percentage stated in a YC-style SAFE as a bare number.
         If the SAFE states "100 minus 50%", extract 50. If it states "Discount Rate is 80%"
         (representing 20% discount), extract 20. NUMBER extraction: the model outputs an integer.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the DISCOUNT RATE "
    "percentage from the SAFE (Simple Agreement for Future Equity). If the SAFE states a discount like "
    '\"the Discount Rate is 80% (representing a 20% discount)\", respond with the discount percentage itself (20, not 80). '
    'If it states \"Discount Rate is 100 minus 50%\", respond with 50. Respond with ONLY the bare percentage number, '
    "no % sign or text."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"safe_discount_rate": <integer>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "safe_discount_rate",
    "description": "Extract the discount rate percentage from a SAFE (2.1.2).",
    "fields": {"safe_discount_rate": {"type": "number", "op": "EX",
               "description": "the discount rate percentage stated in the SAFE"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
