"""
Location: leaves/multi_round_stacked_dilution/source.py
Purpose: Build the multi_round_stacked_dilution leaf corpus + oracle (ref 3.6, op CO=compute)
         from real IPO prospectuses' Dilution-section tables. Every figure below independently
         re-verified two ways: (1) both the table-start anchor AND the answer-line anchor are
         literal substrings of the real fetched document, (2)
         offering_price - ntbv_after == dilution_per_share, checked by assertion against the
         SAME numbers the document itself states (self-consistency, not invention). The
         model-facing window is cut BEFORE the answer-line anchor so the model must actually
         compute the subtraction, not copy the document's own stated dilution figure.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, offering_price, ntbv_after, dilution_per_share, table-start anchor,
#        answer-line anchor [excluded from the model-facing window so it's a real compute
#        task, not a copy], source url)
ITEMS = {
    "civitas": ("Civitas Solutions, Inc.", 21.50, -11.39, 32.89,
        "illustrates this pro forma per share dilution",
        "Dilution per share to new investors $ 32.89",
        "https://www.sec.gov/Archives/edgar/data/1608638/000119312514340497/d729354ds1a.htm"),
    "hyrecar": ("HyreCar Inc.", 3.00, 0.91, 2.09,
        "illustrates this dilution:",
        "Dilution per share to new investors in this offering $ 2.09",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
    "castlebio": ("Castle Biosciences, Inc.", 37.00, 8.18, 28.82,
        "illustrates this dilution:",
        "Dilution per share to new investors participating in this offering",
        "https://www.sec.gov/Archives/edgar/data/1447362/000114036120014751/nt10012655x7_424b4.htm"),
    "veritone": ("Veritone, Inc.", 20.04, 5.14, 14.90,
        "illustrates per share dilution",
        "Dilution per share to new investors purchasing shares in this offering $ 14.90",
        "https://www.sec.gov/Archives/edgar/data/1615165/000119312518194741/d757366d424b4.htm"),
    "axcella": ("Axcella Health Inc.", 4.75, 2.79, 1.96,
        "Our historical net tangible book value (deficit) as of March 31, 2020 was $46.8 million, or $2.02 per share",
        "immediate dilution of $1.96 in as adjusted net tangible book value per share",
        "https://www.sec.gov/Archives/edgar/data/1633070/000104746920003070/a2241647z424b4.htm"),
}


def main():
    oracle_lines = []
    for id_, (company, price, ntbv_after, dilution, table_anchor, answer_anchor, url) in ITEMS.items():
        raw = (FULL / f"{id_}.txt").read_text()
        if table_anchor not in raw:
            print(f"SKIP {id_}: table_anchor not found verbatim -- {table_anchor!r}")
            continue
        if answer_anchor not in raw:
            print(f"SKIP {id_}: answer_anchor not found verbatim -- {answer_anchor!r}")
            continue
        computed = round(price - ntbv_after, 2)
        if abs(computed - dilution) > 0.02:
            print(f"MISMATCH {id_}: {price} - {ntbv_after} = {computed}, doc states {dilution}")
            continue
        table_idx = raw.find(table_anchor)
        answer_idx = raw.find(answer_anchor)
        if answer_idx <= table_idx:
            print(f"SKIP {id_}: answer_anchor appears before/at table_anchor -- can't build a clean window")
            continue
        start = table_idx
        end = answer_idx
        window = raw[start:end].strip()
        if str(dilution) in window or f"${dilution}" in window:
            print(f"SKIP {id_}: dilution answer leaked into window")
            continue
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "multi_round_stacked_dilution": dilution,
            "validating_quote": answer_anchor,
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company}: offering_price={price} ntbv_after={ntbv_after} -> dilution={dilution}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
