"""
Location: leaves/liquidation_preference_multiple/task.py
Purpose: Leaf 1.3.1 — classify the liquidation preference MULTIPLE in a preferred-stock
         charter clause. Enum field: how many times the original purchase price does the
         holder get back (1x, 2x, 3x, other, non-participating). Compatible with
         engine/harness.run_harness (task-dict API).
Functions: build_prompt(), TASK
Calls: (none)
Imports: (none)
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock liquidation preference "
    "clause below and identify the liquidation preference MULTIPLE — i.e., how many times "
    "the original issue price (OIP) the preferred holder receives upon liquidation."
)

_TAXONOMY = (
    "Classify into exactly one of these categories based on the MULTIPLE ONLY:\n"
    "- \"1x\": the preferred receives an amount equal to ONE (1) times the Original Issue Price "
    "(this is the most common, market-standard multiple).\n"
    "- \"2x\": the preferred receives an amount equal to TWO (2) times the Original Issue Price "
    "(off-market, investor-favorable).\n"
    "- \"3x\": the preferred receives an amount equal to THREE (3) times or higher the Original Issue Price "
    "(rare, highly off-market).\n"
    "- \"other\": the clause specifies a liquidation preference with a multiple other than "
    "1x, 2x, or 3x (e.g., 1.5x, 4x, or a named dollar amount).\n"
    "- \"non-participating\": the clause text explicitly states there IS NO liquidation preference "
    "(rare; most charters specify at least 1x).\n"
    "Focus ONLY on the stated MULTIPLE. Participation (whether the holder also shares remaining assets) "
    "is a separate classification (leaf 1.3.2). If the clause is silent/absent, use \"1x\" (the default).\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"liquidation_preference_multiple": "non-participating" | "1x" | "2x" | "3x" | "other"}\n'
)


def build_prompt(instance: dict) -> str:
    """Stable prefix (system + taxonomy + instruction) then the clause tail."""
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nLIQUIDATION CLAUSE:\n{clause}\n\nJSON:"


TASK = {
    "name": "liquidation_preference_multiple",
    "description": "Classify liquidation preference multiple (1x, 2x, 3x, other, non-participating) (leaf 1.3.1).",
    "fields": {
        "liquidation_preference_multiple": {
            "type": "enum",
            "values": ["non-participating", "1x", "2x", "3x", "other"],
            "description": "How many times the OIP the preferred holder receives upon liquidation.",
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
