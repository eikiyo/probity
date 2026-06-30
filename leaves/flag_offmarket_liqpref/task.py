"""
Location: leaves/flag_offmarket_liqpref/task.py
Purpose: Leaf 8.1 — risk flag: read a preferred-stock liquidation provision, work out the liquidation
         preference MULTIPLE (the multiple of the Original Issue Price), and flag whether it is
         OFF-MARKET (greater than 1x). Standard venture terms are a 1x preference; >1x is investor-
         favorable / off-market. A reasoning leaf: extract the multiple, then apply the 1x norm.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer screening a term for off-market risk. Read the liquidation "
    "provision below, determine the liquidation-preference MULTIPLE (how many times the Original "
    "Issue Price the preferred is paid before common), and answer whether that multiple is "
    "OFF-MARKET."
)
_TAXONOMY = (
    "The market-standard liquidation preference is 1x (one times the Original Issue Price, optionally "
    "plus accrued/declared dividends). Answer:\n"
    "- \"yes\": the liquidation-preference multiple is GREATER THAN 1x (e.g. 1.5x, two times / 2x, "
    "three times / 3x, 200% of the Original Issue Price). This is off-market. Accrued dividends added "
    "on TOP of a 1x preference do NOT make it >1x — only a multiple above one of the Original Issue "
    "Price counts.\n"
    "- \"no\": the liquidation-preference multiple is exactly 1x (an amount equal to the Original Issue "
    "Price, or 1.0x, possibly plus accrued/declared dividends). This is standard, not off-market.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"flag_offmarket_liqpref": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nLIQUIDATION PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "flag_offmarket_liqpref",
    "description": "Flag whether a liquidation preference multiple is off-market (>1x) (8.1).",
    "fields": {"flag_offmarket_liqpref": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if the liquidation preference multiple is greater than 1x, else no."}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
