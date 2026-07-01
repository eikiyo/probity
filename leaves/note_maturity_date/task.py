"""
Location: leaves/note_maturity_date/task.py
Purpose: Leaf 2.2.3 -- extract the MATURITY DATE of a convertible promissory note as an ISO date.
         DATE extraction (not yes/no): the model outputs an ISO date string YYYY-MM-DD.
Functions: build_prompt(), TASK
Calls: engine.task_builder.build_standard_prompt
Imports: sys, pathlib
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from task_builder import build_standard_prompt  # noqa: E402

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the MATURITY DATE "
    "of the convertible promissory note. The maturity date is the date on which the note is due and payable if not "
    "converted or extended. Return the date as an ISO date string (YYYY-MM-DD) if a specific calendar date is stated. "
    "If the date is relative or computed (e.g., '60 months from the Closing Date'), return the literal text as stated in the document."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"note_maturity_date": "<ISO date YYYY-MM-DD or literal relative date text>"}\n'
)


def build_prompt(instance: dict) -> str:
    return build_standard_prompt(_SYSTEM, _INSTRUCTION, instance)


TASK = {
    "name": "note_maturity_date",
    "description": "Extract the maturity date of a convertible promissory note (2.2.3).",
    "fields": {"note_maturity_date": {"type": "date", "op": "EX",
               "description": "the maturity date of the convertible promissory note as ISO date (YYYY-MM-DD) if explicit, or literal text if relative"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
