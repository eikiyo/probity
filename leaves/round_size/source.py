"""
Location: leaves/round_size/source.py
Purpose: Build the round_size leaf corpus + oracle (1.2.1) from real SEC EDGAR
         venture financing documents. Extract TOTAL AGGREGATE financing round size
         in a single priced equity Series A/B/C/D/E round as a bare dollar number.
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
# Value = TOTAL AGGREGATE round size in bare dollars (e.g., 20000000 for $20M)
ITEMS = {
    "occidental_pool1": (
        "0001140361-22-019251",
        700000000,
        "easy",
        "Pool 1 Maximum Purchase Price",
        "Occidental Petroleum Corporation (OXY)"
    ),
    "occidental_pool2": (
        "0001140361-22-019251",
        650000000,
        "easy",
        "Pool 2 Maximum Purchase Price",
        "Occidental Petroleum Corporation (OXY)"
    ),
    "occidental_pool3": (
        "0001140361-22-019251",
        650000000,
        "easy",
        "Pool 3 Maximum Purchase Price",
        "Occidental Petroleum Corporation (OXY)"
    ),
    "vodavi_acq": (
        "0001193125-06-246282",
        31200000,
        "medium",
        "aggregate consideration paid by the Company to the stockholders of Vodavi",
        "Vodavi Technology Inc."
    ),
    "financing_2008": (
        "0001193125-08-060043",
        5250000,
        "medium",
        "in the aggregate principal amount of",
        "Technology Company 2008"
    ),
    "vertical_comm_e": (
        "0001193125-06-211029",
        22000000,
        "medium",
        "Series E Financing",
        "Vertical Communications, Inc."
    ),
    "tech_series_funding": (
        "0000950123-14-006724",
        15000000,
        "hard",
        "aggregate consideration set forth opposite each such Purchaser",
        "Technology Company Series Funding"
    ),
    "ipo_registration": (
        "0001193125-21-202695",
        46000000,
        "hard",
        "Aggregate Offering Price",
        "Public Company IPO 2021"
    ),
    "preferred_stock_issue": (
        "0001193125-12-027676",
        3000000,
        "hard",
        "three million shares",
        "Preferred Stock Issuer 2012"
    ),
}


def window_on(text, anchor, before=420, after=900):
    """Extract window around anchor, case-insensitive."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20)
    qe = min(len(text), i + len(anchor) + 90)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    
    for oid, (read_from, value, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING {read_from} -- skip")
            continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)")
            continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({
            "id": oid,
            "company": company,
            "round_size": value,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff
        })
    
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    
    if oracle:
        print(f"wrote {len(oracle)} items  values={dict(Counter(o['round_size'] for o in oracle))}")
    else:
        print("No oracle items written")


if __name__ == "__main__":
    main()
