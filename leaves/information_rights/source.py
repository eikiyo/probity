"""
Location: leaves/information_rights/source.py
Purpose: Build the information_rights leaf corpus + SEPARATED oracle (5.3) from real SEC EDGAR
         documents (raw candidates pre-fetched by a parallel agent into corpus/full/ +
         candidates_*.jsonl; this script is the MANUAL oracle pass -- each item was READ and
         hand-classified against the real document text by a human). YES = a live financial-delivery
         obligation. NO = no such covenant, or a TRAP where the operative text WAIVES delivery.
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
    # YES -- a live financial-statement delivery obligation
    "0001193125-11-204682_dex402":          ("yes", "easy",   "4. Information Rights", "Vocera Communications, Inc."),
    "0000950123-09-064388_f53797orexv4w2":  ("yes", "easy",   "Deliver to each Major Investor", "QuinStreet, Inc."),
    "0000950123-14-010038_filename6":       ("yes", "medium", "deliver the following annual financial statements", "Entellus Medical Inc."),
    "0000950123-20-004953_filename4":       ("yes", "medium", "3.1 Delivery of Financial Statements", "Fusion Pharmaceuticals Inc."),
    "0001628280-21-019876_exhibit102-sx1":  ("yes", "medium", "AMENDMENT OF INVESTORS", "NerdWallet, Inc."),
    "0000950134-08-014307_f42787exv10w2":   ("yes", "hard", "financial statements", "Bell Microproducts Inc."),
    # NO -- no information-rights covenant at all (different doc genre: employee restricted stock)
    "0001193125-06-212415_dex991":          ("no", "easy", "FORM OF RESTRICTED STOCK AGREEMENT", "Speedway Motorsports, Inc."),
    "0001193125-07-042724_dex101":          ("no", "easy", "RESTRICTED STOCK AGREEMENT PLAN", "TSFG (The South Financial Group)"),
    "0000945841-07-000055_restrstockagreement": ("no", "easy", "RESTRICTED STOCK AGREEMENT", "Pool Corp"),
    "0001193125-15-060049_d836724dex1031":  ("no", "easy", "RESTRICTED STOCK AGREEMENT", "Huron Consulting Group Inc."),
    "0000898173-20-000007_orly-20191231ex101926dba": ("no", "easy", "RESTRICTED STOCK", "O'Reilly Automotive, Inc."),
    # NO -- TRAP: operative text WAIVES the delivery requirement
    "0000950134-06-004765_c01111s1exv4w4":  ("no", "hard", "WAIVER TO INVESTORS' RIGHTS AGREEMENT", "Restore Medical Inc."),
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
        oracle.append({"id": cid, "company": company, "information_rights": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['information_rights'] for o in oracle))}")


if __name__ == "__main__":
    main()
