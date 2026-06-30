"""
Location: leaves/board_seats_investor/task.py
Purpose: Leaf 5.1 -- extract the NUMBER of board seats an investor/investor class has the contractual
         right to designate, from a Voting Agreement / Shareholders' Agreement / Designation Agreement
         board-composition clause. NUMBER extraction (not yes/no): the model outputs an integer.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the NUMBER of "
    "board seats the named investor/investor class has the contractual right to designate."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"board_seats_investor": <integer>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "board_seats_investor",
    "description": "Extract the number of board seats an investor has the right to designate (5.1).",
    "fields": {"board_seats_investor": {"type": "number", "op": "EX",
               "description": "the number of board seats the investor/investor class may designate"}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
