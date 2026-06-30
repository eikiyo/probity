"""
Location: leaves/redemption_rights/task.py
Purpose: Leaf 1.7 — classify whether a preferred-stock charter grants a REDEMPTION RIGHT (the holder
         can require the company to redeem, or the shares are subject to mandatory redemption) or is
         NON-REDEEMABLE (no such right). The model reads the real charter clause and maps it.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock provision below and classify whether "
    "the preferred stock carries a REDEMPTION RIGHT for its holders, or is NON-REDEEMABLE."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the preferred is REDEEMABLE — the holders can require the company to redeem (buy back) "
    "their shares, or the shares are subject to MANDATORY redemption on a date/event ('the Company "
    "shall redeem', 'the holders shall have the right to require the Corporation to redeem', 'shall be "
    "redeemed for cash'). This gives investors a way to force their money back.\n"
    "- \"no\": the preferred is NON-REDEEMABLE — the holders have no right to force redemption ('the "
    "Preferred Stock shall not be redeemable', 'shall not be redeemable at the option of the holder', "
    "'not subject to redemption'). The equity stays outstanding until it converts.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"redemption_rights": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nPREFERRED-STOCK PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "redemption_rights",
    "description": "Classify whether preferred stock is redeemable (holder/mandatory) or non-redeemable (1.7).",
    "fields": {"redemption_rights": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if the preferred carries a holder/mandatory redemption right, else no."}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
