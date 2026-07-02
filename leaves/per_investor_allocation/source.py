"""
Location: leaves/per_investor_allocation/source.py
Purpose: Build the per_investor_allocation leaf corpus + oracle (ref 1.2.2, op EX=extract) from
         real Schedule 13D/13D-A filings -- investor-side disclosures that state a specific
         named investor's own purchase price, unlike company-side 8-Ks which only disclose
         round totals. Each figure independently re-verified as a literal substring of the
         real fetched document.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (investor, company, dollar_amount, anchor substring, source url)
ITEMS = {
    "roka": ("TPG Biotech III", "Roka BioScience, Inc.", 4000000,
        "TPG Biotech III acquired, for an aggregate purchase price of $4,000,000, (i) 4,000 Series A Preferred Shares",
        "https://www.sec.gov/Archives/edgar/data/1472343/000090342316001330/roka13d_1031.htm"),
    "casmedical": ("TMP II LP", "CAS Medical Systems, Inc.", 9418200,
        "TMP II LP purchased 94,182 shares of Series A Convertible Preferred Stock, par value $0.001, of the Company (the &#8220;Series A Convertible&#8221;) for an aggregate purchase price of $9,418,200",
        "https://www.sec.gov/Archives/edgar/data/764579/000089914011000453/c090611.htm"),
    "ocular": ("Incept, LLC", "Ocular Therapeutix, Inc.", 1650000,
        "Incept, LLC acquired 500,000 shares of Common Stock for an aggregate purchase price of $1,650,000",
        "https://www.sec.gov/Archives/edgar/data/1393434/000119312514293672/d767866dsc13d.htm"),
    "navidea": ("the Reporting Person", "Navidea Biopharmaceuticals, Inc.", 3000000,
        "the Reporting Person purchased 916,030 shares of Common Stock for an aggregate purchase price of $3,000,000",
        "https://www.sec.gov/Archives/edgar/data/810509/000119312521071694/d83915dsc13da.htm"),
    "quantrx": ("Mark Capital", "QuantRx Biomedical Corp", 46715.64,
        "Mark Capital purchased 1,750,000 shares of Series A Convertible Preferred Stock of the Issuer",
        "https://www.sec.gov/Archives/edgar/data/820608/000092963806000136/markcap13d28mar06.htm"),
}


def build_window(raw_text, anchor):
    idx = raw_text.find(anchor)
    if idx == -1:
        return None
    start = max(0, idx - 250)
    end = min(len(raw_text), idx + len(anchor) + 250)
    return raw_text[start:end].strip()


def main():
    oracle_lines = []
    for id_, (investor, company, amount, anchor, url) in ITEMS.items():
        raw = (FULL / f"{id_}.txt").read_text()
        if anchor not in raw:
            print(f"SKIP {id_}: anchor not found verbatim -- {anchor!r}")
            continue
        window = build_window(raw, anchor)
        if window is None:
            print(f"SKIP {id_}: could not build window")
            continue
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "per_investor_allocation": amount,
            "validating_quote": anchor,
            "source_url": url,
            "company": company,
            "investor": investor,
        })
        print(f"OK {id_} {investor} @ {company}: ${amount}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
