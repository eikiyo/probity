"""
Location: leaves/exercise_window/task.py
Purpose: Leaf 6.5 -- extract the post-termination option exercise window (a duration in days)
         for a SPECIFIED termination scenario from a real stock option agreement (op EX=extract).
         Multiple termination scenarios (general/without-cause, retirement, death/disability)
         commonly carry DIFFERENT windows in the same real document, so the target scenario is
         named explicitly in the window text (a real, literal instruction pointing at one real
         clause already in the real document -- runner only passes {id, document} through).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are an equity-compensation attorney. Read the option agreement excerpt below and find "
    "the TARGET SCENARIO specified at the top. Extract the post-termination exercise window "
    "(the number of days the option remains exercisable after that specific termination event)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"exercise_window": "<N> days"}\n'
    'where <N> is the bare number of days (e.g. "90 days", "180 days"), for the TARGET SCENARIO only.\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nOPTION AGREEMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "exercise_window",
    "description": "Extract the post-termination option exercise window for a named scenario (6.5).",
    "fields": {
        "exercise_window": {
            "type": "string",
            "op": "EX",
            "description": "the exercise window as '<N> days' for the target termination scenario"
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
