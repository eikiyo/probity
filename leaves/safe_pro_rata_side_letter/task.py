"""
Location: leaves/safe_pro_rata_side_letter/task.py
Purpose: Leaf 2.1.6 -- classify whether a SAFE (Simple Agreement for Future Equity) financing is 
         accompanied by a standalone PRO RATA SIDE LETTER or embedded "Pro Rata Rights Agreement" 
         clause that grants the investor the right to purchase its pro rata share in the priced equity 
         round that the SAFE converts into (vs no such side letter / pro-rata mechanism present).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the SAFE document excerpt below and classify whether it "
    "includes a Pro Rata Rights Agreement side letter or embedded pro-rata side-letter clause."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the SAFE or related document explicitly mentions a 'Pro Rata Rights Agreement' side letter "
    "or an embedded clause stating that the investor will execute or has the right to a pro-rata share purchase "
    "in future equity rounds (e.g., 'the Company will execute a Pro Rata Rights Agreement', 'Pro Rata Rights "
    "Agreement giving the Investor a right to purchase its pro rata share').\n"
    "- \"no\": the SAFE does NOT include any mention of a pro-rata side letter or embedded pro-rata rights clause. "
    "It may cover conversion mechanics, equity financing, or other terms, but lacks the specific pro-rata "
    "side-letter language.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"safe_pro_rata_side_letter": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "safe_pro_rata_side_letter",
    "description": "Classify whether a SAFE includes a Pro Rata Rights Agreement side letter (2.1.6).",
    "fields": {"safe_pro_rata_side_letter": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if the SAFE has a pro-rata side letter, else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
