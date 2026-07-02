"""
Location: leaves/option_pool_shuffle/task.py
Purpose: Leaf 3.3 -- compute the effective price per share in a financing round that includes
         a PRE-MONEY option pool expansion (ref 3.3, type: number, op: CO compute, stakes 5).
         REBUILD NOTE: prior task.py used field name "result_pct" instead of the registry's
         "option_pool_shuffle". Rebuilt using real, SEC-filed worked examples (a WeFunder
         Agreement for Future Equity template's Appendix II, filed as a Form C exhibit) --
         see source.py for full provenance/redefinition notes.
         Core mechanic: when an option pool is created/expanded PRE-MONEY, the pool is counted
         as part of the pre-money share count, which LOWERS the effective price per share paid
         by the new investor's post-money percentage (the pool dilutes existing shareholders,
         not the new investor). price_per_share = pre_money_valuation / fully_diluted_shares
         (where fully_diluted_shares already includes the newly-created pool).
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing expert. Read the financing round details below, where a new "
    "option pool is being created PRE-MONEY (before the price per share is set). Compute the "
    "price per share paid by new investors: pre-money valuation divided by the company's "
    "fully-diluted outstanding capital stock immediately prior to the financing (which already "
    "includes the newly-created option pool, since the pool dilutes existing shareholders, not "
    "the new investor)."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"option_pool_shuffle": <decimal>}\n'
    'where decimal is the price per share (e.g., 0.909).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nFINANCING ROUND DETAILS:\n{clause}\n\nJSON:"


TASK = {
    "name": "option_pool_shuffle",
    "description": "Compute price per share in a pre-money option-pool-expansion financing round (3.3, stakes=5).",
    "fields": {
        "option_pool_shuffle": {
            "type": "number",
            "op": "CO",
            "description": "price per share = pre-money valuation / pool-inclusive fully-diluted share count"
        }
    },
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
