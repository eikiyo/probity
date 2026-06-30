"""
Location: leaves/round_size/task.py
Purpose: Leaf 1.2.1 -- extract the NUMBER representing the TOTAL AGGREGATE financing 
         round size (in dollars, all investors combined) from Series A/B/C/D/E 
         Preferred Stock financing documents.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the "
    "TOTAL AGGREGATE financing round size — the total dollar amount raised across all "
    "investors in the priced Series [X] Preferred Stock round. This is the aggregate for "
    "the entire round, not a single investor's allocation or per-share price."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"round_size": <integer>}\n'
    'where integer is the bare dollar amount with no commas or $ sign (e.g., 20000000).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "round_size",
    "description": "Extract the total aggregate financing round size in dollars (1.2.1).",
    "fields": {"round_size": {"type": "number", "op": "EX",
               "description": "total aggregate dollar amount raised in the equity financing round"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
