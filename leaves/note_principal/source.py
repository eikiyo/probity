"""
Location: leaves/note_principal/source.py
Purpose: Build the note_principal leaf corpus + SEPARATED oracle (2.2.1) from real SEC EDGAR
         documents (raw candidates fetched into corpus/full/). NUMBER extraction: each item's ground
         truth is the principal amount of a convertible promissory note, hand-verified against the real
         clause text.
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
ITEMS = {
    "0007217481400043_acology": (
        "000072174814000435_pncr050514s1ex104",
        400000,
        "easy",
        "principal amount of FOUR HUNDRED THOUSAND AND NO/100 DOLLARS (US$400,000.00)",
        "ACOLOGY, INC."
    ),
    "0008929170200000_gardenburger": (
        "000089291702000003_gbamnote",
        17364375,
        "easy",
        "principal amount of Seventeen Million Three Hundred Sixty Four Thousand Three Hundred Seventy Five dollars ($17,364,375)",
        "GARDENBURGER, INC."
    ),
    "0001125282060068_sedona": (
        "000112528206006873_b415608_ex10-82",
        500000,
        "medium",
        "New Vey Note includes in aggregate principal amount accrued interest",
        "SEDONA CORPORATION"
    ),
    "0001213900170072_minerco_ciarello": (
        "000121390017007223_f8k043016_minercoinc",
        12500,
        "easy",
        "Convertible Promissory Note, dated February 23, 2016, in principal amount of $12,500",
        "MINERCO, INC. (Ciarello)"
    ),
    "0001213900170072_minerco_schmidt": (
        "000121390017007223_f8k043016_minercoinc",
        12500,
        "easy",
        "Convertible Promissory Note, dated March 8, 2016, in principal amount of $12,500",
        "MINERCO, INC. (Schmidt)"
    ),
    "0001213900170072_minerco_msf": (
        "000121390017007223_f8k043016_minercoinc",
        350000,
        "easy",
        "Promissory Note, with original principal amount of Three Hundred and Fifty Thousand Dollars ($350,000)",
        "MINERCO, INC. (MSF)"
    ),
    "0001213900170072_minerco_rios": (
        "000121390017007223_f8k043016_minercoinc",
        100000,
        "medium",
        "with principal amount of $100,000 and due on November 1, 2016",
        "MINERCO, INC. (Rios)"
    ),
    "0001213900170072_minerco_pacific_isle": (
        "000121390017007223_f8k043016_minercoinc",
        250000,
        "easy",
        "Promissory Note to Buyer in principal amount of Two Hundred and Fifty Thousand Dollars (US$250,000)",
        "MINERCO, INC. (Pacific Isle)"
    ),
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
            print(f"MISSING full text {read_from} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor[:50]!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "note_principal": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['note_principal'] for o in oracle))}")


if __name__ == "__main__":
    main()

# Excluded (audit caught multi-value ambiguity, kept for trail, NEVER in oracle):
#   minerco_saad: the same excerpt the model would see lists TWO notes (#1 $25,000, #2 $10,000)
#     with no signal which one the question targets.
#   minerco_messina: the same excerpt lists FIVE different notes ($52,500/$37,500 x3/$25,000) with
#     no signal which one the question targets.
