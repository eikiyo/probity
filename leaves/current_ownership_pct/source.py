"""
Location: leaves/current_ownership_pct/source.py
Purpose: Build the current_ownership_pct leaf corpus + oracle (ref 3.1, op CO=compute) from
         Uber Technologies, Inc.'s real S-1 (filed 2019-04-11, CIK 1543151, accession
         0001193125-19-103850, primary doc d647752ds1.htm) "Security Ownership of Certain
         Beneficial Owners and Management" table. Uber has SINGLE-CLASS common stock at IPO
         (no multi-class voting-power split), so its stated "%" column is plain economic
         ownership, unlike Airbnb/Pinterest/Chewy (all multi-class Class A/B/H, rejected as
         candidates -- their % columns conflate voting power with economic ownership, and their
         earlier-stage S-1 drafts had blank placeholder percentages not yet filled in).
         Every (holder, shares, expected_pct) below was independently HAND-VERIFIED: shares /
         1,362,500 (the table's own stated total shares outstanding as of 2019-03-31) reproduces
         the table's own stated % to one decimal place for every item. The model is shown the
         raw share count + total outstanding (NOT the %) and must COMPUTE the percentage itself
         (matches the leaf's "CO" = compute/math op).
Functions: main()
Imports: json, pathlib
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

TOTAL_SHARES_THOUSANDS = 1362500  # "1,362.5 million shares of common stock outstanding as of March 31, 2019"

# holder -> (shares_thousands, expected_pct, difficulty, description)
# Every expected_pct independently recomputed as shares_thousands / TOTAL_SHARES_THOUSANDS * 100
# and confirmed to match the real table's own stated % (to 1 decimal) before inclusion.
ITEMS = {
    "uber_garrett_camp": (81575, 6.0, "easy", "Garrett Camp (through Expa-1, LLC and RMG-Trust LLC)"),
    "uber_matt_cohler_benchmark": (150079, 11.0, "easy", "Entities affiliated with Benchmark Capital Partners (Matt Cohler)"),
    "uber_ryan_graves": (33184, 2.4, "medium", "Ryan Graves"),
    "uber_travis_kalanick": (117505, 8.6, "easy", "Travis Kalanick"),
    "uber_al_rumayyan_pif_director": (72963, 5.4, "medium", "H.E. Yasir Al-Rumayyan (director; PIF-affiliated)"),
    "uber_sb_cayman": (222228, 16.3, "medium", "SB Cayman 2 Ltd. (SoftBank-affiliated vehicle)"),
    "uber_alphabet_entities": (71097, 5.2, "medium", "Entities affiliated with Alphabet Inc."),
    "uber_public_investment_fund": (72841, 5.3, "medium", "The Public Investment Fund"),
    "uber_all_directors_officers_group": (462351, 33.9, "hard", "All directors and executive officers as a group (19 persons)"),
}

# Excluded (audit trail, never in oracle):
#   Dara Khosrowshahi (196 thousand shares): the table itself reports this as "*" ("less than 1%"),
#     not a stated numeric percentage -- no ground-truth figure to grade a compute answer against.
#   Airbnb, Pinterest, Chewy S-1s: all rejected. Airbnb/Pinterest are multi-class (Class A/B/H)
#     common stock, so the table's "%" column is voting power (weighted by class), not a clean
#     shares-held/shares-outstanding ratio -- would silently teach the wrong formula. Pinterest's
#     and Chewy's S-1 (both preliminary drafts, fetched and checked directly) have every
#     percentage as a literal blank placeholder ("% of our outstanding shares") -- no real number
#     was ever filed in this revision, so no ground truth exists to extract.


def build_document(holder_desc, shares_thousands, total_thousands):
    return (
        f"From Uber Technologies, Inc.'s S-1 registration statement, \"Security Ownership of "
        f"Certain Beneficial Owners and Management\" table (Shares Beneficially Owned Before "
        f"the Offering):\n\n"
        f"Applicable percentage ownership before the offering is based on {total_thousands:,} "
        f"thousand shares of common stock outstanding as of March 31, 2019.\n\n"
        f"Name of Beneficial Owner: {holder_desc}\n"
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
            "holder": desc,
            "current_ownership_pct": expected_pct,
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

    print(f"wrote {len(oracle)} items, all hand-verified against the real Uber S-1 table")


if __name__ == "__main__":
    main()
