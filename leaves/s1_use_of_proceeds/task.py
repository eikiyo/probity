"""
Location: leaves/s1_use_of_proceeds/task.py
Purpose: Leaf 7.3 -- extract the primary stated use of IPO proceeds from a real S-1/424B4
         filing's Use of Proceeds section (op EX=extract).
         REBUILD NOTE: prior attempt used the wrong field name (primary_use_of_proceeds
         instead of the registry's s1_use_of_proceeds) and was later found to have shipped
         59 items sourced from the WRONG document type (SEC comment letters / CORRESP
         filings ABOUT a company's Use of Proceeds section, not the section itself -- see
         git history). Rebuilt from real, verified S-1/424B4 prospectus bodies only.
         SCORING-METHODOLOGY FIX (2026-07-02, adversarial audit, Eikiyo-confirmed): the prompt
         previously asked for a "short phrase" summary, inviting paraphrase (e.g. "general
         corporate purposes" vs the model's own "operating expenses and corporate needs") that
         canonical string/enum matching would mark wrong even when substantively correct.
         Verified all 5 oracle.jsonl truth values ARE literal (case-insensitive) substrings of
         their corpus/questions/*.txt windows, so this is a pure prompt fix -- oracle.jsonl is
         UNCHANGED. Now requires VERBATIM extraction (the exact phrase as it appears in the
         text), matching the already-proven-working pattern in leaf 7.4 (s1_risk_factors).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a securities analyst. Read the 'Use of Proceeds' section excerpt below from a "
    "real S-1/424B4 IPO prospectus. Extract the PRIMARY stated use of the offering proceeds, "
    "as the SHORTEST possible VERBATIM phrase copied exactly from the text -- 3 to 7 words, "
    "naming just the core purpose (e.g. 'general corporate purposes', 'working capital', "
    "'research and development activities'). Do NOT paraphrase, and do NOT include any "
    "trailing elaboration clause (e.g. an 'including ...' list of sub-uses) -- stop at the "
    "core phrase itself, before any such elaboration begins."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"s1_use_of_proceeds": "<shortest exact verbatim core phrase, no trailing elaboration>"}\n'
)

def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nUSE OF PROCEEDS SECTION EXCERPT:\n{clause}\n\nJSON:"

TASK = {
    "name": "s1_use_of_proceeds",
    "description": "Extract the primary stated use of IPO proceeds from a real S-1/424B4 filing (7.3).",
    "fields": {
        "s1_use_of_proceeds": {
            "type": "string",
            "op": "EX",
            "description": "the primary stated use of proceeds, as an exact verbatim phrase copied from the text"
        }
    },
    "stakes_weight": 2,
    "build_prompt": build_prompt,
}
