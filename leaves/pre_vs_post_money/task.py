"""
Location: leaves/pre_vs_post_money/task.py
Purpose: Leaf 1.1.2 — classify a priced equity round (Series A/B/Seed) as pre-money or post-money basis.
         Single enum; prompt gives the taxonomy, the model must read the real financing doc's valuation
         language and classify the basis.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the priced equity financing document excerpt below "
    "(from a Series Seed/A/B term sheet or stock purchase agreement) and classify whether the stated "
    "valuation is on a PRE-MONEY or POST-MONEY basis."
)

_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"pre-money\": the valuation is on a PRE-MONEY basis. The stated valuation is the company's value "
    "BEFORE the new capital injection. When computing the founder/investor dilution, the pre-money valuation "
    "excludes the round being financed.\n"
    "- \"post-money\": the valuation is on a POST-MONEY basis. The stated valuation is the company's value "
    "AFTER the new capital injection. The post-money valuation includes all new capital being raised in the round.\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"pre_vs_post_money": "pre-money" | "post-money"}\n'
)

def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nFINANCING DOCUMENT EXCERPT:\n{clause}\n\nJSON:"

TASK = {
    "name": "pre_vs_post_money",
    "description": "Classify a priced equity round's valuation basis as pre-money or post-money (1.1.2).",
    "fields": {
        "pre_vs_post_money": {
            "type": "enum",
            "values": ["pre-money", "post-money"],
            "description": "Whether the financing round's stated valuation is pre-money or post-money basis."
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
