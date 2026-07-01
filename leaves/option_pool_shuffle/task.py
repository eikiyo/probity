"""
Location: leaves/option_pool_shuffle/task.py
Purpose: Leaf 3.3 — VC financing reasoning task: compute resulting ownership % shifts
         when an option pool is created/expanded PRE-MONEY (ref 3.3, type: number, op: CO compute).
         The core mechanic: pre-money pool dilutes ONLY existing shareholders+founders, not the investor.
         Given financing numbers (pre-money, investment, pool size/expansion), compute the result.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing expert. Read the financing round details below and compute "
    "the resulting ownership percentage change or the pool size as a percentage of the company after "
    "the pre-money option pool adjustment. Return the percentage as a bare decimal number (e.g., 12.5)."
)
_EXPLANATION = (
    "When an option pool is created or expanded PRE-MONEY (BEFORE calculating the new investor's price per share), "
    "it dilutes only the existing shareholders and founders, not the new investor. The investor's percentage is calculated "
    "on the ENLARGED share count (post-pool). Use the given pre-money valuation, investment amount, and pool details "
    "to compute: (1) the resulting ownership % of a specific party, or (2) the pool size as a % of the fully-diluted shares."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"result_pct": <decimal>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_EXPLANATION}\n\n{_INSTRUCTION}\nFINANCING DETAILS:\n{clause}\n\nJSON:"


TASK = {
    "name": "option_pool_shuffle",
    "description": "Compute VC option pool dilution (pre-money) impact on ownership percentages (3.3, stakes=5).",
    "fields": {
        "result_pct": {
            "type": "number",
            "op": "CO",
            "description": "the resulting ownership % or pool % as a bare decimal (e.g., 12.5)"
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
