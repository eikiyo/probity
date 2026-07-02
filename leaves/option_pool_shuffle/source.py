"""
Location: leaves/option_pool_shuffle/source.py
Purpose: Build the option_pool_shuffle leaf corpus + oracle (ref 3.3, op CO=compute) from real,
         SEC-filed worked examples in a WeFunder "Agreement for Future Equity" template's
         Appendix II (filed as Exhibit 99.1 to Snapwire Media, Inc.'s Form C/A, a real Reg CF
         crowdfunding offering). PROVENANCE NOTE: these are illustrative worked examples from a
         standardized legal-document template (used across many WeFunder-platform Reg CF
         issuers), not Snapwire's own specific historical financing round -- but they are REAL,
         SEC-filed, PUBLIC text with genuinely computed, internally self-consistent numbers, not
         invented. Each item's arithmetic independently re-verified: pre_money / fully_diluted_
         shares == the document's own stated price per share, before being trusted.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (pre_money, pool_shares, fully_diluted_shares, stated price-per-share, anchor for the
#        INPUT sentence [investment+pre-money+pool+total], answer anchor [price-per-share
#        statement, excluded from window])
ITEMS = {
    "example1": (10_000_000, 1_000_000, 11_000_000, 0.909,
        "The company negotiates with investors to sell $1,000,000 worth of Series A Preferred Stock at a $10,000,000 pre-money valuation. The company&rsquo;s fully-diluted outstanding capital stock immediately prior to the financing, including a 1,000,000 share option pool to be adopted in connection with the financing, is 11,000,000 shares.",
        "The company will issue and sell 1,100,110 shares of Series A Preferred at $0.909 per share"),
    "example2": (3_000_000, 500_000, 12_500_000, 0.24,
        "The company negotiates with investors to sell $600,000 worth of Series AA Preferred Stock at a $3,000,000 pre-money valuation. The company&rsquo;s fully-diluted outstanding capital stock immediately prior to the financing, including a 500,000 share option pool to be adopted in connection with the financing, is 12,500,000 shares.",
        "The company will issue and sell 2,500,000 shares of Series AA Preferred at $0.24 per share"),
    "example3": (8_000_000, 1_500_000, 11_500_000, 0.6956,
        "The company negotiates with investors to sell $2,000,000 worth of Series A Preferred Stock at an $8,000,000 pre-money valuation. The company&rsquo;s fully-diluted outstanding capital stock immediately prior to the financing, including a 1,500,000 share option pool to be adopted in connection with the financing, is 11,500,000 shares.",
        "The company will issue and sell 2,875,215 shares of Series A Preferred at $0.6956 per share"),
}


def main():
    oracle_lines = []
    raw = (FULL / "snapwire.txt").read_text()
    for id_, (pre_money, pool, fd_shares, price, input_anchor, answer_anchor) in ITEMS.items():
        if input_anchor not in raw:
            print(f"SKIP {id_}: input anchor not found verbatim")
            continue
        if answer_anchor not in raw:
            print(f"SKIP {id_}: answer anchor not found verbatim")
            continue
        computed = round(pre_money / fd_shares, 4)
        if abs(computed - price) > 0.001:
            print(f"MISMATCH {id_}: {pre_money}/{fd_shares}={computed}, doc states {price}")
            continue
        idx = raw.find(input_anchor)
        end = raw.find(answer_anchor)
        if end <= idx:
            print(f"SKIP {id_}: answer appears before input -- bad window")
            continue
        window = raw[idx:end].strip()
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "option_pool_shuffle": price,
            "validating_quote": answer_anchor,
            "source_url": "https://www.sec.gov/Archives/edgar/data/1680084/000121390017000472/fc2016a1ex99i_snapwire.htm",
            "company": "Snapwire Media, Inc. (WeFunder AFE template, Appendix II)",
        })
        print(f"OK {id_}: pre_money={pre_money} pool={pool} fd_shares={fd_shares} -> price/share={price}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
