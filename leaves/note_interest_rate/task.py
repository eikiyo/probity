"""
Location: leaves/note_interest_rate/task.py
Purpose: Leaf 2.2.2 -- extract the ANNUAL INTEREST RATE of a convertible promissory note as a bare number.
         NUMBER extraction (not yes/no): the model outputs a plain number (percentage points, e.g. 6.0, 12.0).
Functions: build_prompt(), TASK
Calls: engine.task_builder.build_standard_prompt
Imports: sys, pathlib
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from task_builder import build_standard_prompt  # noqa: E402

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the ANNUAL INTEREST RATE "
    "of the convertible promissory note, as a bare number (numeric percentage only, no % sign, no text — e.g., '6.0' or '12.0')."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"note_interest_rate": <number>}\n'
)


def build_prompt(instance: dict) -> str:
    return build_standard_prompt(_SYSTEM, _INSTRUCTION, instance)


TASK = {
    "name": "note_interest_rate",
    "description": "Extract the annual interest rate of a convertible promissory note (2.2.2).",
    "fields": {"note_interest_rate": {"type": "number", "op": "EX",
               "description": "the annual interest rate of the convertible promissory note as a bare number (percentage points)"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
