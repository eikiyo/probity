"""
Location: leaves/convert_vs_preference_decision/source.py
Purpose: Build the convert_vs_preference_decision leaf corpus + oracle (ref 4.4, op CO=compute)
         from real, SEC-filed worked examples in a WeFunder "Agreement for Future Equity"
         template's Appendix II (filed as Exhibit 99.1 to Snapwire Media, Inc.'s Form C/A, a
         real Reg CF crowdfunding offering). PROVENANCE NOTE (same as sibling
         option_pool_shuffle leaf): these are illustrative worked examples from a standardized
         legal-document template, not Snapwire's own specific transaction -- but real, SEC-filed,
         public text with genuinely computed, internally self-consistent numbers. The window
         excludes the document's own stated decision ("the investor would elect to...") so the
         model must compute and decide, not copy.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (decision, scenario-start anchor, decision-line anchor [excluded from window], url)
ITEMS = {
    "example4_convert": ("convert",
        "Investor has purchased an Agreement for Future Equity for $100,000. The Valuation Cap is $10,000,000.\n\xe2\x97\x8f Another entity proposes to acquire the company for cash consideration of $50,000,000.",
        "the investor would elect to convert the Agreement for Future Equity",
        "https://www.sec.gov/Archives/edgar/data/1680084/000121390017000472/fc2016a1ex99i_snapwire.htm"),
    "example5_take_preference": ("take-preference",
        "Investor has purchased an Agreement for Future Equity for $100,000. The Valuation Cap is $6,000,000.\n\xe2\x97\x8f Another entity proposes to acquire the company for cash consideration of $200,000.",
        "the investor would elect to cash out the Agreement for Future Equity",
        "https://www.sec.gov/Archives/edgar/data/1680084/000121390017000472/fc2016a1ex99i_snapwire.htm"),
}


def main():
    oracle_lines = []
    raw = (FULL / "snapwire.txt").read_text()
    for id_, (decision, start_anchor, answer_anchor, url) in ITEMS.items():
        norm_start = start_anchor.replace("\n\xe2\x97\x8f ", " &#9679; ")
        if norm_start not in raw:
            print(f"SKIP {id_}: start anchor not found -- {norm_start[:80]!r}")
            continue
        if answer_anchor not in raw:
            print(f"SKIP {id_}: answer anchor not found -- {answer_anchor!r}")
            continue
        start_idx = raw.find(norm_start)
        end_idx = raw.find(answer_anchor)
        if end_idx <= start_idx:
            print(f"SKIP {id_}: bad window ordering")
            continue
        window = raw[start_idx:end_idx].strip()
        if decision in window.lower().replace("-", "").replace(" ", ""):
            pass  # decision word itself may appear in neutral option-listing prose; only the final "elect to" sentence is excluded
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "convert_vs_preference_decision": decision,
            "validating_quote": answer_anchor,
            "source_url": url,
            "company": "Snapwire Media, Inc. (WeFunder AFE template, Appendix II)",
        })
        print(f"OK {id_}: {decision}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
