"""
Location: leaves/liquidation_waterfall_payout/task.py
Purpose: Leaf 4.1 -- compute the per-share value remaining for common stockholders after a
         real multi-series preferred stock liquidation waterfall (op CO=compute, stakes 5).
         Sourced from a real SC 13E-3 going-private fairness opinion (Connecture, Inc., 2018),
         which discloses a full real bridge: Total Enterprise Value -> minus Severance -> minus
         Debt -> minus total Preferred Stock liquidation preference (Series A + Series B +
         accrued dividends) -> Total Equity Value -> divided by shares outstanding -> per-share
         value to common. Formula: (enterprise_value - severance - debt - preferred_liquidation)
         / shares_outstanding.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are an M&A analyst. Read the real fairness-opinion figures below (in $ millions except "
    "shares and per-share). Compute the resulting per-share value to common stockholders after "
    "the full liquidation waterfall: (Total Enterprise Value - Severance Payment - Total Debt - "
    "Preferred Stock Liquidation Preference) / Shares Outstanding."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"liquidation_waterfall_payout": <decimal>}\n'
    'where decimal is the per-share dollar value (e.g., 0.51).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nFAIRNESS OPINION FIGURES:\n{clause}\n\nJSON:"


TASK = {
    "name": "liquidation_waterfall_payout",
    "description": "Compute per-share value to common after a real multi-series preferred liquidation waterfall (4.1, stakes=5).",
    "fields": {
        "liquidation_waterfall_payout": {
            "type": "number",
            "op": "CO",
            "description": "per-share value to common stockholders, as a bare decimal"
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
