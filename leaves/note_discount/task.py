"""
Location: leaves/note_discount/task.py
Purpose: Leaf 2.2.5 -- extract the DISCOUNT RATE of a convertible promissory note as a bare number.
         NUMBER extraction (not yes/no): the model outputs a plain number (percentage points, e.g. 20.0, 25.0).
         This discount is applied to the conversion price: a "multiplied by 0.80" clause means
         a 20% discount; a "multiplied by 0.75" clause means a 25% discount.
Functions: build_prompt(), TASK
Calls: engine.task_builder.build_standard_prompt
Imports: sys, pathlib
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from task_builder import build_standard_prompt  # noqa: E402

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the DISCOUNT RATE "
    "applied to the conversion price of a convertible promissory note. The discount is the percentage reduction "
    "from the price paid by new investors in the triggering financing (e.g., if the conversion price is 80% of "
    "the new financing price, the discount is 20%). Respond with ONLY a bare number (numeric percentage only, "
    "no % sign, no text — e.g., '20.0' or '25.0'). If there is no discount clause, respond with the word "
    "'NONE' (not a number)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"note_discount": <number or null>}\n'
    'If no discount exists, use null (not the string "NONE").\n'
)


def build_prompt(instance: dict) -> str:
    return build_standard_prompt(_SYSTEM, _INSTRUCTION, instance)


TASK = {
    "name": "note_discount",
    "description": "Extract the discount rate applied to equity conversion of a convertible promissory note (2.2.5).",
    "fields": {"note_discount": {"type": "number", "op": "EX",
               "description": "the discount rate (as a percentage) applied to the conversion price of a convertible promissory note"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
