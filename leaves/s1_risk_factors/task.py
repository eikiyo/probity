"""
Location: leaves/s1_risk_factors/task.py
Purpose: Leaf 7.4 — extract a specific named risk-factor HEADING from an S-1's
         "Risk Factors" section (heading text only, not the full paragraph).
Functions: build_prompt(), TASK
Calls: (none)
Imports: (none)
"""

_SYSTEM = (
    "You are a securities analyst. Read the 'Risk Factors' section from an S-1 IPO filing below. "
    "Identify and extract the HEADING of a specific risk factor (the bolded or italicized title, "
    "not the full paragraph text)."
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"risk_factor_heading": "<extracted heading text>"}\n'
)


def build_prompt(instance: dict) -> str:
    """The risk factors section excerpt."""
    excerpt = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nS-1 RISK FACTORS SECTION:\n{excerpt}\n\nJSON:"


TASK = {
    "name": "s1_risk_factors",
    "description": "Extract a risk-factor heading from an S-1's Risk Factors section (7.4).",
    "fields": {
        "risk_factor_heading": {
            "type": "string",
            "description": "The heading text of a specific risk factor from the S-1.",
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
