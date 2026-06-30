"""
Location: leaves/flag_full_ratchet/task.py
Purpose: Leaf 8.2 — risk flag: read a preferred-stock anti-dilution provision and flag whether
         it uses FULL-RATCHET protection (true, founder-hostile) or WEIGHTED-AVERAGE / none (false,
         standard market). Full-ratchet resets the conversion price ALL THE WAY DOWN to the new, 
         lower issuance price in a down round. Weighted-average adjusts the price by a formula 
         accounting for the number of shares issued. Market standard is weighted-average or no 
         anti-dilution; full-ratchet is rare and off-market.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer screening a term for anti-dilution risk. Read the "
    "anti-dilution provision below and answer whether it uses FULL-RATCHET protection (the "
    "conversion price resets to the new issuance price in a down round) or WEIGHTED-AVERAGE "
    "protection (the price adjusts by a formula) or neither."
)
_TAXONOMY = (
    "The market-standard anti-dilution protection is WEIGHTED-AVERAGE (broad-based or narrow-based) "
    "or none at all. Full-ratchet is rare and founder-hostile. Answer:\n"
    "- \"yes\": the anti-dilution clause uses FULL-RATCHET protection (conversion price resets "
    "to the new issuance price in a down round, regardless of how many shares were issued). "
    "Phrases: 'full ratchet', 'full-ratchet', 'conversion price shall be reduced to equal the "
    "new issuance price'.\n"
    "- \"no\": the anti-dilution clause uses WEIGHTED-AVERAGE (broad-based or narrow-based) "
    "protection (price adjusts by formula), or there is no anti-dilution protection at all. "
    "Phrases: 'weighted average', 'weighted-average', 'broad-based', 'narrow-based', or no "
    "anti-dilution language present.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"flag_full_ratchet": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nANTI-DILUTION PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "flag_full_ratchet",
    "description": "Flag whether an anti-dilution clause uses full-ratchet protection (8.2).",
    "fields": {"flag_full_ratchet": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if the anti-dilution clause uses full-ratchet (conversion price resets to new issuance price), else no."}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
