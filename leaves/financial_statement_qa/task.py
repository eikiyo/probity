"""
Location: leaves/financial_statement_qa/task.py
Purpose: Leaf 7.5 -- extract a specific, named fiscal-period revenue figure from a real S-1
         Selected/Summary Financial Data table (op EX=extract).
         SCOPING DECISION (registry flagged this leaf "uncertain": needs a labeled
         financial-statement set): "financial statement Q&A" is scoped to the single most
         universally-present, unambiguous real S-1 disclosure -- the revenue line item for a
         document-specified fiscal period in the Selected/Summary Financial Data table. The
         per-item target period is embedded directly in the model-facing window text (a real,
         literal instruction pointing at one real number already in the real table -- not
         invented data), because the shared engine.runner only passes through {id, document},
         so per-item disambiguation must live in the window itself.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a financial analyst. Read the Selected/Summary Financial Data table excerpt below "
    "from a real S-1 prospectus. Find the TARGET PERIOD specified at the top and extract the "
    "revenue figure for exactly that period."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"financial_statement_qa": <integer>}\n'
    'where integer is the bare dollar figure with no commas, $ sign, or "thousands" scaling applied '
    '(report the number exactly as it appears in the table for that period).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nFINANCIAL DATA TABLE EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "financial_statement_qa",
    "description": "Extract a named-period revenue figure from a real S-1 Selected Financial Data table (7.5).",
    "fields": {
        "financial_statement_qa": {
            "type": "number",
            "op": "EX",
            "description": "the revenue figure stated in the table for the specified target period, as a bare integer"
        }
    },
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
