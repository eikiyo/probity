"""
Location: leaves/cliff_present/source.py
Purpose: Build the cliff_present leaf corpus + SEPARATED oracle (6.2) from real SEC EDGAR documents
         (raw candidates pre-fetched by a parallel agent into corpus/full/ + candidates_*.jsonl; this
         script is the MANUAL oracle pass -- each item was READ and hand-classified against the real
         document text by a human). YES = an explicit cliff blockage period. NO = no cliff (immediate
         or pure-periodic vesting, OR an implicit equal-annual-from-year-one schedule, OR a TRAP where
         the operative text WAIVES a cliff requirement).
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
    # YES -- explicit cliff blockage period
    "0001503707-23-000002_ltipformfinalforedgar": ("yes", "easy",   "Cliff Vesting Date", "NorthStar Healthcare Income, Inc."),
    "0001558370-21-008713_giii-20210628x8k":      ("yes", "easy",   "Cliff-Vesting RSUs", "G-III Apparel Group, Ltd."),
    "0000790816-14-000054_bdn8k-annualawards_031414": ("yes", "easy", "Cliff-Vesting Restricted Shares", "Brandywine Realty Trust"),
    "0001144204-18-050119_tv502422_10k":          ("yes", "medium", "one year cliff vesting period", "Research Solutions, Inc."),
    "0001299933-11-000951_htm_41195":             ("yes", "medium", "cliff vesting) for executives", "Viad Corp"),
    "0001104659-09-039164_a09-16464_1ex10d1":     ("yes", "medium", "Cliff Vesting Award", "Interval Leisure Group, Inc."),
    # NO -- explicit no-cliff / immediate vesting
    "0001451809-24-000052_ex1034offerofemployment-sa": ("no", "easy", "no cliff", "SiTime Corp"),
    "0001144204-15-053727_v419640_ex10-1":        ("no", "easy", "no cliff", "Atossa Genetics Inc."),
    "0001516513-23-000036_ex-107xcraigoverpeckofferl": ("no", "easy", "no cliff", "Doximity, Inc."),
    "0001299933-05-001251_exhibit2":              ("no", "medium", "vest immediately", "Plato Learning, Inc."),
    # NO -- implicit (equal-annual-from-year-one, no upfront blockage)
    "0000020740-17-000006_a201610kex1012":        ("no", "hard", "shall vest on each anniversary", "Clarcor Inc."),
    # NO -- TRAP: operative text WAIVES a cliff requirement
    "0001104659-09-054183_a09-26145_18k":         ("no", "hard", "waiver of one-year cliff", "World Heart Corp"),
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
    for cid, (label, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING full text {cid} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": cid, "company": company, "cliff_present": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['cliff_present'] for o in oracle))}")


if __name__ == "__main__":
    main()
