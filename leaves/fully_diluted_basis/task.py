"""
Location: leaves/fully_diluted_basis/task.py
Purpose: Leaf 3.4 — classify a financing doc's capitalization definition as FULLY-DILUTED basis
         (includes all options/warrants/convertible securities/unissued option pool) vs
         ISSUED-OUTSTANDING basis (counts only actual issued shares, excludes options).
         Single enum; the model reads the real capitalization clause and maps it.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the CAPITALIZATION clause below and "
    "classify whether the company's capitalization or ownership calculation is computed on a "
    "FULLY-DILUTED basis or an ISSUED-AND-OUTSTANDING basis."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"fully-diluted\": the capitalization definition INCLUDES all outstanding common shares PLUS "
    "ALL convertible securities (options, warrants, restricted stock units, convertible debt, etc.) "
    "and TYPICALLY the entire unissued option pool (even ungranted options), whether or not vested. "
    "Tell-tale language: 'all outstanding shares and the full Unissued Option Pool', "
    "'fully diluted capitalization', 'as converted basis', 'on a fully diluted basis assumes the exchange "
    "of all outstanding' securities, 'including all issued and unissued options'.\n"
    "- \"issued-outstanding\": the capitalization definition counts ONLY shares actually issued and "
    "outstanding (excluding unissued options, warrants, or the option pool). Tell-tale language: "
    "'issued and outstanding shares', 'excluding options and warrants', 'Common Stock issued', "
    "'only actual issued shares', explicitly EXCLUDES options/pool.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"fully_diluted_basis": "fully-diluted" | "issued-outstanding"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nCAPITALIZATION CLAUSE:\n{clause}\n\nJSON:"


TASK = {
    "name": "fully_diluted_basis",
    "description": "Classify capitalization definition as fully-diluted or issued-outstanding basis (3.4).",
    "fields": {"fully_diluted_basis": {"type": "enum", "values": ["fully-diluted", "issued-outstanding"],
               "description": "Whether cap is computed on fully-diluted or issued-outstanding basis."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
