"""
Location: leaves/safe_cap_vs_discount_applies/task.py
Purpose: Leaf 2.1.3 — classify whether a SAFE uses cap-only, discount-only, or both cap+discount (MFN).
         ENUM-type field: model outputs one of three values based on the SAFE's conversion mechanic.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the SAFE (Simple Agreement for Future Equity) "
    "document excerpt below and classify how the SAFE's conversion price is computed."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"cap\": the SAFE uses ONLY a valuation cap to compute the conversion price. There is NO discount "
    "rate in this SAFE. The 'Conversion Price' is defined as the cap divided by the company capitalization.\n"
    "- \"discount\": the SAFE uses ONLY a discount rate to compute the conversion price. There is NO valuation "
    "cap in this SAFE. The 'Conversion Price' is defined as a percentage discount off the next financing round's price.\n"
    "- \"both-mfn\": the SAFE uses BOTH a valuation cap AND a discount rate, with an MFN (most-favored-nation) clause. "
    "The 'Conversion Price' is defined as 'the LOWER of (1) the cap price or (2) the discount price' or "
    "'whichever calculation results in a GREATER number of shares.' This is the YC 2018+ standard post-money SAFE.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"safe_cap_vs_discount_applies": "cap" | "discount" | "both-mfn"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nSAFE EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "safe_cap_vs_discount_applies",
    "description": "Classify whether a SAFE uses cap, discount, or both-MFN for conversion pricing (2.1.3).",
    "fields": {
        "safe_cap_vs_discount_applies": {
            "type": "enum",
            "values": ["cap", "discount", "both-mfn"],
            "description": "Whether the SAFE's conversion price uses cap-only, discount-only, or both with MFN."
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
