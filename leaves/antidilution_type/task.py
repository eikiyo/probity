"""
Location: leaves/antidilution_type/task.py
Purpose: Leaf 1.5.1 — classify the anti-dilution protection mechanism in a preferred-stock
         charter clause into exactly one of: full-ratchet, weighted-average, broad-based,
         narrow-based, none. This leaf focuses on the PRIMARY mechanism type.
Functions: build_prompt(), TASK
Calls: (none)
Imports: (none)
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock charter anti-dilution "
    "clause below and classify the PRIMARY anti-dilution protection mechanism."
)

_TAXONOMY = (
    "Classify into exactly one of these categories based on the anti-dilution MECHANISM:\n"
    "- \"full-ratchet\": upon issuance of new shares below the conversion price, the conversion "
    "price is set to the new (lower) price. Investor-favorable, rare.\n"
    "- \"weighted-average\": conversion price is adjusted using a weighted-average formula that "
    "blends old and new prices + share counts. This may be broad-based (all outstanding common) "
    "or narrow-based (excluding some classes), but the PRIMARY type is weighted-average.\n"
    "- \"broad-based\": ONLY if the clause explicitly states broad-based WITHOUT mentioning "
    "any averaging formula. Rare on its own; usually combined with weighted-average.\n"
    "- \"narrow-based\": ONLY if the clause explicitly states narrow-based WITHOUT mentioning "
    "any averaging formula. Rare on its own; usually combined with weighted-average.\n"
    "- \"none\": the holder has NO anti-dilution protection (the charter explicitly states this).\n"
    "If the clause describes weighted-average with broad-based or narrow-based sub-details, "
    "classify as \"weighted-average\" (the primary type). If no clause is present, classify as \"none\".\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{\"antidilution_type\": \"full-ratchet\" | \"weighted-average\" | \"broad-based\" | '
    '\"narrow-based\" | \"none\"}\n'
)


def build_prompt(instance: dict) -> str:
    """Stable prefix (system + taxonomy + instruction) then the clause tail."""
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nCLAUSE:\n{clause}\n\nJSON:"


TASK = {
    "name": "antidilution_type",
    "description": "Classify anti-dilution mechanism (full-ratchet, weighted-average, broad-based, narrow-based, none) (leaf 1.5.1).",
    "fields": {
        "antidilution_type": {
            "type": "enum",
            "values": ["full-ratchet", "weighted-average", "broad-based", "narrow-based", "none"],
            "description": "The primary anti-dilution protection mechanism in the preferred-stock charter clause.",
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
