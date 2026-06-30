"""
Location: leaves/note_principal/task.py
Purpose: Leaf 2.2.1 -- extract the PRINCIPAL AMOUNT of a convertible promissory note as a bare dollar number.
         NUMBER extraction (not yes/no): the model outputs an integer.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the PRINCIPAL AMOUNT "
    "of the convertible promissory note, as a bare dollar number (integer only, no dollar sign, no commas)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"note_principal": <integer>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "note_principal",
    "description": "Extract the principal amount of a convertible promissory note (2.2.1).",
    "fields": {"note_principal": {"type": "number", "op": "EX",
               "description": "the principal amount of the convertible promissory note as a bare integer"}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
