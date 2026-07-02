"""
Location: leaves/flag_missing_pro_rata/task.py
Purpose: Leaf 8.5 -- flag whether a real financing document EXPLICITLY denies/waives an
         investor's pro-rata investment right (true) or EXPLICITLY grants it (false)
         (op FL=flag). REBUILD NOTE: prior audit found the existing pro_rata_rights corpus's
         "no" class was noise (unrelated Stock Restriction Agreement exhibits), except for two
         genuine real explicit-waiver documents (Xcyte Therapies, Rapid7) surfaced on a
         follow-up re-audit of that same "no" class -- confirming both real classes exist as
         distinct documents, not one universal template's two branches (the failure mode this
         leaf was originally deferred to guard against).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the excerpt below from a real financing "
    "document. Flag whether it EXPLICITLY denies or waives an investor's pro-rata investment "
    "right (true) or EXPLICITLY grants/confirms one (false)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"flag_missing_pro_rata": true | false}\n'
    'true = the document explicitly WAIVES or DENIES a pro-rata/preemptive right.\n'
    'false = the document explicitly GRANTS or CONFIRMS a pro-rata right.\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "flag_missing_pro_rata",
    "description": "Flag whether a real document explicitly waives/denies (vs grants) pro-rata rights (8.5).",
    "fields": {
        "flag_missing_pro_rata": {
            "type": "bool",
            "op": "FL",
            "description": "true if pro-rata right is explicitly waived/denied, false if explicitly granted"
        }
    },
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
