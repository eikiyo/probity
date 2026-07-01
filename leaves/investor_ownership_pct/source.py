"""
Location: leaves/investor_ownership_pct/source.py
Purpose: Build the investor_ownership_pct leaf corpus + oracle (ref 3.2.2, op CO=compute) from
         the same real Uber Technologies, Inc. S-1 Security Ownership table used by
         current_ownership_pct (3.1) and founder_ownership_pct (3.2.1) -- this time the
         INSTITUTIONAL / VC INVESTOR holders (not founders), which the table's own
         "5% Stockholders and Selling Stockholders" section lists distinctly from founders
         and executives. Same compute framing: model given raw shares + total outstanding,
         must compute shares / total * 100 itself.
Functions: main()
Imports: json, pathlib
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

TOTAL_SHARES_THOUSANDS = 1362500  # "1,362.5 million shares of common stock outstanding as of March 31, 2019"

# investor -> (shares_thousands, expected_pct, difficulty, description)
# Every expected_pct independently recomputed as shares_thousands / TOTAL_SHARES_THOUSANDS * 100
# and confirmed to match the real table's own stated % (to 1 decimal) before inclusion.
# All four are listed under the table's own "5% Stockholders and Selling Stockholders" heading,
# distinct from the "Directors and Named Executive Officers" section used by founder_ownership_pct.
ITEMS = {
    "uber_sb_cayman_investor": (222228, 16.3, "easy", "SB Cayman 2 Ltd. (SoftBank-affiliated investment vehicle)"),
    "uber_benchmark_investor": (150079, 11.0, "easy", "Entities affiliated with Benchmark Capital Partners"),
    "uber_pif_investor": (72841, 5.3, "medium", "The Public Investment Fund"),
    "uber_alphabet_investor": (71097, 5.2, "medium", "Entities affiliated with Alphabet Inc."),
}

# Excluded (audit trail, never in oracle):
#   H.E. Yasir Al-Rumayyan (72,963 thousand shares, 5.4%): already used in current_ownership_pct
#     as a DIRECTOR-affiliated holder (he sits on Uber's board as a PIF representative); using him
#     again here as a distinct "investor" would double-count the same underlying PIF stake already
#     captured via "The Public Investment Fund" line item (72,841 thousand, 5.3%) -- near-duplicate,
#     dropped to avoid double-counting one economic position as two independent data points.


def build_document(holder_desc, shares_thousands, total_thousands):
    return (
        f"From Uber Technologies, Inc.'s S-1 registration statement, \"Security Ownership of "
        f"Certain Beneficial Owners and Management\" table, \"5% Stockholders and Selling "
        f"Stockholders\" section (Shares Beneficially Owned Before the Offering):\n\n"
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
            "investor": desc,
            "investor_ownership_pct": expected_pct,
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
