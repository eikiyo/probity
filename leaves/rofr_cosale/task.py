"""
Location: leaves/rofr_cosale/task.py
Purpose: Leaf 5.5 -- classify whether a stockholder/transfer document grants INVESTORS a contractual
         Right of First Refusal and/or Co-Sale right over another holder's proposed share transfer
         (the classic VC "RoFR & Co-Sale Agreement" mechanism), or does NOT. The discriminator is the
         MECHANISM, not mere keyword presence: a company's own repurchase right on terminated/unvested
         restricted stock ("First Refusal Right" held by the Company) and a preemptive/pro-rata right
         on FUTURE financings both use adjacent vocabulary but are NOT an investor RoFR/co-sale on
         TRANSFER -- those are deliberate hard negatives.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether it "
    "grants OTHER STOCKHOLDERS/INVESTORS a Right of First Refusal and/or Co-Sale right over a "
    "stockholder's proposed transfer of shares, or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the document grants investors/other stockholders a RIGHT OF FIRST REFUSAL (the right "
    "to buy the shares first) and/or a CO-SALE/TAG-ALONG right (the right to sell alongside the "
    "transferring holder) on a proposed TRANSFER of shares by another stockholder. This is the "
    "classic 'RoFR & Co-Sale Agreement' mechanism between investors/stockholders.\n"
    "- \"no\": the document does NOT grant this. This includes documents with NO such provision at "
    "all, AND two look-alike traps: (1) a right of first refusal held by the COMPANY ITSELF to "
    "repurchase a holder's unvested/restricted/terminated shares (a company buy-back right, not an "
    "investor transfer right), and (2) a PREEMPTIVE or PRO-RATA right to participate in a FUTURE "
    "financing/equity raise (not a right tied to another holder's share TRANSFER).\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"rofr_cosale": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "rofr_cosale",
    "description": "Classify whether a document grants investors a RoFR/co-sale right on a stockholder transfer (5.5).",
    "fields": {"rofr_cosale": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if investors hold a RoFR and/or co-sale right on another holder's transfer, else no."}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
