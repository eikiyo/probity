"""
Location: leaves/investor_ownership_pct/task.py
Purpose: Leaf 3.2.2 -- compute a named INSTITUTIONAL INVESTOR's ownership percentage from raw
         share counts in a real S-1 filing (ref 3.2.2, type: number, op: CO compute). The model
         is given the investor's shares and total shares outstanding (NOT the percentage) and
         must compute shares / total * 100 itself. Same template as current_ownership_pct (3.1)
         and founder_ownership_pct (3.2.1).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing analyst. Read the excerpt below from a real S-1 registration "
    "statement's Security Ownership table. COMPUTE the named institutional investor's ownership "
    "percentage: (investor's shares / total shares outstanding) * 100, rounded to 1 decimal place."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"investor_ownership_pct": <decimal>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nS-1 SECURITY OWNERSHIP TABLE EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "investor_ownership_pct",
    "description": "Compute a named institutional investor's ownership percentage from raw S-1 share counts (3.2.2).",
    "fields": {
        "investor_ownership_pct": {
            "type": "number",
            "op": "CO",
            "description": "the computed investor ownership percentage as a bare decimal (e.g., 16.3)"
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
