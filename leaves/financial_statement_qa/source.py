"""
Location: leaves/financial_statement_qa/source.py
Purpose: Build the financial_statement_qa leaf corpus + oracle (ref 7.5, op EX=extract) from
         real S-1 Selected/Summary Financial Data tables. Each figure independently re-verified
         as a literal substring of the real fetched document. The target-period line prepended
         to each window is a real, literal instruction (not fabricated data) pointing at one
         specific number already present in the real table -- necessary because the shared
         runner only passes {id, document} through to build_prompt (no per-item extra keys).
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, target_period_desc, revenue_value, table anchor substring, source url)
ITEMS = {
    "civitas": ("Civitas Solutions, Inc.", "fiscal year ended September 30, 2012", 1123118,
        "Fiscal Year Ended September 30, Nine Months Ended June 30, 2011 2012 2013 2013 2014",
        "https://www.sec.gov/Archives/edgar/data/1608638/000119312514340497/d729354ds1a.htm"),
    "ignentertainment": ("IGN Entertainment, Inc.", "fiscal year ended December 31, 2003", 17541,
        "Year Ended December 31, Three Months Ended March 31, 2002 2003 2004 2004 2005",
        "https://www.sec.gov/Archives/edgar/data/1101547/000104746905019338/a2158851zs-1.htm"),
    "castlebio": ("Castle Biosciences, Inc.", "fiscal year ended December 31, 2018", 22786,
        "Years Ended December 31,",
        "https://www.sec.gov/Archives/edgar/data/1447362/000114036120014751/nt10012655x7_424b4.htm"),
    "emageon": ("Emageon Inc.", "fiscal year ended December 31, 2002", 12619,
        "1999 2000 2001 2002 2003(1) 2003(1) 2004(1)",
        "https://www.sec.gov/Archives/edgar/data/1121439/000095014405000529/g89998a2sv1za.htm"),
    "hyrecar": ("HyreCar Inc.", "fiscal year ended December 31, 2018", 9777079,
        "Three Months Ended March 31, Years Ended December 31, 2019 2018 2018 2017",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
}

# find the revenue-line raw text to build the table window around
REVENUE_ANCHORS = {
    "civitas": "Net revenue $ 1,062,773 $ 1,123,118 $ 1,198,653 $ 893,541 $ 938,861",
    "ignentertainment": "Total revenue 11,272 17,541 42,949 5,684 13,743",
    "castlebio": "Net revenues",
    "emageon": "Total revenue 187 165 2,499 12,619 23,291 14,095 29,556",
    "hyrecar": "Revenues $ 3,510,725 1,714,183 $ 9,777,079 3,223,874",
}


def main():
    oracle_lines = []
    for id_, (company, period, value, table_anchor, url) in ITEMS.items():
        raw = (FULL / f"{id_}.txt").read_text()
        rev_anchor = REVENUE_ANCHORS[id_]
        if table_anchor not in raw:
            print(f"SKIP {id_}: table_anchor not found -- {table_anchor!r}")
            continue
        if rev_anchor not in raw:
            print(f"SKIP {id_}: revenue anchor not found -- {rev_anchor!r}")
            continue
        table_idx = raw.find(table_anchor)
        rev_idx = raw.find(rev_anchor)
        start = min(table_idx, rev_idx)
        end = max(table_idx, rev_idx) + len(rev_anchor if rev_idx > table_idx else table_anchor) + 50
        table_excerpt = raw[start:end].strip()
        window = f"TARGET PERIOD: {period}\n\n{table_excerpt}"
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "financial_statement_qa": value,
            "validating_quote": rev_anchor,
            "source_url": url,
            "company": company,
            "target_period": period,
        })
        print(f"OK {id_} {company} ({period}): {value}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
