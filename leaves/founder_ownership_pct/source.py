"""
Location: leaves/founder_ownership_pct/source.py
Purpose: Build the founder_ownership_pct leaf corpus + oracle (ref 3.2.1, op CO=compute) from
         Uber Technologies, Inc.'s real S-1 (filed 2019-04-11, CIK 1543151, accession
         0001193125-19-103850, primary doc d647752ds1.htm) "Security Ownership of Certain
         Beneficial Owners and Management" table. Uber has SINGLE-CLASS common stock at IPO
         (no multi-class voting-power split), so its stated "%" column is plain economic
         ownership, unlike Airbnb/Pinterest/Chewy (all multi-class, rejected as candidates).
         Every (founder, shares, expected_pct) below was independently HAND-VERIFIED: shares /
         1,362,500 (the table's own stated total shares outstanding as of 2019-03-31) reproduces
         the table's own stated % to one decimal place for every item.
         FOUNDERS ONLY: Garrett Camp (co-founder), Travis Kalanick (co-founder), Ryan Graves
         (CEO from 2009-2010, early-stage leader). The model is shown raw share counts + total
         outstanding (NOT the %) and must COMPUTE the percentage itself (matches CO op).
Functions: main()
Imports: json, pathlib
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

TOTAL_SHARES_THOUSANDS = 1362500  # "1,362.5 million shares of common stock outstanding as of March 31, 2019"

# founder -> (shares_thousands, expected_pct, difficulty, description)
ITEMS = {
    "uber_garrett_camp_founder": (81575, 6.0, "easy", "Garrett Camp (Founder; through Expa-1, LLC and RMG-Trust LLC)"),
    "uber_travis_kalanick_founder": (117505, 8.6, "easy", "Travis Kalanick (Founder)"),
    "uber_ryan_graves_ceo": (33184, 2.4, "medium", "Ryan Graves (CEO 2009-2010)"),
}


def build_document(founder_desc, shares_thousands, total_thousands):
    return (
        f"From Uber Technologies, Inc.'s S-1 registration statement, \"Security Ownership of "
        f"Certain Beneficial Owners and Management\" table (Shares Beneficially Owned Before "
        f"the Offering):\n\n"
        f"Applicable percentage ownership before the offering is based on {total_thousands:,} "
        f"thousand shares of common stock outstanding as of March 31, 2019.\n\n"
        f"Name of Beneficial Owner: {founder_desc}\n"
        f"Shares (in thousands): {shares_thousands:,}"
    )


def main():
    (HERE / "corpus" / "full").mkdir(parents=True, exist_ok=True)
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []

    for cid, (shares_k, expected_pct, diff, desc) in ITEMS.items():
        recomputed = round(shares_k / TOTAL_SHARES_THOUSANDS * 100, 1)
        assert recomputed == expected_pct, f"{cid}: recompute {recomputed} != expected {expected_pct}"

        doc = build_document(desc, shares_k, TOTAL_SHARES_THOUSANDS)
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(doc, encoding="utf-8")

        oracle.append({
            "id": cid,
            "founder": desc.split("(")[0].strip(),
            "founder_ownership_pct": expected_pct,
            "shares_thousands": shares_k,
            "total_shares_thousands": TOTAL_SHARES_THOUSANDS,
            "company": "Uber Technologies, Inc.",
            "validating_quote": f"{desc}: {shares_k:,} thousand shares of {TOTAL_SHARES_THOUSANDS:,} thousand total = {expected_pct}%",
            "difficulty": diff,
            "url": "https://www.sec.gov/Archives/edgar/data/1543151/000119312519103850/d647752ds1.htm",
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    print(f"wrote {len(oracle)} founder items, all hand-verified against the real Uber S-1 table")


if __name__ == "__main__":
    main()
