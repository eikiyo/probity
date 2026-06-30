"""
Location: leaves/acceleration_trigger/task.py
Purpose: Leaf 6.3 — classify an equity-award / employment-agreement acceleration provision as
         single-trigger or double-trigger. Single enum; the model reads the real provision and maps
         the mechanic (does a change of control ALONE accelerate, or is termination also required?).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a startup-equity lawyer. Read the vesting-acceleration provision below and classify "
    "whether the acceleration is SINGLE-TRIGGER or DOUBLE-TRIGGER."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"single-trigger\": the equity vesting accelerates upon a CHANGE OF CONTROL ALONE (a sale / "
    "merger / corporate transaction). No termination of employment is required — the change of "
    "control by itself triggers the acceleration. Tell-tale: 'upon a Change in Control, [X%] shall "
    "vest', acceleration 'effective immediately prior to the Change in Control', no termination "
    "condition.\n"
    "- \"double-trigger\": the vesting accelerates ONLY IF TWO things both happen — a change of "
    "control AND (usually within a stated window after it) an involuntary termination of employment "
    "without Cause or a resignation for Good Reason. The change of control alone is NOT enough. "
    "Tell-tale: 'if, within 12 months following a Change in Control, the executive is terminated "
    "without Cause or resigns for Good Reason', 'Involuntary Termination ... after that Change in "
    "Control'.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"acceleration_trigger": "single-trigger" | "double-trigger"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nACCELERATION PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "acceleration_trigger",
    "description": "Classify equity vesting acceleration as single-trigger or double-trigger (6.3).",
    "fields": {"acceleration_trigger": {"type": "enum", "values": ["single-trigger", "double-trigger"],
               "description": "Whether vesting acceleration is single-trigger or double-trigger."}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
