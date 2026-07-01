"""
Location: leaves/employee_pool_pct/source.py
Purpose: Build the employee_pool_pct leaf corpus + oracle (ref 3.2.3, op CO=compute) from
         Uber Technologies, Inc.'s real S-1 (filed 2019-04-11, CIK 1543151, accession
         0001193125-19-103850, primary doc d647752ds1.htm). The S-1's own capitalization
         narrative states: "130.0 million shares of our common stock reserved for future
         issuance under our 2019 Equity Incentive Plan (the '2019 Plan')". Model is given
         raw pool shares + total shares outstanding (NOT the percentage) and must compute
         pool / total * 100 itself.
Functions: main()
Imports: json, pathlib
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

TOTAL_SHARES_THOUSANDS = 1362500  # same S-1's stated total shares outstanding as of 2019-03-31

# oracle_id -> (pool_shares_k, expected_pct, difficulty, plan_name, company, cik, accession)
# Real quote: "130.0 million shares of our common stock reserved for future issuance under
# our 2019 Equity Incentive Plan ("2019 Plan")" -- verified present verbatim in the real
# fetched S-1 text before inclusion.
ITEMS = {
    "uber_2019_equity_incentive_plan_pool": (
        130_000,
        9.5,
        "easy",
        "2019 Equity Incentive Plan",
        "Uber Technologies, Inc.",
        "1543151",
        "0001193125-19-103850",
    ),
}

# Excluded (audit trail, never in oracle):
#   A prior sibling-agent attempt at this leaf (same session) fabricated a "288,000 thousand
#   shares reserved under our 2010 Equity Incentive Plan" figure -- neither the number nor the
#   plan name appears anywhere in the real fetched Uber S-1 text (confirmed by direct grep of
#   the raw document). The real document's actual capitalization-section figure is 130.0
#   million shares under the "2019 Equity Incentive Plan" (Uber's plans are named the 2010
#   Stock Plan, 2013 Equity Incentive Plan, and 2019 Equity Incentive Plan -- there is no
#   "2010 Equity Incentive Plan"). Caught on independent audit, logged as a repeat high-blast
#   mistake, fabricated files deleted, rebuilt with the real verified figure above.
#   Airbnb, Pinterest, Lyft, Dropbox, Snap S-1s: not checked in this pass (thin-but-clean
#   single real item accepted rather than risk further fabrication under time pressure).


def build_document(company, pool_shares_k, total_shares_k, plan_name):
    return (
        f"From {company}'s S-1 registration statement, capitalization narrative:\n\n"
        f"\"{pool_shares_k // 1000}.0 million shares of our common stock reserved for future "
        f"issuance under our {plan_name}\"\n\n"
        f"Total shares of common stock outstanding: {total_shares_k:,} thousand"
    )


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []

    for cid, (pool_k, expected_pct, diff, plan, company, cik, acc) in ITEMS.items():
        recomputed = round(pool_k / TOTAL_SHARES_THOUSANDS * 100, 1)
        assert recomputed == expected_pct, f"{cid}: recompute {recomputed} != expected {expected_pct}"

        doc = build_document(company, pool_k, TOTAL_SHARES_THOUSANDS, plan)
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(doc, encoding="utf-8")

        oracle.append({
            "id": cid,
            "company": company,
            "employee_pool_pct": expected_pct,
            "pool_shares_thousands": pool_k,
            "total_shares_thousands": TOTAL_SHARES_THOUSANDS,
            "validating_quote": f"130.0 million shares of our common stock reserved for future issuance under our {plan} (“2019 Plan”)",
            "difficulty": diff,
            "cik": cik,
            "accession": acc,
            "url": "https://www.sec.gov/Archives/edgar/data/1543151/000119312519103850/d647752ds1.htm",
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    print(f"wrote {len(oracle)} items, hand-verified against the real Uber S-1 text")


if __name__ == "__main__":
    main()
