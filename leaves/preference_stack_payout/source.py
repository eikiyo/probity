"""
Location: leaves/preference_stack_payout/source.py
Purpose: Build the preference_stack_payout leaf corpus + oracle (ref 4.3, op CO=compute) from
         the same real Connecture, Inc. SC 13E-3 fairness opinion as liquidation_waterfall_
         payout. Two real, independent series: Series A ($52.0M preference + $6.9M accrued
         dividends) and Series B ($17.5M preference + $2.2M accrued dividends). Each item's sum
         independently re-verified against the document's own combined "$78.6 million" total
         Preferred Stock figure (52.0+6.9+17.5+2.2 == 78.6) before being trusted.
Functions: main()
Imports: json, pathlib
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
QUESTIONS = HERE / "corpus" / "questions"

FACTS = (
    "Total Projected Preferred Stock as of 12/31/17: $(78.6) million, consisting of: "
    "Series A Preferred Stock liquidation preference of $52.0 million plus projected accrued "
    "dividends as of 12/31/17 of $6.9 million; and Series B Preferred Stock liquidation "
    "preference of $17.5 million plus projected accrued dividends as of 12/31/17 of $2.2 "
    "million."
)

# id -> (target series, base preference, accrued dividends, total payout)
ITEMS = {
    "series_a": ("Series A Preferred Stock", 52.0, 6.9, 58.9),
    "series_b": ("Series B Preferred Stock", 17.5, 2.2, 19.7),
}


def main():
    # cross-check the combined total independently before trusting either sub-item
    total = 52.0 + 6.9 + 17.5 + 2.2
    assert abs(total - 78.6) < 0.01, f"combined total {total} does not match disclosed $78.6M"

    oracle_lines = []
    for id_, (series, pref, div, payout) in ITEMS.items():
        computed = round(pref + div, 1)
        if abs(computed - payout) > 0.01:
            print(f"MISMATCH {id_}: {pref}+{div}={computed} vs {payout}")
            continue
        window = f"TARGET SERIES: {series}\n\n{FACTS}"
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "preference_stack_payout": payout,
            "validating_quote": f"{series} liquidation preference of ${pref} million plus projected accrued dividends as of 12/31/17 of ${div} million",
            "source_url": "https://www.sec.gov/Archives/edgar/data/1211759/000119312518039721/d516937dex99c3.htm",
            "company": "Connecture, Inc.",
        })
        print(f"OK {id_} {series}: {pref}+{div}={payout}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
