"""
Location: leaves/post_money_valuation/task.py
Purpose: Leaf 1.1.1 — extract the post-money valuation (dollar figure) from a priced-equity
         financing document (term sheet, stock purchase agreement, or board consent).
         This is a NUMBER extraction task: the model outputs a bare dollar amount (e.g. 50000000).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract "
    "the POST-MONEY VALUATION figure stated for the priced-equity financing round."
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"post_money_valuation": <number_in_dollars>}\n'
    'Example: {"post_money_valuation": 50000000} for a $50 million post-money valuation.\n'
    'If no post-money valuation is stated, respond with: {"post_money_valuation": null}'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "post_money_valuation",
    "description": "Extract the post-money valuation dollar amount from a priced-equity financing document (1.1.1).",
    "fields": {"post_money_valuation": {
        "type": "number",
        "description": "The post-money valuation in US dollars stated in the document."
    }},
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
