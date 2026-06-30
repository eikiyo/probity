"""
Location: leaves/option_strike_409a/task.py
Purpose: Leaf 6.4 -- extract the STOCK OPTION EXERCISE/STRIKE PRICE PER SHARE from a stock
         option grant agreement or notice of grant. NUMBER extraction (not yes/no): the model
         outputs a bare number (e.g., 2.31). This is the "409A" fair market value price set
         at grant date per IRS Section 409A valuation rules.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the "
    "STOCK OPTION EXERCISE PRICE PER SHARE (also called strike price) stated in the grant. "
    "This is the fair market value per share at which the optionee may exercise the option."
)
_INSTRUCTION = (
    "Respond with ONLY this JSON object, nothing else:\n"
    "{\"option_strike_409a\": <number>}\n"
    "\n"
    "Return ONLY the strike price as a number (e.g. 2.31), with no dollar sign and no other text."
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "option_strike_409a",
    "description": "Extract the stock option exercise price per share from a grant agreement (6.4).",
    "fields": {"option_strike_409a": {"type": "number", "op": "EX",
               "description": "the exercise price (strike price) per share of the granted option"}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
