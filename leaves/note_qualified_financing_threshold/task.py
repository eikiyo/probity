"""
Location: leaves/note_qualified_financing_threshold/task.py
Purpose: Leaf 2.2.6 -- extract the minimum aggregate dollar amount of a "Qualified Financing"
         on a convertible promissory note as a bare number.
         NUMBER extraction (not yes/no): the model outputs a plain number (dollars).
Functions: build_prompt(), TASK
Calls: engine.task_builder.build_standard_prompt
Imports: sys, pathlib

WHY the worked examples were changed from 10000000/40000000 (added 2026-07-02, adversarial
audit): this leaf has only N=2 real items, and their true values are EXACTLY $10,000,000 and
$40,000,000 -- the same two numbers the original prompt used as its illustrative examples. That
meant a model could score 100% on this entire leaf by pattern-matching the prompt's own worked
examples without reading the document at all; the leaf carried near-zero true discriminative
signal. Swapped the examples to numbers that don't match either real item, removing the
confound. N=2 itself is still flagged separately in AUDIT_TODO.md as too small a sample to draw
real conclusions from -- that's a re-sourcing task, not fixable by a prompt edit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from task_builder import build_standard_prompt  # noqa: E402

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the minimum aggregate "
    "dollar amount that qualifies as a 'Qualified Financing' triggering automatic conversion of the convertible "
    "promissory note, as a bare number (numeric dollars only, no $ sign, no commas, no text — e.g., '15000000' or '75000000')."
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
