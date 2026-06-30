"""
Location: leaves/information_rights/task.py
Purpose: Leaf 5.3 -- classify whether a document grants investors INFORMATION RIGHTS -- an ongoing
         contractual obligation for the company to DELIVER periodic financial statements/reports to
         investors (annual/quarterly financials) -- or does NOT.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether it "
    "grants investors INFORMATION RIGHTS -- an ongoing obligation for the company to deliver periodic "
    "financial statements/reports -- or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the excerpt grants a live, ongoing obligation to deliver financial statements/reports "
    "to investors ('Information Rights', 'the Company shall deliver to each Major Investor ... annual "
    "financial statements', inspection rights).\n"
    "- \"no\": the excerpt does NOT grant this. This includes documents with no such covenant at all "
    "(e.g. a restricted-stock award agreement -- about one employee's equity, not investor reporting), "
    "AND a trap: an excerpt whose operative text WAIVES the financial-statement delivery requirement "
    "(the obligation is being excused, not currently in effect as shown).\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"information_rights": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "information_rights",
    "description": "Classify whether a document grants investors a live financial-reporting/information right (5.3).",
    "fields": {"information_rights": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if a live obligation to deliver financials to investors exists, else no."}},
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
