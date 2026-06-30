"""
Location: leaves/participation_cap/source.py
Purpose: Build the participation_cap leaf corpus + oracle (1.3.3) from real SEC EDGAR documents.
         NUMBER extraction: each item's ground truth is the numeric cap multiple for a capped
         participating-preferred clause, hand-verified against the real clause text.
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
    "1200720_000104746904001493": (
        "1200720_000104746904001493", 3.5, "medium",
        "until the Preferred Stockholders have received 3.5 times",
        "Jazz Semiconductor Inc"),
    "1447599_000119312515209758": (
        "1447599_000119312515209758", 3, "hard",
        "Participation Cap Amount",
        "Fitbit Inc"),
    "1344413_000089161805000914": (
        "1344413_000089161805000914", 3, "medium",
        "until such time as the holders of Preferred Stock have received",
        "Alexza Pharmaceuticals Inc."),
}
# Excluded (audit caught mislabel/ambiguity, kept for trail, NEVER in oracle):
#   Medicines Co (Rempex): "Maximum Participation Amount" is a FLAT PER-SHARE DOLLAR cap
#     ($3.00/sh Series A, $3.15/sh Series B), not a multiple of Original Issue Price -- wrong
#     mechanism for this field, the agent misread "$3.00" as "3x".
#   Workday, Inc.: the same excerpt the model would see states THREE different caps in one
#     passage (Series E=3x, Series A/B/C/D/F=2x, Series G=1x) with no signal which series the
#     question targets -- genuinely ambiguous, not a clean single-answer item.


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
        oracle.append({"id": oid, "company": company, "participation_cap": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['participation_cap'] for o in oracle))}")


if __name__ == "__main__":
    main()
