"""
Location: leaves/note_qualified_financing_threshold/task.py
Purpose: Leaf 2.2.6 -- extract the minimum aggregate dollar amount of a "Qualified Financing"
         on a convertible promissory note as a bare number.
         NUMBER extraction (not yes/no): the model outputs a plain number (dollars, e.g. 10000000, 40000000).
Functions: build_prompt(), TASK
Calls: engine.task_builder.build_standard_prompt
Imports: sys, pathlib
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from task_builder import build_standard_prompt  # noqa: E402

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the minimum aggregate "
    "dollar amount that qualifies as a 'Qualified Financing' triggering automatic conversion of the convertible "
    "promissory note, as a bare number (numeric dollars only, no $ sign, no commas, no text — e.g., '10000000' or '40000000')."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"note_qualified_financing_threshold": <number>}\n'
)


def build_prompt(instance: dict) -> str:
    return build_standard_prompt(_SYSTEM, _INSTRUCTION, instance)


TASK = {
    "name": "note_qualified_financing_threshold",
    "description": "Extract the minimum aggregate dollar amount for Qualified Financing of a convertible promissory note (2.2.6).",
    "fields": {"note_qualified_financing_threshold": {"type": "number", "op": "EX",
               "description": "the minimum aggregate dollar amount that qualifies as a Qualified Financing on a convertible promissory note"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
