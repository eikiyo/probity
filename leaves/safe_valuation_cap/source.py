"""
Location: leaves/safe_valuation_cap/source.py
Purpose: Build the safe_valuation_cap leaf corpus + oracle (2.1.1) from real SEC EDGAR
         documents. Extract the VALUATION CAP dollar amount (bare integer) stated in
         YC-style SAFE agreements. Reuses 8 documents from sibling safe_pre_post leaf.
Functions: window_on(), main()
Imports: json, re, pathlib
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# Source 8 diverse valuation cap values from real SAFEs in safe_pre_post corpus
# oracle_id -> (read_from_file_id, value, difficulty, anchor, company)
# Anchors are short ASCII-only phrases unique to the cap definition line
ITEMS = {
    "1657493_000121390021028831_cap": (
        "1657493_000121390021028831", 15000000, "easy",
        "is $15,000,000",
        "Rentberry Inc."),
    "1486452_000168316824001414_cap": (
        "1486452_000168316824001414", 20000000, "easy",
        "is $20,000,000",
        "Maison Luxe, Inc."),
    "2036444_000121390025123767_cap": (
        "2036444_000121390025123767", 30000000, "medium",
        "is USD$30,000,000",
        "Neo Aeronautics, Inc."),
    "746210_000143774926019366_cap": (
        "746210_000143774926019366", 40000000, "medium",
        "is $40,000,000",
        "TaoWeave, Inc."),
    "1838987_000121390024014892_cap": (
        "1838987_000121390024014892", 53540000, "medium",
        "is $ 53,540,000",
        "Complete Solaria, Inc."),
    "1900520_000121390024095442_cap": (
        "1900520_000121390024095442", 100000000, "medium",
        "is $100,000,000",
        "Lomond Therapeutics Holdings, Inc."),
    "2010788_000149315224005725_cap": (
        "2010788_000149315224005725", 100000000, "hard",
        "is one-hundred million dollars ($100,000,000",
        "Invizyne Technologies Inc"),
    "1811623_000110465922070160_cap": (
        "1811623_000110465922070160", 150000000, "hard",
        "is $150,000,000",
        "PaxMedica, Inc."),
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
    # Use corpus/full from sibling safe_pre_post leaf
    SAFE_PRE_POST_FULL = HERE.parent / "safe_pre_post" / "corpus" / "full"
    
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    
    for oid, (read_from, value, diff, anchor, company) in ITEMS.items():
        p = SAFE_PRE_POST_FULL / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING full text {read_from} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "safe_valuation_cap": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items | values={sorted([o['safe_valuation_cap'] for o in oracle])}")


if __name__ == "__main__":
    main()
