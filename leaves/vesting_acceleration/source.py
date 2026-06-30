"""
Location: leaves/vesting_acceleration/source.py
Purpose: Build the vesting_acceleration leaf corpus + oracle (5.7) from real SEC EDGAR documents
         (raw candidates pre-fetched by a parallel agent into corpus/full/ + candidates_*.jsonl; this
         script is the MANUAL oracle pass -- each item was READ and hand-classified against the real
         document text by a human). YES = document grants acceleration of vesting on a trigger event
         (unvested equity vests faster than normal schedule). NO = no acceleration provision (fixed
         schedule only, or operative text WAIVES/forbids acceleration rights).
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

ITEMS = {
    # YES -- explicit acceleration of vesting upon trigger
    "912562_000091256215000002":                ("yes", "easy",   "any equity based incentive compensation award, including but not limited to options, stock appreciation rights, restricted stock units and performance stock units, shall vest", "GIBRALTAR INDUSTRIES, INC."),
    "1671858_000119312522280241":               ("yes", "easy",   "shall be accelerated such that the amount of shares vested under such Stock Awards shall equal", "Silverback Therapeutics, Inc."),
    "1293310_000119312512306440":               ("yes", "easy",   "vesting acceleration with respect to each option", "KALOBIOS PHARMACEUTICALS INC"),
    "1433714_000119312514041287":               ("yes", "medium", "Double Trigger Acceleration Policy", "CASTLIGHT HEALTH, INC."),
    "1452751_000119312513403444":               ("yes", "medium", "Single Trigger Acceleration", "Nimble Storage Inc"),
    "1108271_000119312504159873":               ("yes", "medium", "accelerated vesting of all unvested shares in the event of a Change of Control", "CONOR MEDSYSTEMS INC"),
    # NO -- no acceleration language (explicit or via fixed schedule only)
    "0001193125-13-046243_d484075d8k":          ("no", "easy",   "shall vest in equal monthly installments over", "YELP INC"),
    "0001451809-24-000052_ex1034offerofemployment-sa": ("no", "easy", "with no cliff", "SiTime Corp"),
    "0000950005-01-500034_p13538ex99-7":        ("no", "easy",   "No accelerated vesting of the Purchased Shares shall occur", "SHARPER IMAGE CORP"),
}
# Excluded (mislabeled / fail-closed, kept here for audit trail, NEVER in oracle):
#   CONOCOPHILLIPS / EXPEDITORS: anchor text is a stockholder PROXY PROPOSAL asking the company to
#     adopt a no-acceleration policy -- it does not state the company's actual equity-plan acceleration
#     terms, so "no" was not grounded in the company's real grant language.
#   BOSTON LIFE SCIENCES: anchor never matched (doc says "monthly installments...subject to accelerated
#     vesting if certain performance goals are achieved" -- contradicts the planned "no" label); already
#     dropped by the fail-closed anchor check in main().


def window_on(text, anchor, before=420, after=900):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 90)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING full text {cid} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": cid, "company": company, "vesting_acceleration": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['vesting_acceleration'] for o in oracle))}")


if __name__ == "__main__":
    main()
