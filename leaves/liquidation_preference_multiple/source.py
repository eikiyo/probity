"""
Location: leaves/liquidation_preference_multiple/source.py
Purpose: Build the liquidation_preference_multiple leaf corpus + SEPARATED oracle (1.3.1) from
         real SEC EDGAR preferred-stock charter clauses (refetched into corpus/full/ from the
         stored URLs). Each item hand-verified: the stated multiple of the Original Issue Price
         a preferred holder receives upon liquidation (1x market-standard, 2x/3x off-market).
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# id -> (value, difficulty, anchor, company)
ITEMS = {
    '1236997_000106299308001834': ('1x', 'easy', 'one (1)', 'COUNTERPATH CORP  (CIK 0001236997)'),
    # NOTE (2026-07-02, adversarial audit, Eikiyo-confirmed): dropped the sibling
    # '1283259_000149315225027406' item -- byte-for-byte identical "First Amendment to the
    # Third Amended and Restated Certificate of Incorporation" text as this one, just filed
    # under a different accession number (the same amendment attached to two periodic
    # filings). Kept the earlier accession as the single representative. See AUDIT_TODO.md.
    '1283259_000149315225016953': ('1x', 'easy', 'one (1)', 'BIOVENTRIX, INC.  (CIK 0001283259)'),
    '1479290_000119312514020967': ('1x', 'easy', 'one (1)', 'Revance Therapeutics, Inc.  (RVNC)  (CIK 0001479290)'),
    '1130258_000104746906010148': ('2x', 'easy', 'liquidation preference of $2.89', 'ACME PACKET INC'),
    '1427222_000101376208000358': ('2x', 'easy', 'the amount of $44.44', 'HQHEALTHQUEST MEDICAL & WELLNESS CENTERS'),
    '1461993_000119312517361673': ('2x', 'easy', 'liquidation preference equal to two times', 'MELINTA THERAPEUTICS, INC. /NEW/'),
    '1538716_000119312519245313': ('2x', 'easy', 'two (2) times the Original Issue Price', 'Oportun Financial Corp  (OPRT)  (CIK 0001538716)'),
    # NOTE (2026-07-02, adversarial audit, Eikiyo-confirmed): dropped the 2 sibling Pagaya
    # items ('...25000050', '...26000018') -- identical validating_quote/clause text across
    # all 3, just re-filed under different accession numbers over 3 periodic filings. Kept
    # the earliest as the single representative. See AUDIT_TODO.md.
    '1883085_000188308524000060': ('2x', 'easy', 'two (2) times the Original Issue Price', 'Pagaya Technologies Ltd.  (PGY, PGYWW)  (CIK 0001883085)'),
    '1904616_000121390023031361': ('2x', 'easy', 'two (2) times the Original Issue Price', 'Baker Global Asset Management Inc.  (BAKR)  (CIK 0001904616)'),
    '1062195_000110465903012203': ('3x', 'easy', 'three (3)', '24/7 REAL MEDIA INC  (CIK 0001062195)'),
    '1274991_000119312510075918': ('3x', 'easy', 'three (3)', 'BECEEM COMMUNICATIONS INC  (CIK 0001274991)'),
    # NOTE (2026-07-02, adversarial audit, Eikiyo-confirmed): dropped the sibling
    # '1447362_000114036119012901' item -- identical validating_quote/clause text as this
    # one, different accession number. Kept the earlier accession. See AUDIT_TODO.md.
    '1447362_000114036119009024': ('3x', 'easy', 'three (3)', 'CASTLE BIOSCIENCES INC  (CSTL)  (CIK 0001447362)'),
    '877931_000119312508100740': ('3x', 'easy', 'an amount equal to three times', 'Vertical Communications, Inc.'),
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
        oracle.append({"id": cid, "company": company, "liquidation_preference_multiple": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['liquidation_preference_multiple'] for o in oracle))}")


if __name__ == "__main__":
    main()