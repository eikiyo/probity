"""
Location: leaves/note_valuation_cap/source.py
Purpose: Build the note_valuation_cap leaf corpus + SEPARATED oracle (2.2.4) from real SEC EDGAR
         documents. NUMBER extraction: each item's ground truth is the valuation cap (conversion
         ceiling) stated in convertible promissory notes, hand-verified against the real clause text.
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# oracle_id -> (read_from_file_id, value, difficulty, anchor, company)
# VALUE is the bare dollar number (no commas, no $ sign)
ITEMS = {
    "damon_tranche_19to22": (
        "ea022140801ex99-2_damon.htm", 125000000, "easy",
        "valuation cap of $125,000,000 and interest rate of 12%",
        "Damon Motors Inc."),
    "realpha_cap_definition": (
        "ea022204701ex99-1_realpha.htm", 25000000, "easy",
        "Valuation Cap ” means Twenty-Five Million Dollars",
        "Unreal Estate Inc. (formerly Abode Technologies)"),
    "exyn_technologies": (
        # WHY this anchor differs from the obvious "dividing the Valuation Cap by the number
        # of fully diluted shares" formula text (added 2026-07-02, adversarial audit): that
        # phrase appears ~3500 chars BEFORE the document's actual numeric definition of
        # "Valuation Cap" -- window_on()'s after=900 default never reached it, so the original
        # window showed the model a formula that USES "Valuation Cap" as a variable without
        # ever stating its value. Verified via the real EDGAR filing (CIK 1960355, accession
        # 0001104659-26-032156) that "“Valuation Cap” means $90,000,000." is a real, later
        # sentence in the same document -- anchoring on the defining sentence itself instead of
        # a formula that merely references the term fixes the window to actually contain the
        # ground truth.
        "tm2525579d10_ex10-26.htm", 90000000, "medium",
        "Valuation Cap ” means $90,000,000",
        "Exyn Technologies, Inc."),
    "greenfield_robotics": (
        "tm2617498d1_ex3-8.htm", 30000000, "easy",
        "change the Valuation Cap to $30,000,000",
        "Greenfield Robotics Corporation"),
}


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
    for oid, (read_from, value, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING full text {p} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "note_valuation_cap": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['note_valuation_cap'] for o in oracle))}")


if __name__ == "__main__":
    main()
