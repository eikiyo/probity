"""
Location: leaves/per_investor_allocation/task.py
Purpose: Leaf 1.2.2 -- extract a SPECIFIC NAMED investor's individual dollar allocation
         (distinct from the round total) from a real Schedule 13D/13D-A filing (op EX=extract).
         Schedule 13D is an investor-SIDE filing (not the company's own 8-K), which routinely
         states the reporting person's own specific purchase price -- the disclosure gap that
         made this leaf look unsourceable when only company-side 8-Ks were searched.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a securities analyst. Read the excerpt below from a real Schedule 13D filing. "
    "Extract the SPECIFIC dollar amount the named investor (the filer/Reporting Person) paid "
    "for their shares in this transaction."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"per_investor_allocation": <number>}\n'
    'where number is the bare dollar amount with no commas or $ sign (e.g. 4000000 or 46715.64).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nSCHEDULE 13D EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "per_investor_allocation",
    "description": "Extract a named investor's specific dollar allocation from a real Schedule 13D (1.2.2).",
    "fields": {
        "per_investor_allocation": {
            "type": "number",
            "op": "EX",
            "description": "the specific dollar amount the named investor paid, as a bare integer"
        }
    },
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
