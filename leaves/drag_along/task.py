"""
Location: leaves/drag_along/task.py
Purpose: Leaf 5.6 — classify whether a stockholder/transfer agreement grants a DRAG-ALONG right
         (holders are OBLIGATED to join a sale of the company) or does NOT (e.g. a co-sale/right-of-
         first-refusal agreement that grants only a RIGHT, not an obligation, to participate). The
         model reads the real clause window and maps it. The discriminator is OBLIGATION vs RIGHT.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the stockholder/transfer provision below and classify "
    "whether it grants a DRAG-ALONG right, or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the provision grants a DRAG-ALONG right — in a sale of the company, holders can be "
    "COMPELLED to participate ('each stockholder shall be obligated to sell', 'shall be required to "
    "participate in the Drag-Along Sale', 'shall vote in favor of', 'Drag-Along Obligation'). It is a "
    "FORCED-sale right that the majority/company can exercise over minority holders.\n"
    "- \"no\": the provision does NOT grant a drag-along — it grants only a RIGHT (not an obligation) to "
    "participate, such as a co-sale/tag-along right or a right of first refusal ('the right, but not an "
    "obligation, to participate', 'may elect to participate', 'right to participate in such sale'). No "
    "holder is compelled to sell.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"drag_along": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nPROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "drag_along",
    "description": "Classify whether a transfer/stockholder provision grants a drag-along (forced-sale) right (5.6).",
    "fields": {"drag_along": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if holders can be compelled to join a sale (drag-along), else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
