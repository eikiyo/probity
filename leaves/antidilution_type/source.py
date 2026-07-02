"""
Location: leaves/antidilution_type/source.py
Purpose: Build the antidilution_type leaf corpus + SEPARATED oracle (1.5.1) from real SEC EDGAR
         preferred-stock charter clauses. Each item hand-verified: the PRIMARY anti-dilution
         mechanism type (full-ratchet vs weighted-average vs broad-based vs narrow-based vs none).
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
# Hand-curated from real EDGAR documents; every anchor verified in the fetched full text.
ITEMS = {
    '1082733_000165495426003578': ('weighted-average', 'medium', 'broad-based weighted', 'VISIUM TECHNOLOGIES, INC.  (VISM)  (CIK 0001082733)'),
    '1093207_000114420414015857': ('full-ratchet', 'medium', 'full ratchet', 'CROSSROADS SYSTEMS INC  (CIK 0001093207)'),
    '1103078_000119312505072191': ('weighted-average', 'medium', 'weighted average', 'RASER TECHNOLOGIES INC  (CIK 0001103078)'),
    '1161315_000095012314003249': ('full-ratchet', 'medium', 'full ratchet', 'YODLEE INC  (CIK 0001161315)'),
    # replaced 2026-07-02 (adversarial audit, Eikiyo-confirmed): the old 'none' item, POPULAR INC
    # (763901_000095012310045398), is a large public Puerto Rico BANK holding company off-thesis
    # for a VC/startup-financing benchmark (TARP-era depository-share rights/warrant clause, not
    # a preferred-stock financing charter). Replaced with a genuine growth-company Series A
    # Preferred Stock Certificate of Designations (real estate brokerage/franchise tech company,
    # Nasdaq: LRHC, filed as Exhibit 3.6 to its 2023 IPO S-1/A) whose section (ix) explicitly and
    # unambiguously states the Series A Preferred "shall have no anti-dilution rights" -- grepped
    # the full text for full-ratchet/weighted-average/broad-based/narrow-based, zero hits.
    '1879403_000157587223000626': ('none', 'easy', 'no anti-dilution rights', 'LA ROSA HOLDINGS CORP.  (LRHC)  (CIK 0001879403)'),
}
# Excluded (audit caught wrong document type, kept for trail, NEVER in oracle):
#   CROSS MEDIA, VOIP INC, XERIANT, LEAP THERAPEUTICS, UTIX GROUP: the anti-dilution clause is on
#     WARRANTS or convertible NOTES, not preferred stock -- wrong instrument for this field.
#   Vemics: "Investor Shares" / "Broad-Based Weighted Average Price" with no preferred-stock
#     language anywhere in the excerpt -- can't confirm this is a preferred-stock charter clause.
#   TRIAN ACQUISITION, PROSPECT GLOBAL RESOURCES: "no anti-dilution" stated for SPAC sponsor /
#     Series A WARRANTS, not preferred stock.
#   EMMIS COMMUNICATIONS, TRAVEL HUNT HOLDINGS: tender-offer/earnout share-count mechanics, not a
#     charter clause stating the preferred stock itself has no anti-dilution protection.
#   POPULAR INC (763901_000095012310045398): removed 2026-07-02, off-thesis bank-regulatory
#     document (see replacement note above) -- was NOT a mislabeling bug, just wrong document type.


def window_on(text, anchor, before=420, after=900):
    """Find anchor in text (case-insensitive), extract window, return (window, validating_quote)."""
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
        oracle.append({"id": cid, "company": company, "antidilution_type": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    dist = dict(Counter(o['antidilution_type'] for o in oracle))
    print(f"wrote {len(oracle)} items  {dist}")


if __name__ == "__main__":
    main()
