"""
Location: leaves/option_strike_409a/source.py
Purpose: Build the option_strike_409a leaf corpus + oracle (6.4) from real SEC EDGAR
         documents (raw candidates fetched into corpus/full/). NUMBER extraction: each item's
         ground truth is the strike price (exercise price per share) stated in a stock option
         grant agreement or notice of grant, hand-verified against the real clause text and
         extracted as a bare number (e.g. 2.31 for "$2.31 per share"). This price is the
         fair market value set per IRS 409A valuation rules for the grant date.
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
    "0001125282-06-006236_0p03": (
        "0001125282-06-006236_p413913_s1b.htm", 0.03, "easy",
        "exercise price of $0.03 per share",
        "Medecision, Inc."),
    "0001125282-06-006236_0p25": (
        "0001125282-06-006236_p413913_s1b.htm", 0.25, "easy",
        "exercise price of $0.25 per share",
        "Medecision, Inc."),
    "0001193125-11-194811_0p61": (
        "0001193125-11-194811_ds1a.htm", 0.61, "easy",
        "exercise price of $0.61 per share",
        "WhiteGlove Health, Inc."),
    "0001125282-06-006236_1p25": (
        "0001125282-06-006236_p413913_s1b.htm", 1.25, "medium",
        "exercise price of $1.25 per share",
        "Medecision, Inc."),
    "0001125282-06-007804_2p0": (
        "0001125282-06-007804_b413913_s1a.htm", 2.0, "medium",
        "exercise price of $2.00 per share",
        "Medecision, Inc."),
    "0001193125-11-194811_7p5": (
        "0001193125-11-194811_ds1a.htm", 7.5, "medium",
        "exercise price of $7.50 per share",
        "WhiteGlove Health, Inc."),
    "0001125282-06-006236_11p0": (
        "0001125282-06-006236_p413913_s1b.htm", 11.0, "medium",
        "exercise price of $11.00 per share",
        "Medecision, Inc."),
    "0000950134-05-023857_19p85": (
        "0000950134-05-023857_d31494exv99w2.htm", 19.85, "medium",
        "exercise price per share of LGI Series B Stock purchasable upon exercise of the Series B/A Option is $19.85 and",
        "Liberty Global, Inc. - Option Grant"),
    "0000950134-05-023857_40p3": (
        "0000950134-05-023857_d31494exv99w2.htm", 40.3, "hard",
        "established the exercise prices of the LMI Option at $40.30 per share of LMI Series B Stock and",
        "Liberty Media International, Inc. - Option Grant"),
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
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "option_strike_409a": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={sorted(set(o['option_strike_409a'] for o in oracle))}")


if __name__ == "__main__":
    main()
