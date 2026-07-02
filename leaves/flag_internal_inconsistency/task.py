"""
Location: leaves/flag_internal_inconsistency/task.py
Purpose: Leaf 8.6 -- flag whether two real, independently-cited shares-outstanding figures
         within the SAME filing are numerically consistent (op FL=flag).
         SCOPING DECISION (registry flagged this leaf "uncertain": needs a cross-field
         consistency spec): scoped to the single most common, real, checkable cross-field
         pair every S-1 filing contains -- the shares-outstanding figure stated in the
         Capitalization table's "actual" column vs. the shares-outstanding figure cited
         elsewhere in the same filing (prospectus summary "based on X shares outstanding as
         of [date]" language, or a beneficial-ownership table's "Before Offering" column).
         true = the two cited figures DIFFER (a real, date-driven or genuine discrepancy);
         false = the two cited figures MATCH exactly.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a securities-filing reviewer. Read the two share-count citations below, both "
    "taken from the SAME real SEC filing. Flag whether they are internally INCONSISTENT "
    "(the two stated share counts are numerically different) or CONSISTENT (they state the "
    "exact same number)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"flag_internal_inconsistency": true | false}\n'
    'true = the two citations state DIFFERENT numbers (inconsistent).\n'
    'false = the two citations state the SAME number (consistent).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nTWO CITATIONS FROM THE SAME FILING:\n{clause}\n\nJSON:"


TASK = {
    "name": "flag_internal_inconsistency",
    "description": "Flag whether two real share-count citations in the same filing are numerically consistent (8.6).",
    "fields": {
        "flag_internal_inconsistency": {
            "type": "bool",
            "op": "FL",
            "description": "true if the two cited share counts differ, false if they match"
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
