"""
Location: leaves/safe_discount_rate/source.py
Purpose: Build safe_discount_rate leaf corpus + oracle (2.1.2) from real SEC EDGAR SAFE docs.
         NUMBER extraction: discount rate % stated in SAFE. For "100 minus X%", extract X;
         for "is Y%", extract discount (100-Y if 70-90%, else Y).
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
    "manako_20": (
        "746210_000143774926019366", 20, "easy",
        "80% (representing a 20% discount to the price",
        "Manako Labs Ltd"),
    "eighty_20": (
        "1821951_000121390022000982", 20, "medium",
        "is Eighty Percent (80%)",
        "Creci Inc."),
    "80pct_20": (
        "1838987_000121390024014892", 20, "easy",
        "is 80%. See Section 2 for certain",
        "Complete Solaria, Inc."),
    "ninety_10": (
        "1900520_000121390024095442", 10, "hard",
        "is 90%.",
        "Lomond Therapeutics Holdings, Inc."),
    "50pct_2": (
        "2036444_000121390025123767", 50, "medium",
        "is 50%.",
        "Neo Aeronautics, Inc."),
    "80pct_2": (
        "1486452_000168316824001414", 20, "easy",
        "is 80%",
        "Maison Luxe, Inc."),
    "fifty_50_1": (
        "0000721748-17-000529_s1safe", 50, "medium",
        "is fifty percent (50%)",
        "SNM Global Holdings, Inc."),
    "85pct_15": (
        "0001493152-22-024010_ex3-3", 15, "medium",
        "is 85%.",
        "Parker Clay Global, PBC"),
    "sos_50": (
        "0001721868-21-000866_filename15", 50, "hard",
        "100 minus 50%",
        "SOS Hydration Inc."),
}
# Excluded (audit caught placeholder/duplicate issues, kept for trail, NEVER in oracle):
#   fifty_50_2 (0000721748-17-000577_s1safe): a SECOND S-1 exhibit filed by the SAME company (SNM
#     Global Holdings) restating the identical SAFE template -- duplicate of fifty_50_1, not an
#     independent data point.
#   minus_50_2 (0001903596-22-000170): confirmed via document text to ALSO be SOS Hydration Inc.
#     (same "100 minus 50%" SAFE template, refiled in a later registration statement) -- duplicate
#     of sos_50, not independent.


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
            print(f"MISSING {read_from}"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} -- skip"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "safe_discount_rate": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['safe_discount_rate'] for o in oracle))}")


if __name__ == "__main__":
    main()
