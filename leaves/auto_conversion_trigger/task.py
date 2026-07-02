"""
Location: leaves/auto_conversion_trigger/task.py
Purpose: Leaf 1.6.2 -- extract the NUMBER representing the QPO (Qualified Public Offering)
         threshold that AUTOMATICALLY triggers preferred-to-common stock conversion. This is
         the aggregate proceeds amount (in USD) stated in a charter's automatic conversion
         article -- gross or net of underwriting discounts, per whichever convention the real
         charter itself uses (see WHY below).
Functions: build_prompt(), TASK

WHY the prompt says "gross OR net" rather than just "gross" (added 2026-07-02, adversarial
audit): the real charters in this leaf's corpus are NOT consistent about which convention they
use for the QPO threshold -- 2/5 items state the figure as GROSS proceeds ("prior to deduction
of underwriting commissions"), the other 3/5 state it as NET proceeds ("net of underwriting
discounts and commissions"). The original prompt told the model to extract "only the AGGREGATE
GROSS PROCEEDS dollar amount" unconditionally, which was factually wrong for 3 of the 5 real
documents. This did NOT actually produce any measured scoring harm (both models hit 100% on
every item, including the net-proceeds ones) because each document only ever states ONE
qualifying dollar figure -- there's no second, different number for "gross" that the model
could confuse it with, unlike the round_size leaf's totalOfferingAmount/totalAmountSold trap.
Still fixed the wording for correctness/future-proofing: a future re-sourcing pass could add an
item where gross and net genuinely differ, and the old prompt would then produce the wrong
figure by construction. Not rerun -- existing runs are still valid ground truth and fixing
prompt wording that was never actually exercised wrong doesn't need new API spend to "prove"
anything already at 100%/100%.
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract "
    "the QPO (Qualified Public Offering) threshold stated in the preferred-stock charter — "
    "the single aggregate dollar proceeds amount (in USD) that automatically converts all "
    "preferred stock to common stock, whether the charter states it as gross proceeds or net "
    "proceeds (after underwriting discounts) -- extract whichever single dollar figure the "
    "charter itself uses as the QPO trigger. Do NOT extract a price-per-share threshold."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"auto_conversion_trigger": <number>}\n'
    'Examples: 30000000, 50000000, 100000000\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "auto_conversion_trigger",
    "description": "Extract the QPO (aggregate gross-or-net proceeds) threshold for automatic preferred-to-common conversion (1.6.2).",
    "fields": {"auto_conversion_trigger": {"type": "number", "op": "EX",
               "description": "the USD amount (aggregate proceeds, gross or net per the charter's own convention) that triggers automatic conversion"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
