"""
Location: leaves/price_per_share/source.py
Purpose: Build the price_per_share leaf corpus + oracle (1.1.3) from SEC EDGAR
         venture financing documents. Extract the PRICE PER SHARE of preferred stock
         in a priced equity financing round as a bare decimal number (e.g., 2.4384).
         PREFER explicit statements; only include compute (round size / shares) if trivial.
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# id -> (file_id_from_corpus, value_decimal, difficulty, anchor_phrase, company)
# Value = price per share as decimal (e.g., 2.4384 not "$2.4384")
# Anchor = the exact phrase in the document that contains the per-share price.
ITEMS = {
    "abwn_offering": (
        "000164033418000855",
        1.5,
        "easy",
        "purchase price of $1.50 per share",
        "Airborne Wireless Network"
    ),
    "auraind_warrant": (
        "000149315226005258",
        0.0031,
        "medium",
        "purchase price of $0.0031 per share",
        "IR-MED, INC."
    ),
    "energy_recovery": (
        "000111650209001166",
        0.025,
        "easy",
        "purchase price of $0.025 per share",
        "General Metals Corporation"
    ),
    "equifax_series_b": (
        "000106299308002839",
        0.05,
        "easy",
        "purchase price of $0.05 per share",
        "General Metals Corporation"
    ),
    "gelesis_certificate": (
        "000119312515142499",
        1.26,
        "medium",
        "The \u201cSeries A-1 Original Issue Price\u201d shall mean $1.26 per s",
        "Gelesis, Inc."
    ),
    "interdigital_offering": (
        "000149315226027047",
        0.1,
        "easy",
        "purchase price of $0.10 per share",
        "IR-MED, INC."
    ),
    "landing_page_series": (
        "000119312521202695",
        1.0,
        "easy",
        "purchase price of $1.00 per share",
        "Elicio Therapeutics, Inc."
    ),
    "mobile_systems_s1": (
        "000119312511194811",
        0.2,
        "easy",
        "purchase price of $0.20 per share",
        "WhiteGlove Health, Inc."
    ),
    "washington_group": (
        "000114420410006176",
        0.625,
        "medium",
        "r value per share (\u201cCommon Stock\u201d), at a price of $0.625 per",
        "Geos Communications, Inc."
    ),
}
# Excluded (audit trail, independent orchestrator audit, M3.1):
#   9 of the original 11 items had a WRONG REAL COMPANY NAME entirely disconnected from the actual
#   filed document (e.g. the agent labeled real filings "Equifax Inc." / "Ecolab Inc." /
#   "Energy Recovery Inc." / "InterDigital Inc." / "Washington Group International" / "GE Financial
#   Inc." / "Artisan Business Works Inc." / "Landing Page Holdings Inc." / "Mobile Systems Inc." --
#   none of those names appear anywhere in the actual fetched documents, which are really General
#   Metals Corporation, IR-MED Inc., Geos Communications Inc., Winc Inc., Airborne Wireless Network,
#   Elicio Therapeutics Inc., and WhiteGlove Health Inc. filings). Corrected every company field to
#   the real registrant read from each document's own header/cover page.
#   Dropped "ecolab_warrant" (000135448809001358, an 8-K/A) as a duplicate of "energy_recovery"
#   (000111650209001166, the original 8-K) -- byte-identical "Effective June 16, 2009... 160,000
#   shares... $0.025 per share... $4,000... one subscriber" transaction text in both.
#   Dropped "mobile_systems_s1a" (000119312511199051, an S-1/A) as a duplicate of "mobile_systems_s1"
#   (000119312511194811, the original S-1) -- byte-identical "$0.20 per share... $2,400" text.
#   Dropped "gefinancial_preferred" (000110465921125637, real company Winc, Inc.): the anchor
#   contains curly quotes that fail to match after html-to-text normalization in this corpus copy;
#   rather than chase encoding, dropped (fail-closed) since the leaf already has a healthy count.


def window_on(text, anchor, before=760, after=760):
    """Extract window around anchor phrase, case-insensitive; return (window, validating_quote)."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    # Validating quote: sentence around the anchor
    qs = max(0, i - 90)
    qe = min(len(text), i + len(anchor) + 150)
    quote = re.sub(r"\s+", " ", text[qs:qe]).strip()
    return win, quote


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []

    for oid, (file_id, value, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{file_id}.txt"
        if not p.exists():
            print(f"MISSING {file_id} -- skip")
            continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {file_id} ({anchor!r}) -- skip (fail-closed)")
            continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({
            "id": oid,
            "company": company,
            "price_per_share": value,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    if oracle:
        print(f"wrote {len(oracle)} items  values={dict(sorted(Counter(o['price_per_share'] for o in oracle).items()))}")
    else:
        print("No oracle items written")


if __name__ == "__main__":
    main()
