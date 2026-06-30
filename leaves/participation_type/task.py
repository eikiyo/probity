"""
Location: leaves/participation_type/task.py
Purpose: Leaf 1.3.2 — classify a preferred-stock liquidation provision's participation type.
         Single enum field; prompt gives the standard textbook taxonomy, the model must read the
         real clause and map it. Compatible with engine/harness.run_harness (task-dict API).
Functions: build_prompt(), TASK
Calls: (none)
Imports: (none)
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock liquidation provision below "
    "and classify how the preferred stock participates in liquidation proceeds."
)

_TAXONOMY = (
    "Classify into exactly one of these standard categories:\n"
    "- \"non-participating\": the preferred receives the GREATER OF (a) its liquidation preference "
    "OR (b) the amount it would get by converting to common — one or the other, not both.\n"
    "- \"participating\": the preferred receives its liquidation preference AND THEN ALSO shares "
    "the remaining assets together with the common stock (on an as-converted basis) — it double-dips.\n"
    "- \"capped\": participating, but the preferred's total take is limited to a stated cap "
    "(e.g. a multiple of the original issue price, or a 'Maximum Participation Amount').\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"participation_type": "non-participating" | "participating" | "capped"}\n'
)


def build_prompt(instance: dict) -> str:
    """Stable prefix (system + taxonomy + instruction) then the clause tail."""
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nLIQUIDATION PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "participation_type",
    "description": "Classify preferred-stock liquidation participation (1.3.2).",
    "fields": {
        "participation_type": {
            "type": "enum",
            "values": ["participating", "non-participating", "capped"],
            "description": "How the preferred participates in liquidation proceeds.",
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
