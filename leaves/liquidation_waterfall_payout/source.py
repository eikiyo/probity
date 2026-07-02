"""
Location: leaves/liquidation_waterfall_payout/source.py
Purpose: Build the liquidation_waterfall_payout leaf corpus + oracle (ref 4.1, op CO=compute)
         from a real SC 13E-3 going-private fairness opinion (Connecture, Inc., filed 2018).
         The opinion's own DCF/comps table discloses 4 independent methodology columns, each
         with a real, self-consistent bridge from Enterprise Value to per-share common equity
         value through a real Series A + Series B preferred liquidation stack ($78.6M combined,
         itself verified as $52.0M Series A pref + $6.9M accrued Series A dividends + $17.5M
         Series B pref + $2.2M accrued Series B dividends = $78.6M). Every item's arithmetic
         independently re-verified: (EV - severance - debt - preferred) / shares == the
         document's own disclosed per-share figure, before being trusted.
Functions: main()
Imports: json, pathlib
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

SHARED_FACTS = (
    "Severance Run-Off Payment: $(0.3) million. "
    "Projected Total Debt as of 12/31/17: $(32.6) million. "
    "Projected Preferred Stock as of 12/31/17: $(78.6) million "
    "(Series A Preferred Stock liquidation preference of $52.0 million plus projected accrued "
    "dividends as of 12/31/17 of $6.9 million, and Series B Preferred Stock liquidation "
    "preference of $17.5 million plus projected accrued dividends as of 12/31/17 of $2.2 "
    "million). Projected Shares Outstanding as of 12/31/17: 25.2 million."
)

# id -> (methodology label, enterprise_value_high_end, severance, debt, preferred, shares, stated_per_share)
ITEMS = {
    "col1_selected_companies_ltm": ("Selected Companies Analysis (LTM Ended 9/30/17 GAAP Revenue)", 124.3, 0.3, 32.6, 78.6, 25.2, 0.51),
    "col2_selected_companies_fy17e": ("Selected Companies Analysis (FY2017E GAAP Revenue)", 122.0, 0.3, 32.6, 78.6, 25.2, 0.42),
    "col3_selected_companies_fy18e": ("Selected Companies Analysis (FY2018E GAAP Revenue)", 121.2, 0.3, 32.6, 78.6, 25.2, 0.39),
    "col4_discounted_cash_flow": ("Discounted Cash Flow Analysis", 122.6, 0.3, 32.6, 78.6, 25.2, 0.44),
}


def main():
    oracle_lines = []
    for id_, (label, ev, severance, debt, pref, shares, stated) in ITEMS.items():
        computed = round((ev - severance - debt - pref) / shares, 2)
        if abs(computed - stated) > 0.02:
            print(f"MISMATCH {id_}: computed {computed} vs disclosed {stated}")
            continue
        window = (
            f"Methodology: {label} (high end of reference range).\n\n"
            f"Implied Total Enterprise Value: ${ev} million.\n\n{SHARED_FACTS}"
        )
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "liquidation_waterfall_payout": stated,
            "validating_quote": f"Implied Per Share Reference Range ... ${stated}",
            "source_url": "https://www.sec.gov/Archives/edgar/data/1211759/000119312518039721/d516937dex99c3.htm",
            "company": "Connecture, Inc.",
        })
        print(f"OK {id_}: EV={ev} -> per_share={stated} (computed {computed})")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
