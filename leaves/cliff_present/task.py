"""
Location: leaves/cliff_present/task.py
Purpose: Leaf 6.2 -- classify whether a founder/employee equity vesting schedule includes a CLIFF
         (a blockage period -- typically one year -- during which zero shares vest, followed by a
         chunk vesting at once and the remainder vesting periodically), or does NOT (vesting starts
         immediately / is purely periodic from day one with no blockage period). The discriminator is
         the SCHEDULE SHAPE shown, not the word "vest": an equal-annual-from-year-one schedule and a
         document whose operative text WAIVES a cliff requirement are both deliberate hard negatives.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether the "
    "vesting schedule it describes includes a CLIFF, or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the schedule includes a CLIFF -- a blockage period (e.g. one year) during which zero "
    "shares vest, after which a chunk vests at once and the remainder vests periodically "
    "('one-year cliff', 'Cliff Vesting Date', 'cliff-vesting').\n"
    "- \"no\": the schedule does NOT include a cliff. This includes vesting that starts immediately, "
    "purely periodic vesting with no blockage period ('vests quarterly, no cliff', 'vest "
    "immediately'), an equal-amount-vests-on-each-anniversary-starting-year-one schedule (no upfront "
    "blockage, even though it never says the word 'no cliff'), AND a trap: an excerpt whose operative "
    "text is a WAIVER of a cliff requirement (the cliff is being removed/excused, not currently in "
    "effect as shown).\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"cliff_present": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "cliff_present",
    "description": "Classify whether a vesting schedule includes a cliff blockage period (6.2).",
    "fields": {"cliff_present": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if the schedule has a cliff blockage period, else no."}},
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
