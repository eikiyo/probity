"""
Location: leaves/flag_missing_pro_rata/source.py
Purpose: Build the flag_missing_pro_rata leaf corpus + oracle (ref 8.5, op FL=flag) by reusing
         real, already-fetched documents from the sibling pro_rata_rights leaf's corpus. Two
         genuine explicit-waiver documents (Xcyte Therapies, Rapid7) were found on re-audit of
         that leaf's "no" class -- distinct real documents, not a universal template's two
         branches of the same clause (the failure mode this leaf was originally deferred to
         guard against). Paired with two genuine explicit-grant documents (Greenfield Robotics,
         SOS Hydration) from the same leaf's "yes" class.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, flag_value, anchor substring, source url)
ITEMS = {
    "xcyte_waiver": ("Xcyte Therapies, Inc.", True,
        "WAIVER OF PREEMPTIVE RIGHTS AND AMENDMENT OF AMENDED AND RESTATED INVESTOR RIGHTS AGREEMENT",
        "https://www.sec.gov/Archives/edgar/data/0001193125-03-085295/dex108.htm"),
    "rapid7_waiver": ("Rapid7, Inc.", True,
        "Waiver of Right to Future Stock Issuances",
        "https://www.sec.gov/Archives/edgar/data/0000950123-15-006790/filename6.htm"),
    "greenfield_grant": ("Greenfield Robotics Corp", False,
        "Pro Rata Right . Investor shall have the right to purchase its pro rata share of Preferred Stock",
        "https://www.sec.gov/Archives/edgar/data/0001104659-26-075802/tm2617498d1_ex3-9.htm"),
    "soshydration_grant": ("SOS Hydration Inc.", False,
        "The Investor and the Company will execute a Pro Rata Rights Agreement",
        "https://www.sec.gov/Archives/edgar/data/0001721868-21-000866/filename15.htm"),
}


def build_window(raw_text, anchor):
    idx = raw_text.find(anchor)
    if idx == -1:
        return None
    start = max(0, idx - 200)
    end = min(len(raw_text), idx + len(anchor) + 350)
    return raw_text[start:end].strip()


def main():
    oracle_lines = []
    for id_, (company, flag_val, anchor, url) in ITEMS.items():
        raw_file = FULL / f"{FULL_MAP[id_]}.txt"
        raw = raw_file.read_text()
        if anchor not in raw:
            print(f"SKIP {id_}: anchor not found verbatim -- {anchor!r}")
            continue
        window = build_window(raw, anchor)
        if window is None:
            print(f"SKIP {id_}: could not build window")
            continue
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "flag_missing_pro_rata": flag_val,
            "validating_quote": anchor,
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company}: flag_missing_pro_rata={flag_val}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


FULL_MAP = {
    "xcyte_waiver": "0001193125-03-085295_dex108",
    "rapid7_waiver": "0000950123-15-006790_filename6",
    "greenfield_grant": "0001104659-26-075802_tm2617498d1_ex3-9",
    "soshydration_grant": "0001721868-21-000866_filename15",
}


if __name__ == "__main__":
    main()
