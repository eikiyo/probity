"""
Location: leaves/dividend_rate_pct/source.py
Purpose: Build the dividend_rate_pct leaf corpus + SEPARATED oracle (1.4.1) from real SEC EDGAR
         documents (raw candidates fetched into corpus/full/). NUMBER extraction: each item's ground
         truth is the annual dividend rate percentage stated in the preferred stock charter's
         dividend clause, hand-verified against the real clause text. Oracle values are bare numbers
         (not strings), e.g. 5.1 or 8, with NO percent sign.
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
# Values are BARE NUMBERS (int/float), NOT strings with "%"
ITEMS = {
    "f02955exv4w8_5p1": (
        "f02955exv4w8.htm", 5.1, "easy",
        "non-cumulative, cash dividends at the annual rate of 5.1%",
        "Freddie Mac 5.1% Non-Cumulative Preferred Stock"),

    "f02955exv4w7_5p3": (
        "f02955exv4w7.htm", 5.3, "easy",
        "non-cumulative, cash dividends at the annual rate of 5.3%",
        "Freddie Mac 5.3% Non-Cumulative Preferred Stock"),

    "f02955exv4w4_5p0": (
        "f02955exv4w4.htm", 5.0, "easy",
        "non-cumulative, cash dividends at the annual rate of 5%",
        "Freddie Mac 5% Non-Cumulative Preferred Stock"),

    "f02955exv4w17_5p81": (
        "f02955exv4w17.htm", 5.81, "easy",
        "non-cumulative, cash dividends at the annual rate of 5.81%",
        "Freddie Mac 5.81% Non-Cumulative Preferred Stock"),

    "f02955exv4w25_7p875": (
        "f02955exv4w25.htm", 7.875, "medium",
        "7.875% per annum, with the resulting dividend per share",
        "Freddie Mac 7.875% Fixed-to-Floating Rate Non-Cumulative Preferred Stock"),

    "bacmarch8k1_6p75": (
        "bacmarch8k1.htm", 6.75, "medium",
        "rate of 6.75% per annum , payable quarterly",
        "Bank of America 6.75% Perpetual Preferred Stock"),

    "bacmarch8k1_6p6": (
        "bacmarch8k1.htm", 6.6, "medium",
        "rate of 6.60% per annum computed on the basis of the issue price",
        "Bank of America 6.60% Fixed/Adjustable Rate Cumulative Preferred Stock"),

    "fixed1_6p6": (
        "fixed1.htm", 6.6, "medium",
        "6.60% per annum computed on the basis of an issue price thereof of $250 per share",
        "Bank of America Fixed/Adjustable Rate Cumulative Preferred Stock"),

    "dex31_5p0": (
        "dex31.htm", 5.0, "hard",
        "not greater than 5.00% per annum or greater than 11.50% per annum",
        "Adjustable Rate Preferred Stock (5.00% floor)"),

    "dex31_11p5": (
        "dex31.htm", 11.5, "hard",
        "than 11.50% per annum. Except as provided below",
        "Adjustable Rate Preferred Stock (11.50% ceiling)"),

    "exhibit46_6p35": (
        "exhibit46-q42023.htm", 6.35, "medium",
        "6.350% Fixed-to-Floating Rate Non-Cumulative Perpetual Preferred Stock",
        "Company Fixed-to-Floating Rate Non-Cumulative Perpetual Preferred Stock"),
}


def window_on(text, anchor, before=420, after=900):
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
    skipped = []

    for oid, (read_from, value, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{read_from}.txt"
        if not p.exists():
            skipped.append((oid, f"file {read_from} not found"))
            continue

        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)

        if not win:
            skipped.append((oid, f"anchor not found in {read_from}"))
            continue

        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")

        oracle.append({
            "id": oid,
            "company": company,
            "dividend_rate_pct": value,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    values_count = dict(Counter(o['dividend_rate_pct'] for o in oracle))
    print(f"wrote {len(oracle)} items; values={values_count}")
    if skipped:
        print(f"skipped {len(skipped)} items:")
        for oid, reason in skipped:
            print(f"  {oid}: {reason}")


if __name__ == "__main__":
    main()
