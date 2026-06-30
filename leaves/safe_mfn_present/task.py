"""
Location: leaves/safe_mfn_present/task.py
Purpose: Leaf 2.1.5 -- classify whether a SAFE (Simple Agreement for Future Equity) contains
         a Most-Favored-Nation (MFN) clause that grants the investor the right to automatically
         adopt more-favorable terms if the company later issues a SAFE/note to someone else on
         better terms (vs no such MFN provision present).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the SAFE document excerpt below and classify whether it "
    "includes a Most-Favored-Nation (MFN) clause that grants the investor the right to adopt more-favorable "
    "terms issued to other investors."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the SAFE explicitly includes a Most-Favored-Nation (MFN) or \"MFN\" clause, amendment provision, "
    "or similar language stating that if the Company issues convertible securities with more favorable terms "
    "(e.g., lower valuation cap, higher discount), this investor's SAFE will automatically be amended to reflect "
    "those more-favorable terms. (e.g., 'If the Company issues any Subsequent Convertible Securities with terms "
    "more favorable... the Company will amend and restate this instrument...')\n"
    "- \"no\": the SAFE does NOT include a Most-Favored-Nation (MFN) clause or any provision giving the investor "
    "the right to adopt more-favorable terms issued to others. It may cover conversion mechanics, equity financing, "
    "or other terms, but lacks the specific MFN/amendment-to-reflect language.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{\"safe_mfn_present\": \"yes\" | \"no\"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "safe_mfn_present",
    "description": "Classify whether a SAFE includes a Most-Favored-Nation (MFN) clause (2.1.5).",
    "fields": {"safe_mfn_present": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if the SAFE has an MFN clause, else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
