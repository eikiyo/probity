"""
Location: leaves/flag_uncapped_participation/task.py
Purpose: Leaf 8.3 -- classify whether a preferred stock clause grants holders UNCAPPED
         participating-preferred rights (participates in remaining proceeds with NO CAP).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether it "
    "grants preferred stockholders/investors UNCAPPED PARTICIPATING-PREFERRED RIGHTS -- the right "
    "to participate in the remaining proceeds after the liquidation preference WITHOUT ANY CAP on the "
    "additional amount received -- or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the excerpt grants preferred holders the right to participate in remaining "
    "proceeds AFTER their liquidation preference is paid, WITH NO LIMIT/CAP on the additional amount. "
    "Examples: \"the remaining assets shall be distributed ratably among holders of Preferred and "
    "Common Stock,\" \"participate with the holders of Common Stock in all remaining distributions.\"\n"
    "- \"no\": the excerpt does NOT grant uncapped participation. This includes: (1) "
    "NON-PARTICIPATING preferred (preference only, no further participation; e.g., greater-of "
    "structure), (2) CAPPED participation (preference + participation up to a cap, e.g. \"until "
    "stockholders have received 3x their investment\"), (3) no liquidation preference language. \n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{\"flag_uncapped_participation\": \"yes\" | \"no\"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "flag_uncapped_participation",
    "description": "Classify whether a preferred stock clause grants UNCAPPED participating-preferred rights (8.3).",
    "fields": {"flag_uncapped_participation": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if preferred can participate in remaining proceeds without a cap, else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
