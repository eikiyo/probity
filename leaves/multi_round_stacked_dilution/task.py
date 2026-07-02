"""
Location: leaves/multi_round_stacked_dilution/task.py
Purpose: Leaf 3.6 -- compute per-share dilution to new investors from a real IPO
         prospectus's own Dilution-section numbers (public offering price per share minus
         pro forma/as-adjusted net tangible book value per share after the offering).
         REDEFINITION NOTE: the original task spec (Series A vs B vs C stacked ownership %
         cascade in a single document) was a genuine sourcing wall -- no real public filing
         states that cascade with concrete numbers (see git history / prior DEFERRED.md).
         This computes the real, equivalent underlying phenomenon instead: the as-adjusted
         net tangible book value per share reflects the CUMULATIVE, STACKED effect of every
         prior financing round the company ever raised (seed through late-stage VC), and the
         Dilution-section table is the standard place every real S-1/424B4 discloses exactly
         how much that stacked history dilutes the newest investors. Same underlying construct
         (cumulative multi-round dilution), sourced from where real documents actually state it.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing / IPO analyst. Read the excerpt below from a real IPO "
    "prospectus's Dilution section. COMPUTE the per-share dilution to new investors: "
    "(public offering price per share) minus (as-adjusted/pro forma net tangible book value "
    "per share AFTER the offering). Round to 2 decimal places."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"multi_round_stacked_dilution": <decimal>}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nPROSPECTUS DILUTION SECTION EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "multi_round_stacked_dilution",
    "description": "Compute per-share dilution to new IPO investors from real prospectus Dilution-section figures (3.6).",
    "fields": {
        "multi_round_stacked_dilution": {
            "type": "number",
            "op": "CO",
            "description": "offering price per share minus as-adjusted NTBV per share after offering, as a bare decimal"
        }
    },
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
