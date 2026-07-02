"""
Location: leaves/convert_vs_preference_decision/task.py
Purpose: Leaf 4.4 -- decide whether an investor should CONVERT to common stock or TAKE their
         PREFERENCE (purchase amount returned) in an acquisition/liquidity event (op CO=compute,
         type enum). Sourced from real, SEC-filed worked examples: a WeFunder Agreement for
         Future Equity template's Appendix II (filed as a Form C exhibit) -- see source.py for
         full provenance. The decision rule: compute the as-converted payout (Liquidity Price =
         Valuation Cap / fully-diluted shares; converted shares = purchase amount / Liquidity
         Price; payout = converted shares * (deal consideration / fully-diluted shares)) and
         compare it to the flat purchase-amount preference -- convert if higher, take-preference
         if lower.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing expert. Read the acquisition scenario below. An investor holds "
    "an Agreement for Future Equity (a SAFE-like instrument) with a stated purchase amount and "
    "Valuation Cap. Decide whether the investor should CONVERT to common stock and participate "
    "pro rata in the deal consideration, or TAKE THEIR PREFERENCE (have the purchase amount "
    "returned in cash) -- whichever gives the investor more money."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"convert_vs_preference_decision": "convert" | "take-preference"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nACQUISITION SCENARIO:\n{clause}\n\nJSON:"


TASK = {
    "name": "convert_vs_preference_decision",
    "description": "Decide convert-vs-take-preference in a real acquisition scenario (4.4).",
    "fields": {
        "convert_vs_preference_decision": {
            "type": "enum",
            "op": "CO",
            "values": ["convert", "take-preference"],
            "description": "whether the investor should convert to common or take their preference"
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
