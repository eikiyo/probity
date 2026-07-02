"""
Location: leaves/s1_use_of_proceeds/task.py
Purpose: Leaf 7.3 -- extract the primary stated use of IPO proceeds from a real S-1/424B4
         filing's Use of Proceeds section (op EX=extract).
         REBUILD NOTE: prior attempt used the wrong field name (primary_use_of_proceeds
         instead of the registry's s1_use_of_proceeds) and was later found to have shipped
         59 items sourced from the WRONG document type (SEC comment letters / CORRESP
         filings ABOUT a company's Use of Proceeds section, not the section itself -- see
         git history). Rebuilt from real, verified S-1/424B4 prospectus bodies only.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a securities analyst. Read the 'Use of Proceeds' section excerpt below from a "
    "real S-1/424B4 IPO prospectus. Extract the PRIMARY stated use of the offering proceeds, "
    "as a short phrase (the main category or purpose named)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"s1_use_of_proceeds": "<short extracted phrase>"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nUSE OF PROCEEDS SECTION EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "s1_use_of_proceeds",
    "description": "Extract the primary stated use of IPO proceeds from a real S-1/424B4 filing (7.3).",
    "fields": {
        "s1_use_of_proceeds": {
            "type": "string",
            "op": "EX",
            "description": "the primary stated use of proceeds, as a short phrase"
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
