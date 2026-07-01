"""
Location: leaves/form_d_fields/task.py
Purpose: Leaf 7.2 -- extract the "Total Amount Sold" field value from a real Form D filing
         (ref 7.2, type: string, op: EX extract). Both sourced items ask for this same field,
         so it's stated directly in the prompt (the shared engine/runner.py loader only passes
         through {id, document} from oracle.jsonl, not arbitrary extra keys like field_name).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a securities lawyer. Read the Form D filing excerpt below and extract the exact "
    "\"Total Amount Sold\" value stated in the document (a dollar amount, digits and commas/decimal only, "
    "no dollar sign)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"form_d_field_value": "<exact Total Amount Sold value from the document>"}\n'
)


def build_prompt(instance: dict) -> str:
    excerpt = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nFORM D EXCERPT:\n{excerpt}\n\nJSON:"


TASK = {
    "name": "form_d_fields",
    "description": "Extract the Total Amount Sold field value from a real Form D filing (7.2).",
    "fields": {
        "form_d_field_value": {
            "type": "string",
            "description": "The extracted Total Amount Sold dollar value from the Form D.",
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
