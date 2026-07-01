"""
Location: leaves/antidilution_base/source.py
Purpose: Build the antidilution_base leaf corpus + SEPARATED oracle (1.5.2) by REUSING
         the already-fetched SEC charter corpus from leaves/antidilution_type/corpus/full.
         For each charter labeled "weighted-average" in the sibling leaf, read the full
         anti-dilution article and classify the share base as broad-based, narrow-based,
         or n/a (for full-ratchet and none structures). SEPARATED oracle pattern: each
         item hand-verified against the REAL denominator-definition text in the charter.
Functions: window_on(), main()
Calls: antidilution_type full-text corpus
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE.parent / "antidilution_type" / "corpus" / "full"

# id -> (value, difficulty, anchor, company)
# Hand-verified by reading the REAL anti-dilution denominator definition in each charter.
# Anchor = short phrase, exact case will be found case-insensitively by window_on().
ITEMS = {
    # ===== BROAD-BASED (denominator includes all outstanding common + all convertible securities)
    '1082733_000165495426003578': ('broad-based', 'medium', 'broad-based weighted', 'VISIUM TECHNOLOGIES, INC.  (VISM)  (CIK 0001082733)'),
    '1103078_000119312505072191': ('broad-based', 'medium', 'broad-based weighted average', 'RASER TECHNOLOGIES INC  (CIK 0001103078)'),
    '1090908_000143774913006947': ('broad-based', 'hard', 'Series C Stock is subject to broad-based weighted-average anti-dilution', 'SELECTICA INC  (CIK 0001090908)'),
    '842010_000095013507006022': ('broad-based', 'hard', 'Series C Preferred Stock contains broad-based weighted-average', 'UTIX GROUP INC  (CIK 0000842010)'),

    # ===== NARROW-BASED (denominator is only outstanding common stock, excludes options/warrants/convertibles)
    '1108699_000101968704002883': ('narrow-based', 'medium', 'narrow based weighted', 'uWink, Inc.  (CIK 0001108699)'),
    '1627480_000121390015005091': ('narrow-based', 'hard', 'narrow-based weighted', 'PV Nano Cell, Ltd.  (PVNNF)  (CIK 0001627480)'),
    '1752234_000114420418064195': ('narrow-based', 'medium', 'narrow-based weighted', 'YX Asset Recovery Ltd  (CIK 0001752234)'),
    '1800315_000095012320009492': ('narrow-based', 'hard', 'narrow-based weighted', 'Galecto Inc.  (GLTO)  (CIK 0001800315)'),

    # ===== N/A (charter uses full-ratchet or has no anti-dilution protection)
    '1093207_000114420414015857': ('n/a', 'medium', 'full ratchet', 'CROSSROADS SYSTEMS INC  (CIK 0001093207)'),
    '1161315_000095012314003249': ('n/a', 'medium', 'full ratchet', 'YODLEE INC  (CIK 0001161315)'),
    '763901_000095012310045398': ('n/a', 'easy', 'no anti-dilution', 'POPULAR INC  (BPOP, BPOPM, BPOPO)  (CIK 0000763901)'),
}
# Excluded (audit caught issues — these documents are correct but excluded from this leaf per rules):
#   1408057 (Vemics): "Investor Shares" / "Broad-Based Weighted Average Price" but NOT preferred-stock
#     language; cannot confirm this is a preferred-stock charter clause (instrument type uncertain).
#   1075066, 1125294, 1316925, 1434647, 1549084, 33113: unclear contexts (e.g., convertible notes
#     rather than preferred stock charters, or language too ambiguous to read the actual formula).
#   CROSS MEDIA, VOIP INC, XERIANT, LEAP THERAPEUTICS: anti-dilution on WARRANTS/convertible NOTES,
#     not preferred stock — wrong instrument.
#   VIE FINANCIAL GROUP (1003740): 'Final and Optional Conversions' + 'Additional Financing' —
#     convertible-debenture language, not a preferred-stock charter denominator; wrong instrument.
#   DIGITAL LIGHTWAVE (1016100): clause reads 'Borrower issues additional equity securities' —
#     loan-agreement/promissory-note anti-dilution, not preferred stock; wrong instrument.
#   CUR MEDIA (1556226): validating text is explicitly 'anti-dilution provisions contained in the
#     Original Warrants' — warrant anti-dilution, not preferred-stock charter; wrong instrument.
#   (Independent audit caught these 3 after the agent's own self-report missed them — M3.1.)
#   CROSS MEDIA MARKETING (1069201): both weighted-average mentions are Warrant/conditional-exchange
#     language, not a clean preferred-stock charter clause; excluded (ambiguous instrument).
#   CADIZ INC (727273): both mentions are New Secured Convertible Loan / Warrant anti-dilution —
#     debt instrument, not preferred stock; wrong instrument, excluded.
#   BOSTON LIFE SCIENCES (94784): Series E preferred clause states 'weighted average anti-dilution
#     formula' with NO broad/narrow qualifier anywhere in the document — genuinely underspecified
#     for this field (fine for the parent antidilution_type leaf, not for this one); excluded.
#   SELECTICA (1090908) and UTIX (842010) each have a Preferred-Stock clause AND a separate Warrant
#     clause with the same wording — anchor narrowed to the exact Preferred Stock sentence in both.


def window_on(text, anchor, before=600, after=1200):
    """Find anchor in text (case-insensitive), extract window, return (window, validating_quote)."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    # validating quote: ~sentence around the anchor
    qs = max(0, i - 20)
    qe = min(len(text), i + len(anchor) + 120)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING full text {cid} -- skip")
            continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) -- skip (fail-closed)")
            continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": cid, "company": company, "antidilution_base": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    dist = dict(Counter(o['antidilution_base'] for o in oracle))
    print(f"wrote {len(oracle)} items  {dist}")


if __name__ == "__main__":
    main()
