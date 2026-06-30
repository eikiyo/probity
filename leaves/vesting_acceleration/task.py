"""
Location: leaves/vesting_acceleration/task.py
Purpose: Leaf 5.7 -- classify whether a document grants ACCELERATION OF VESTING upon a specified
         trigger (termination without cause, resignation for good reason, change of control) -- i.e.
         unvested shares/options vest faster than the normal schedule -- or does NOT.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether it "
    "grants ACCELERATION OF VESTING upon a specified trigger, or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the excerpt grants the holder accelerated vesting upon a trigger (termination without "
    "cause, resignation for good reason, change of control/single-trigger, double-trigger) -- unvested "
    "shares/options vest faster than the normal schedule because of that event.\n"
    "- \"no\": the excerpt does NOT grant this -- a fixed vesting schedule with no acceleration "
    "language, or an explicit statement that no accelerated vesting occurs.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"vesting_acceleration": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "vesting_acceleration",
    "description": "Classify whether a document grants accelerated vesting upon a trigger (5.7).",
    "fields": {"vesting_acceleration": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if accelerated vesting on a trigger is granted, else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
