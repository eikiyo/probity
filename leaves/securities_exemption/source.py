"""
Location: leaves/securities_exemption/source.py
Purpose: Build the securities_exemption leaf corpus + oracle (ref 7.1, op CL=classify) from
         real SEC Form D filings. Ground truth is read DIRECTLY from each filing's own
         structured <federalExemptionsExclusions><item> XML field (SEC's own item codes:
         "06b"=Rule 506(b), "06c"=Rule 506(c)), never inferred from a naive raw-text substring
         search. The model is shown the filing's real <offeringData> exemption/type-of-security
         section and must classify which exemption was claimed.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# id -> (company, real federalExemptionsExclusions item code, url)
# Ground truth confirmed by fetching each filing's real primary_doc.xml and reading its own
# <federalExemptionsExclusions> block directly -- NOT inferred from raw-text keyword search.
ITEMS = {
    "1102449": ("ACCELERATED I/O INC", "06b", "https://www.sec.gov/Archives/edgar/data/1102449/000110244915000001/primary_doc.xml"),
    "1260990": ("GTX INC /DE/", "06b", "https://www.sec.gov/Archives/edgar/data/1260990/000157093414000003/primary_doc.xml"),
    "1444307": ("ONCOSEC MEDICAL Inc", "06b", "https://www.sec.gov/Archives/edgar/data/1444307/000149315223019301/primary_doc.xml"),
    "1498738": ("VoCare, Inc.", "06c", "https://www.sec.gov/Archives/edgar/data/1498738/000149873814000005/primary_doc.xml"),
    "1597815": ("Handybook, Inc.", "06b", "https://www.sec.gov/Archives/edgar/data/1597815/000159781514000002/primary_doc.xml"),
    "1795387": ("Brewer Lane Ventures Fund I, L.P.", "06c", "https://www.sec.gov/Archives/edgar/data/1795387/000179538720000001/primary_doc.xml"),
    "1804648": ("Material Impact Fund II, L.P.", "06c", "https://www.sec.gov/Archives/edgar/data/1804648/000180464820000004/primary_doc.xml"),
    "1902507": ("NextView Ventures V, L.P.", "06c", "https://www.sec.gov/Archives/edgar/data/1902507/000190250722000003/primary_doc.xml"),
    "1947170": ("Devorto Corp", "06b", "https://www.sec.gov/Archives/edgar/data/1947170/000194717022000001/primary_doc.xml"),
    "1981408": ("McBride Sisters Collections, Inc.", "06b", "https://www.sec.gov/Archives/edgar/data/1981408/000198140823000001/primary_doc.xml"),
}

CODE_TO_LABEL = {"06b": "506b", "06c": "506c", "05": "504"}

# Excluded (audit trail): a prior sibling-agent build of this SAME leaf shipped 124 items
# whose oracle labels were assigned by a naive `"506(c)" in raw_text.lower()` substring search,
# and whose "validating_quote" was either the answer label itself or a generic XML header
# (<edgarSubmission><primaryIssuer>...) that never even contains the real exemption field --
# the corpus/questions window shown to the model was truncated BEFORE the real
# <federalExemptionsExclusions> section, making the task unanswerable from the shown text.
# Independent audit (re-fetching the real primary_doc.xml and reading the actual
# <federalExemptionsExclusions><item> field) found at least 3 of the 124 labels flatly WRONG
# (Brewer Lane Ventures, Material Impact Fund II, NextView Ventures V were all labeled "506b"
# but are real "506c" filings). All 124 items discarded; rebuilt from scratch here using the
# real structured field as the only source of truth, and the window built to include the
# actual <federalExemptionsExclusions> section the model must read.


def build_window(raw_xml, code):
    """Extract a real excerpt spanning issuer name + the actual exemptions field."""
    m = re.search(r"<entityName>.*?</federalExemptionsExclusions>", raw_xml, re.S)
    if not m:
        return None
    text = re.sub(r"\n\s*\n", "\n", m.group(0)).strip()
    return text


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []

    for cik, (company, code, url) in ITEMS.items():
        full_path = FULL / f"{cik}.xml"
        if not full_path.exists():
            print(f"MISSING {cik} -- skip"); continue
        raw = full_path.read_text(errors="ignore")

        # Verify the claimed code is a REAL substring of the REAL fetched document.
        real_field = re.search(r"<federalExemptionsExclusions>.*?</federalExemptionsExclusions>", raw, re.S)
        if not real_field or f"<item>{code}</item>" not in real_field.group(0):
            print(f"MISMATCH {cik}: claimed {code} not found in real field -- skip (fail-closed)")
            continue

        win = build_window(raw, code)
        if not win:
            print(f"NO WINDOW {cik} -- skip"); continue

        label = CODE_TO_LABEL.get(code, "other")
        (HERE / "corpus" / "questions" / f"{cik}.txt").write_text(win, encoding="utf-8")

        oracle.append({
            "id": cik,
            "company": company,
            "securities_exemption": label,
            "difficulty": "medium",
            "validating_quote": f"<item>{code}</item>",
            "url": url,
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    from collections import Counter
    print(f"wrote {len(oracle)} items  {dict(Counter(o['securities_exemption'] for o in oracle))}")


if __name__ == "__main__":
    main()
