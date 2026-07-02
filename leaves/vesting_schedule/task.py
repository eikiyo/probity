"""
Location: leaves/vesting_schedule/task.py
Purpose: Leaf 6.1 — extract and normalize an equity-award vesting schedule from the actual
         provision text. The model reads the real vesting clause and maps it to a canonical
         normalized string format, e.g. "4yr/1yr-cliff" or "3yr/no-cliff".
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the vesting schedule provision below and extract "
    "the vesting schedule, normalizing it to a canonical format."
)
_TAXONOMY = (
    "Normalize the vesting schedule into exactly one of these canonical formats:\n"
    "- \"Nyr/Myr-cliff\": Total vesting period is N years, with a cliff (blockage) of M years "
    "(where N and M are integers or decimals like 1.5, 2.5, 4, etc.). The cliff is a period "
    "during which zero shares vest, after which a chunk vests and the remainder vests periodically. "
    "Example: '4yr/1yr-cliff' = 4-year total vesting with a 1-year cliff (25% at year 1, then "
    "monthly thereafter). '3yr/cliff' = 3-year cliff vesting (all shares vest in one chunk at year 3).\n"
    "- \"Nyr/no-cliff\": Total vesting period is N years with NO cliff. Vesting starts immediately "
    "and is periodic (e.g. monthly, quarterly, or equal annual amounts). "
    "Example: '4yr/no-cliff' = 4-year vesting with no blockage, vesting each month or quarter. "
    "'1.5yr/no-cliff' = 1.5-year (18-month) vesting with no cliff, vesting periodically.\n"
    "When the text states only 'cliff vesting' with a total period (e.g. '3-year cliff vesting'), "
    "normalize to 'Nyr/cliff' (cliff at the end). When it states 'N-year vesting with X-year cliff', "
    "use 'Nyr/Xyr-cliff'. When it states 'N-year vesting with no cliff', use 'Nyr/no-cliff'.\n"
)
_INSTRUCTION = (
    'Respond with ONLY a JSON object of the exact form {"vesting_schedule": "<your answer>"}, '
    'substituting <your answer> with ONE normalized value from the formats above (e.g. '
    '{"vesting_schedule": "4yr/1yr-cliff"}). Do not include multiple alternatives, punctuation '
    'marks, or any text besides the JSON object.\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nVESTING SCHEDULE PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "vesting_schedule",
    "description": "Extract and normalize vesting schedule to canonical string format (6.1).",
    "fields": {
        "vesting_schedule": {
            "type": "string",
            "description": "Normalized vesting schedule: e.g. '4yr/1yr-cliff', '3yr/no-cliff', '4yr/cliff'.",
        }
    },
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
