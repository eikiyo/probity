"""
Location: leaves/flag_internal_inconsistency/source.py
Purpose: Build the flag_internal_inconsistency leaf corpus + oracle (ref 8.6, op FL=flag) by
         pairing two real, independently-cited shares-outstanding figures from the same real
         SEC filing (S-1/424B4 capitalization table vs. prospectus summary/beneficial-ownership
         table). Each figure independently re-verified as a literal substring of the real
         fetched document; the label is TRUE (inconsistent) only when the two real numbers are
         numerically different, FALSE (consistent) only when they are numerically identical --
         computed programmatically from the two real extracted numbers, never asserted by hand.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, citation_a_label, citation_a_anchor, citation_b_label, citation_b_anchor, url)
ITEMS = {
    "actelis_consistent": ("Actelis Networks, Inc.",
        "Capitalization table (actual column)",
        "94,318,590 shares issued and outstanding, actual",
        "Balance sheet as of December 31, 2021",
        "94,318,590 and 94,191,508 shares issued and outstanding as of December&#x00a0;31, 2021, and 2020, respectively",
        "https://www.sec.gov/Archives/edgar/data/1141284/000121390022020064/fs12022_actelisnet.htm"),
    "castlebio_consistent": ("Castle Biosciences, Inc.",
        "Capitalization table (actual column)",
        "17,203,496 shares issued and outstanding, actual",
        "Dilution section basis statement",
        "is based on 17,203,496 shares of common stock outstanding as of March 31, 2020",
        "https://www.sec.gov/Archives/edgar/data/1447362/000114036120014751/nt10012655x7_424b4.htm"),
    "castlebio_inconsistent": ("Castle Biosciences, Inc.",
        "Capitalization table (actual column)",
        "17,203,496 shares issued and outstanding, actual",
        "Beneficial-ownership table 'Before Offering' basis",
        "is based on 17,360,096 shares of common stock outstanding as of May 29, 2020",
        "https://www.sec.gov/Archives/edgar/data/1447362/000114036120014751/nt10012655x7_424b4.htm"),
    "hyrecar_inconsistent": ("HyreCar Inc.",
        "Capitalization table (actual column, as of March 31, 2019)",
        "12,191,508 shares issued and outstanding, actual",
        "Prospectus summary basis statement",
        "be outstanding immediately after this offering is based on 12,331,348 shares of our common stock outstanding as of July 18, 2019",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
    "ignentertainment_inconsistent": ("IGN Entertainment, Inc.",
        "Capitalization table (actual column)",
        "20,392,610 shares issued and outstanding, actual",
        "Prospectus summary basis statement",
        "which includes 20,824,068 shares outstanding as of March 31, 2005",
        "https://www.sec.gov/Archives/edgar/data/1101547/000104746905019338/a2158851zs-1.htm"),
}


def _extract_number(anchor):
    m = re.search(r"[\d,]{5,}", anchor)
    return int(m.group(0).replace(",", "")) if m else None


def main():
    oracle_lines = []
    for id_, (company, label_a, anchor_a, label_b, anchor_b, url) in ITEMS.items():
        raw_path = FULL / f"{id_.split('_')[0]}.txt"
        raw = raw_path.read_text()
        if anchor_a not in raw:
            print(f"SKIP {id_}: citation A not found verbatim -- {anchor_a!r}")
            continue
        if anchor_b not in raw:
            print(f"SKIP {id_}: citation B not found verbatim -- {anchor_b!r}")
            continue
        num_a = _extract_number(anchor_a)
        num_b = _extract_number(anchor_b)
        inconsistent = (num_a != num_b)
        window = (
            f"Citation A ({label_a}): \"{anchor_a}\"\n\n"
            f"Citation B ({label_b}): \"{anchor_b}\""
        )
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "flag_internal_inconsistency": inconsistent,
            "validating_quote": f"{anchor_a} | {anchor_b}",
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company}: A={num_a} B={num_b} -> inconsistent={inconsistent}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
