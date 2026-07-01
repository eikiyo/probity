"""
Location: leaves/antidilution_base/task.py
Purpose: Leaf 1.5.2 — for a preferred-stock charter using WEIGHTED-AVERAGE anti-dilution,
         classify which SHARE BASE the denominator of the weighted-average formula includes:
         broad-based (all outstanding common + all convertibles/options/warrants) vs
         narrow-based (only outstanding common stock, excludes convertibles) vs n/a (the
         charter uses full-ratchet or has no anti-dilution protection).
Functions: build_prompt_from_parts() [shared utility], TASK
Calls: (none)
Imports: (none)
"""

def build_prompt_from_parts(system: str, taxonomy: str, instruction: str, document: str) -> str:
    """Generic prompt builder: combine system + taxonomy + instruction + document."""
    return f"{system}\n\n{taxonomy}\n{instruction}\nCLAUSE:\n{document}\n\nJSON:"


_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock charter anti-dilution "
    "clause below. If it uses WEIGHTED-AVERAGE anti-dilution, classify the share base that "
    "the weighted-average formula's denominator includes."
)

_TAXONOMY = (
    "Classify into exactly one of these categories based on the weighted-average DENOMINATOR:\n"
    "- \"broad-based\": the weighted-average formula's denominator includes (a) all outstanding "
    "shares of Common Stock AND (b) all shares of Common Stock issuable upon exercise or conversion "
    "of outstanding warrants, options, convertible securities, etc. (i.e., fully diluted). "
    "Denominator language: 'all shares of Common Stock outstanding, plus all shares of Common Stock "
    "issuable upon exercise or conversion of...warrants, options, convertible securities.' This is "
    "FOUNDER-favorable, investor-unfavorable (smaller denominator → smaller adjustment).\n"
    "- \"narrow-based\": the weighted-average formula's denominator includes ONLY outstanding "
    "shares of Common Stock (excludes unexercised options, unexercised warrants, unconverted "
    "securities). Denominator language: 'shares of Common Stock outstanding' alone, or explicitly "
    "excluding options/warrants/convertibles. This is INVESTOR-favorable, founder-unfavorable "
    "(larger denominator → larger adjustment).\n"
    "- \"n/a\": the charter does NOT use weighted-average anti-dilution. It either uses full-ratchet "
    "(conversion price set to the new, lower price on any dilutive issuance — rare, investor-favorable) "
    "or has NO anti-dilution protection (the charter explicitly states this or the holder has no "
    "protection on dilution). The base-classification question does not apply.\n"
    "If the charter explicitly states 'broad-based weighted average' or 'narrow-based weighted average', "
    "use that language. If no explicit label, read the formula's denominator definition to infer the base. "
    "If the clause describes only weighted-average WITHOUT specifying the denominator, default to 'broad-based' "
    "(the standard in US venture practice).\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{\"antidilution_base\": \"broad-based\" | \"narrow-based\" | \"n/a\"}\n'
)


def build_prompt(instance: dict) -> str:
    """Build prompt using shared utility."""
    clause = instance.get("document", "")
    return build_prompt_from_parts(_SYSTEM, _TAXONOMY, _INSTRUCTION, clause)


TASK = {
    "name": "antidilution_base",
    "description": "For weighted-average anti-dilution, classify the denominator base (broad-based, narrow-based, or n/a if not weighted-average) (leaf 1.5.2).",
    "fields": {
        "antidilution_base": {
            "type": "enum",
            "values": ["broad-based", "narrow-based", "n/a"],
            "description": "The share base (denominator) that the weighted-average anti-dilution formula uses, or n/a if the charter uses full-ratchet or no anti-dilution.",
        }
    },
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
