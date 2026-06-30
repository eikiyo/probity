"""
Location: leaves/safe_pre_post/task.py
Purpose: Leaf 2.1.4 — classify a YC SAFE as pre-money or post-money. Single enum; prompt gives the
         taxonomy, the model must read the real SAFE's cap/conversion mechanics and map it.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the SAFE (Simple Agreement for Future Equity) "
    "provision below and classify whether its valuation cap is PRE-MONEY or POST-MONEY."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"post-money\": the valuation cap is a POST-MONEY cap. The 'Company Capitalization' used to "
    "compute the conversion price INCLUDES all SAFEs and convertible securities (and usually the "
    "option pool). This is YC's 2018+ standard 'Post-Money Valuation Cap' SAFE; the founders bear "
    "the dilution from the whole SAFE round.\n"
    "- \"pre-money\": the valuation cap is a PRE-MONEY cap. The capitalization EXCLUDES other SAFEs / "
    "convertibles when computing the conversion price. This is YC's original (2013-2018) pre-money SAFE.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"safe_cap_type": "post-money" | "pre-money"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nSAFE PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "safe_pre_post",
    "description": "Classify a SAFE's valuation cap as pre-money or post-money (2.1.4).",
    "fields": {"safe_cap_type": {"type": "enum", "values": ["post-money", "pre-money"],
               "description": "Whether the SAFE valuation cap is pre-money or post-money."}},
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
