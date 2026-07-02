"""
Location: leaves/dividend_rate_pct/source.py
Purpose: Build the dividend_rate_pct leaf corpus + oracle (ref 1.4.1, op EX=extract) from real
         venture-financing preferred-stock charters (reusing the same real, already-fetched
         documents as the sibling dividend_cumulative leaf: Jazz/Fitbit/Zoom/Teladoc/biotech VC
         charters, NOT bank-regulatory perpetual preferred, which was this leaf's original
         off-thesis contamination -- see the retired DEFERRED.md history in git log). Each item's
         percentage is manually located and independently re-verified against the raw fetched
         document text below (anchor phrase must be a literal substring of the source).
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, dividend_rate_pct, anchor substring literally present in the fetched raw doc, source url)
# Every anchor below was found by direct regex scan of the real fetched plain-text document,
# manually reviewed to exclude unrelated %-figures near the word "dividend" (e.g. Jazz
# Semiconductor's 7.25% officer-loan rate, Melinta's 8.25% debt interest, Impel/Entercom's
# 30% withholding-tax rate, scPharma's 20% cumulative CAP -- none are the stated per-annum
# dividend rate itself and were rejected during manual audit).
ITEMS = {
    "1119700_000114420405033377": ("BIOACCELERATE HOLDINGS INC", 6,
        "cumulative dividend at a rate of Six Per Cent (6%) per annum",
        "https://www.sec.gov/Archives/edgar/data/1119700/000114420405033377/ex_10-13.txt"),
    "1725255_000110465920135025": ("AdaptHealth Corp.", 8.0,
        "dividends at the per share rate of 8.0% of the Original Issue Price per annum shall accrue",
        "https://www.sec.gov/Archives/edgar/data/1725255/000110465920135025/tm2037721d4_ex3-1.htm"),
    "1620179_000104746918002690": ("Exela Technologies, Inc.", 10,
        "cumulative dividends at a rate per annum of 10% of the Liquidation Preference",
        "https://www.sec.gov/Archives/edgar/data/1620179/000104746918002690/a2235262z10-k.htm"),
    "1604950_000119312517316695": ("scPharmaceuticals Inc.", 6,
        "dividends at the rate per annum of six percent (6%) of the Series B Base Amount",
        "https://www.sec.gov/Archives/edgar/data/1604950/000119312517316695/d435316dex31.htm"),
    "1445499_000095012321001942": ("IMPEL NEUROPHARMA INC", 8,
        "are entitled to receive 8% dividends, when, if, and as declared",
        "https://www.sec.gov/Archives/edgar/data/1445499/000095012321001942/filename1.htm"),
    "1585521_000119312519083351": ("Zoom Video Communications, Inc.", 6,
        "shall mean for each series of the Preferred Stock, an annual rate of six percent (6%) of the Original Issue Price",
        "https://www.sec.gov/Archives/edgar/data/1585521/000119312519083351/d642624dex31.htm"),
}


def build_window(raw_text, anchor):
    """Real excerpt: anchor phrase +/- surrounding context, as it actually appears in the fetched doc."""
    idx = raw_text.find(anchor)
    if idx == -1:
        # anchor may have curly-quote variants; try normalizing
        norm_raw = raw_text.replace("’", "'").replace("&#146;", "'").replace("&#147;", '"').replace("&#148;", '"')
        norm_anchor = anchor.replace("’", "'")
        idx = norm_raw.find(norm_anchor)
        if idx == -1:
            return None
        raw_text = norm_raw
        anchor = norm_anchor
    start = max(0, idx - 400)
    end = min(len(raw_text), idx + len(anchor) + 400)
    return raw_text[start:end].strip()


def main():
    oracle_lines = []
    for id_, (company, pct, anchor, url) in ITEMS.items():
        raw = (FULL / f"{id_}.txt").read_text()
        window = build_window(raw, anchor)
        if window is None:
            print(f"SKIP {id_}: anchor not found verbatim in raw doc -- {anchor!r}")
            continue
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "dividend_rate_pct": pct,
            "validating_quote": anchor,
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company}: dividend_rate_pct={pct}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
