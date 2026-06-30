"""
Location: leaves/note_valuation_cap/task.py
Purpose: Leaf 2.2.4 -- extract the valuation cap (conversion ceiling in dollars) stated in a
         convertible promissory note. NUMBER extraction: the model outputs a bare integer.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the convertible promissory note excerpt below and "
    "extract the VALUATION CAP — the company valuation ceiling used to set the note's conversion "
    "price into equity shares."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"note_valuation_cap": <integer>}\n'
    'where <integer> is the bare dollar number (no $ sign, no commas). If no valuation cap is stated, respond with \n'
    '{"note_valuation_cap": null}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "note_valuation_cap",
    "description": "Extract the valuation cap dollar amount from a convertible promissory note (2.2.4).",
    "fields": {"note_valuation_cap": {"type": "number", "op": "EX",
               "description": "the valuation cap (conversion ceiling) stated in the note, as a bare dollar number"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
