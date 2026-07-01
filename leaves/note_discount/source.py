"""
Location: leaves/note_discount/source.py
Purpose: Build the note_discount leaf corpus + SEPARATED oracle (2.2.5) from real SEC EDGAR
         documents. NUMBER extraction: each item's ground truth is the conversion discount
         rate (percentage) stated on a convertible promissory note that converts at a discount
         to the price paid by new investors in a subsequent qualified financing (e.g., "80% of
         the price" = 20% discount; "75% of the price" = 25% discount).
Functions: main()
Calls: engine.corpus_utils.window_on
Imports: json, pathlib, collections, sys
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from corpus_utils import window_on  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# oracle_id -> (read_from_file_id, discount_value, difficulty, anchor, company)
# DISCOUNT_VALUE is the bare number representing the discount percentage (e.g., 20.0, 25.0)
# Note: Not all convertible notes have an explicit discount mechanic (some are cap-only or
# interest-only); this leaf extracts ONLY notes that state a conversion discount.
ITEMS = {
    "greenfield_robotics_20pct": (
        "tm2617498d1_ex3-8",
        20.0,
        "easy",
        "conversion price equal to the lesser of (i) the cash price paid per share for Equity Securities by the Investors in the Qualified Financing multiplied by 0.80",
        "Greenfield Robotics Corporation"
    ),
    "exyn_technologies_25pct": (
        "tm2525579d10_ex10-26",
        25.0,
        "easy",
        "the lesser of (i) the public offering price per share of Common Stock offered by the Company the IPO multiplied by 0.75",
        "Exyn Technologies, Inc."
    ),
    "acology_50pct": (
        "000072174814000435_pncr050514s1ex104",
        50.0,
        "easy",
        "shall be fifty percent (50%) of the Current Market Price",
        "ACOLOGY, INC."
    ),
    "hepalife_5pct_vwap": (
        "000105427407000020_exhibit49note",
        5.0,
        "medium",
        "equal to 95% of the volume weighted average prices",
        "HepaLife Technologies, Inc."
    ),
}


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []

    for oid, (read_from, value, diff, anchor, company) in ITEMS.items():
        # Try multiple possible file extensions
        found = False
        for ext in ["", ".txt", ".htm", ".html"]:
            p = FULL / f"{read_from}{ext}.txt"
            if p.exists():
                found = True
                full = p.read_text(errors="ignore")
                break

        if not found:
            print(f"MISSING full text {read_from} -- skip"); continue

        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor[:50]!r}) -- skip (fail-closed)"); continue

        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({
            "id": oid,
            "company": company,
            "note_discount": value,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    print(f"wrote {len(oracle)} items  values={sorted(set(o['note_discount'] for o in oracle))}")


if __name__ == "__main__":
    main()

# Excluded items (audit trail):
#   Not all convertible promissory notes include a discount mechanic; some rely solely on:
#   - Valuation cap (cap on conversion price ceiling)
#   - Interest rate (fixed coupon)
#   - Warrant coverage (separate warrant issuance)
#   Only notes with an EXPLICIT discount clause (typically "multiplied by 0.XX" pattern,
#   or percentage-of-price language like "95% of VWAP") are included here.
#
#   Future expansion note: Full corpus sourcing would require additional SEC EDGAR searches
#   targeting discount rates to expand from current 4 items toward 10+ target:
#   - 15% discount (0.85 factor), 30% discount (0.70 factor) are common VC standards
#   - Multi-country convertible notes (less common outside US venture financing)
#   - SAFE discount rates (different instrument family, stored in safe_discount_rate leaf)
