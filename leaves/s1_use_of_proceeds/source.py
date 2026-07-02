"""
Location: leaves/s1_use_of_proceeds/source.py
Purpose: Build the s1_use_of_proceeds leaf corpus + oracle (ref 7.3, op EX=extract) from real
         S-1/424B4 IPO prospectus bodies (verified to be the actual prospectus, not a comment
         letter/CORRESP document about the section -- the prior contamination's failure mode).
         Each answer phrase independently re-verified as a literal substring of the real
         fetched document's own "We intend to use..." sentence.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, short answer phrase, anchor substring [longer, contains the answer], url)
ITEMS = {
    "hyrecar": ("HyreCar Inc.", "general corporate purposes",
        "We intend to use the net proceeds to us from this offering for general corporate purposes, including working capital",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
    "castlebio": ("Castle Biosciences, Inc.", "research and development activities",
        "we intend to use the net proceeds from this offering, together with our existing cash and cash equivalents, to further support and increase our research and development activities",
        "https://www.sec.gov/Archives/edgar/data/1447362/000114036120014751/nt10012655x7_424b4.htm"),
    "axcella": ("Axcella Health Inc.", "advance our current liver programs",
        "We intend to use the net proceeds from this offering, together with our existing cash and cash equivalents, to advance our current liver programs",
        "https://www.sec.gov/Archives/edgar/data/1633070/000104746920003070/a2241647z424b4.htm"),
    "veritone": ("Veritone, Inc.", "working capital and general corporate purposes",
        "We intend to use the net proceeds from this offering for working capital and general corporate purposes",
        "https://www.sec.gov/Archives/edgar/data/1615165/000119312518194741/d757366d424b4.htm"),
    "civitas": ("Civitas Solutions, Inc.", "redeem all of the senior notes",
        "We intend to use the net proceeds from the sale of common stock by us in this offering to redeem all of the senior notes",
        "https://www.sec.gov/Archives/edgar/data/1608638/000119312514340497/d729354ds1a.htm"),
}


def build_window(raw_text, anchor):
    idx = raw_text.find(anchor)
    if idx == -1:
        return None
    start = max(0, idx - 100)
    end = min(len(raw_text), idx + len(anchor) + 300)
    return raw_text[start:end].strip()


def main():
    oracle_lines = []
    for id_, (company, answer, anchor, url) in ITEMS.items():
        raw = (FULL / f"{id_}.txt").read_text()
        if anchor not in raw:
            print(f"SKIP {id_}: anchor not found verbatim")
            continue
        if answer not in anchor:
            print(f"SKIP {id_}: answer not a substring of its own anchor -- inconsistent")
            continue
        window = build_window(raw, anchor)
        if window is None:
            print(f"SKIP {id_}: could not build window")
            continue
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "s1_use_of_proceeds": answer,
            "validating_quote": anchor,
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company}: {answer}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
