"""
Location: leaves/s1_risk_factors/task.py
Purpose: Leaf 7.4 -- extract the risk-factor HEADING (the bolded topic sentence that opens a
         real S-1 risk-factor paragraph) from a real S-1's Risk Factors section (op EX=extract).
         REBUILD NOTE: prior attempt used the wrong field name (risk_factor_heading instead of
         the registry's s1_risk_factors) and never sourced real items. Rebuilt: the model is
         given the heading sentence immediately followed by its real body paragraph (as
         plain-text HTML scraping would present it, with bold formatting lost) and must extract
         exactly the opening heading sentence, not any part of the body.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a securities analyst. Read the risk-factor excerpt below from a real S-1 IPO "
    "filing's Risk Factors section. It begins with a bolded HEADING sentence (the risk factor's "
    "title), immediately followed by the body paragraph explaining the risk. Extract ONLY the "
    "heading sentence -- the first sentence, which states the risk itself in one sentence."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"s1_risk_factors": "<exact heading sentence>"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nRISK FACTOR EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "s1_risk_factors",
    "description": "Extract the heading sentence of a real S-1 risk factor (7.4).",
    "fields": {
        "s1_risk_factors": {
            "type": "string",
            "op": "EX",
            "description": "the exact risk-factor heading sentence, verbatim"
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
