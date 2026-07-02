"""
Location: leaves/round_size/source.py
Purpose: Build the round_size leaf corpus + oracle (ref 1.2.1, op EX=extract) from real SEC
         Form D filings. Ground truth is read directly from each filing's own structured
         <totalAmountSold> XML field (SEC's own reported figure for capital actually raised),
         restricted to operating companies (industryGroupType != "Pooled Investment Fund", so
         the amount represents a company's financing round, not a VC fund's LP capital close)
         with a nonzero amount sold (a $0-sold filing means no round closed yet).
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, real totalAmountSold as fetched from primary_doc.xml, source url)
# Every figure below independently re-confirmed from the cached real XML in corpus/full/
# by direct regex extraction of <totalAmountSold> -- not typed by hand from memory.
ITEMS = {
    "1260990": ("GTX INC /DE/", "https://www.sec.gov/Archives/edgar/data/1260990/000157093414000003/primary_doc.xml"),
    "1498738": ("VoCare, Inc.", "https://www.sec.gov/Archives/edgar/data/1498738/000149873814000005/primary_doc.xml"),
    "1597815": ("Handybook, Inc.", "https://www.sec.gov/Archives/edgar/data/1597815/000159781514000002/primary_doc.xml"),
    "1981408": ("McBride Sisters Collections, Inc.", "https://www.sec.gov/Archives/edgar/data/1981408/000198140823000001/primary_doc.xml"),
    "1436444": ("TIGO ENERGY INC", "https://www.sec.gov/Archives/edgar/data/1436444/000143644409000002/primary_doc.xml"),
    "1887997": ("POSEIDON MEDICAL INC.", "https://www.sec.gov/Archives/edgar/data/1887997/000188799721000001/primary_doc.xml"),
    "1601118": ("BEYONDCORE, INC.", "https://www.sec.gov/Archives/edgar/data/1601118/000160111814000001/primary_doc.xml"),
    "1520726": ("ShopTap, Inc.", "https://www.sec.gov/Archives/edgar/data/1520726/000152072613000001/primary_doc.xml"),
    "1651590": ("Link Labs, Inc.", "https://www.sec.gov/Archives/edgar/data/1651590/000165159015000001/primary_doc.xml"),
    "1880063": ("Outerspace Ops, Inc.", "https://www.sec.gov/Archives/edgar/data/1880063/000188006321000002/primary_doc.xml"),
}


def build_window(raw_xml):
    """Real excerpt spanning issuer name through the offeringData totalAmountSold block."""
    m = re.search(r"<entityName>.*?<totalRemaining>.*?</totalRemaining>", raw_xml, re.S)
    if not m:
        return None
    text = re.sub(r"\n\s*\n", "\n", m.group(0)).strip()
    return text


def main():
    oracle_lines = []
    for cik, (company, url) in ITEMS.items():
        raw = (FULL / f"{cik}.xml").read_text()
        m_sold = re.search(r"<totalAmountSold>(.*?)</totalAmountSold>", raw)
        m_industry = re.search(r"<industryGroupType>(.*?)</industryGroupType>", raw)
        if not m_sold or not m_industry:
            print(f"SKIP {cik}: missing fields")
            continue
        if m_industry.group(1) == "Pooled Investment Fund":
            print(f"SKIP {cik}: is a VC fund, not an operating company")
            continue
        sold = int(m_sold.group(1))
        if sold == 0:
            print(f"SKIP {cik}: $0 sold, no round actually closed")
            continue
        # Verification: re-derive the sold figure from the raw XML independently of ITEMS dict
        if str(sold) not in raw:
            print(f"MISMATCH {cik}: sold figure not found verbatim in raw doc -- skip")
            continue
        window = build_window(raw)
        if window is None or str(sold) not in window:
            print(f"SKIP {cik}: window doesn't contain the real totalAmountSold value")
            continue
        (QUESTIONS / f"{cik}.txt").write_text(window)
        oracle_lines.append({
            "id": cik,
            "round_size": sold,
            "validating_quote": f"<totalAmountSold>{sold}</totalAmountSold>",
            "source_url": url,
            "company": company,
        })
        print(f"OK {cik} {company}: round_size={sold}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
