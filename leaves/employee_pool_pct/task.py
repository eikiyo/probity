"""
Location: leaves/employee_pool_pct/task.py
Purpose: Leaf 3.2.3 -- compute employee stock option pool percentage from S-1 capitalization data
         (ref 3.2.3, type: number, op: CO compute).
         The model is given pool shares and total shares outstanding (NOT the percentage)
         and must compute pool_shares / total_shares * 100 itself.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing analyst. Read the excerpt below from a real S-1 registration "
    "statement's Capitalization section. COMPUTE the employee stock option pool's percentage of total shares: "
    "(reserved_shares / total_shares_outstanding) * 100, rounded to 1 decimal place."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"employee_pool_pct": <decimal>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nS-1 CAPITALIZATION SECTION EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "employee_pool_pct",
    "description": "Compute employee stock option pool as % of total shares from S-1 capitalization data (3.2.3).",
    "fields": {
        "employee_pool_pct": {
            "type": "number",
            "op": "CO",
            "description": "the computed employee pool percentage as a bare decimal (e.g., 9.5)"
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
