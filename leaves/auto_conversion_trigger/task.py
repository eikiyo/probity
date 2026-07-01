"""
Location: leaves/auto_conversion_trigger/task.py
Purpose: Leaf 1.6.2 -- extract the NUMBER representing the QPO (Qualified Public Offering)
         threshold that AUTOMATICALLY triggers preferred-to-common stock conversion. This is
         the aggregate gross proceeds amount (in USD) stated in a charter's automatic
         conversion article.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract "
    "the QPO (Qualified Public Offering) threshold stated in the preferred-stock charter — "
    "the aggregate gross proceeds amount (in USD) that automatically converts all preferred "
    "stock to common stock. Do NOT extract a price-per-share threshold; extract only the "
    "AGGREGATE GROSS PROCEEDS dollar amount."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"auto_conversion_trigger": <number>}\n'
    'Examples: 30000000, 50000000, 100000000\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "auto_conversion_trigger",
    "description": "Extract the QPO (aggregate gross proceeds) threshold for automatic preferred-to-common conversion (1.6.2).",
    "fields": {"auto_conversion_trigger": {"type": "number", "op": "EX",
               "description": "the USD amount (aggregate gross proceeds) that triggers automatic conversion"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
