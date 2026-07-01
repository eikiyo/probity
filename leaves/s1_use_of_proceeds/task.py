"""
Location: leaves/s1_use_of_proceeds/task.py
Purpose: Leaf 7.3 — extract the primary stated use of proceeds from an S-1 filing's
         "Use of Proceeds" section.
Functions: build_prompt(), TASK
Calls: (none)
Imports: (none)
"""

_SYSTEM = (
    "You are a securities analyst. Read the 'Use of Proceeds' section from an S-1 IPO filing below. "
    "Extract the PRIMARY stated use of the IPO proceeds (the first or main category mentioned)."
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"primary_use_of_proceeds": "<extracted use category or amount>"}\n'
)


def build_prompt(instance: dict) -> str:
    """The use-of-proceeds section excerpt."""
    excerpt = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nS-1 USE OF PROCEEDS SECTION:\n{excerpt}\n\nJSON:"


TASK = {
    "name": "s1_use_of_proceeds",
    "description": "Extract the primary use of IPO proceeds from an S-1 filing (7.3).",
    "fields": {
        "primary_use_of_proceeds": {
            "type": "string",
            "description": "The primary stated use or allocation of IPO proceeds.",
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
