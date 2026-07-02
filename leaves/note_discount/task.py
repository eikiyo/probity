"""
Location: leaves/note_discount/task.py
Purpose: Leaf 2.2.5 -- extract the DISCOUNT RATE of a convertible promissory note as a bare number.
         NUMBER extraction (not yes/no): the model outputs a plain number (percentage points).
Functions: build_prompt(), TASK
Calls: engine.task_builder.build_standard_prompt
Imports: sys, pathlib

WHY the worked examples were changed from 20.0/25.0 to 33.0/62.5 (added 2026-07-02, adversarial
audit): the original prompt used "20%"/"25%" as its illustrative discount examples, and 2 of
the leaf's 4 real oracle items ARE 20.0 and 25.0 (a real coincidence, not contamination -- see
AUDIT_TODO.md). gemma3-1b answered "20.0" on ALL 4 items with 100% consistency each run,
including the 3 items whose true value was 50.0/5.0/25.0 -- a clean anchor-bias signature (it
latched onto the first example number regardless of document content). Swapped the worked
examples to numbers that don't match any real item in this corpus, removing the confound for
future reruns. Also fixed a genuine internal contradiction: the old _SYSTEM prompt told the
model to answer the literal string "NONE" for a no-discount note, while _INSTRUCTION told it to
use JSON null -- these directly conflicted. Neither of the leaf's 4 real items exercises the
no-discount path (all 4 have a real stated discount), so this was a real but never-triggered
bug; fixed by aligning both blocks on null. Archived pre-fix runs and reran both models.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from task_builder import build_standard_prompt  # noqa: E402

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the DISCOUNT RATE "
    "applied to the conversion price of a convertible promissory note. The discount is the percentage reduction "
    "from the price paid by new investors in the triggering financing (e.g., if the conversion price is 67% of "
    "the new financing price, the discount is 33%). Respond with ONLY a bare number (numeric percentage only, "
    "no % sign, no text — e.g., '33.0' or '62.5'). If there is no discount clause, respond with JSON null "
    "for the value (not a number, not the string \"NONE\")."
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
