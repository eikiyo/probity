"""
Location: leaves/pro_rata_rights/task.py
Purpose: Leaf 5.4 -- classify whether a document grants an investor a PRO RATA RIGHT (the right to
         purchase its pro rata share of securities in a FUTURE financing round, to avoid dilution),
         or does NOT. The discriminator is a live GRANT vs two look-alikes: a document that mentions
         the term while actually WAIVING it for one specific issuance (the underlying general right is
         not evidenced as currently exercisable in the excerpt shown), and a document with no pro-rata
         mechanism at all (e.g. a restricted-stock/exchange agreement).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether it "
    "grants the investor/holder a PRO RATA RIGHT -- the right to purchase its pro rata share of "
    "securities in a FUTURE financing round to avoid dilution -- or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the excerpt GRANTS a live pro rata / preemptive right to participate in a future "
    "financing ('Pro Rata Right', 'shall have the right to purchase its pro rata share', 'the Company "
    "will execute a Pro Rata Rights Agreement').\n"
    "- \"no\": the excerpt does NOT currently grant this. This includes documents with no pro-rata "
    "mechanism at all, AND a trap: an excerpt whose OPERATIVE text is a WAIVER of the right for one "
    "specific issuance/transaction (even if it references that a right exists under another, "
    "underlying agreement) -- within the four corners of what is shown, no right is being granted or "
    "is currently exercisable.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"pro_rata_rights": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "pro_rata_rights",
    "description": "Classify whether a document grants a live pro-rata right to participate in a future financing (5.4).",
    "fields": {"pro_rata_rights": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if a live pro-rata/preemptive right on future financings is granted, else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
