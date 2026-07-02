"""
Location: leaves/round_size/task.py
Purpose: Leaf 1.2.1 -- extract the NUMBER representing the TOTAL AGGREGATE financing 
         round size (in dollars, all investors combined). Sourced from real Form D
         filings' structured XML fields.
Functions: build_prompt(), TASK

WHY the prompt explicitly disambiguates totalAmountSold vs totalOfferingAmount (added
2026-07-02, adversarial audit): a Form D filing's XML always carries BOTH a
<totalOfferingAmount> (what the issuer is trying to raise, the target/ceiling) and a
<totalAmountSold> (what has actually closed so far) -- these are often EQUAL (offering fully
subscribed) but frequently differ (an ongoing or partially-filled round). The original prompt
wording ("the total dollar amount raised") was genuinely ambiguous between these two real,
adjacent numbers in the source document. Verified empirically: BOTH gemma3:1b and deepseek-v4-
flash scored EXACTLY 30% accuracy with 0% wobble (i.e., both models were perfectly internally
consistent, and perfectly consistent WITH EACH OTHER) -- and the pattern was 100% deterministic:
every item where the two XML fields were EQUAL scored correct; every item where they DIFFERED,
both models picked totalOfferingAmount and were marked wrong against an oracle that always uses
totalAmountSold. This was not a genuine reasoning/extraction failure -- it was an under-specified
instruction reliably steering two independent models to the same defensible-but-wrong reading.
The fix below makes the intended field explicit so the task actually tests extraction ability,
not prompt-wording-guessing.
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and extract the "
    "TOTAL AGGREGATE financing round size — the total dollar amount raised across all "
    "investors in the priced Series [X] Preferred Stock round. This is the aggregate for "
    "the entire round, not a single investor's allocation or per-share price. "
    "IMPORTANT: if the document is a Form D filing showing BOTH a total offering amount "
    "(the target/ceiling the issuer is trying to raise) and a total amount SOLD (what has "
    "actually closed so far), and these two figures differ, use the AMOUNT SOLD/ACTUALLY "
    "RAISED figure — the round size is what investors have actually put in, not the "
    "issuer's stated fundraising target."
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"round_size": <integer>}\n'
    'where integer is the bare dollar amount with no commas or $ sign (e.g., 20000000).\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "round_size",
    "description": "Extract the total aggregate financing round size in dollars (1.2.1).",
    "fields": {"round_size": {"type": "number", "op": "EX",
               "description": "total aggregate dollar amount raised in the equity financing round"}},
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
