"""
Location: leaves/s1_risk_factors/source.py
Purpose: Extract risk-factor headings from real S-1 IPO filings.
Functions: main()
Calls: _leaf_src (shared utilities)
Imports: json, re, time, pathlib, sys
"""

import json
import re
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from _leaf_src import search_edgar, fetch_url, url_from_hit  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"


def main():
    FULL.mkdir(parents=True, exist_ok=True)
    candidates = []
    seen_cik = set()

    hits = search_edgar("Risk Factors", forms="S-1", limit=12)
    for h in hits:
        src = h["_source"]
        cik = int(src["ciks"][0])
        if cik in seen_cik:
            continue
        seen_cik.add(cik)

        url = url_from_hit(h)
        text = fetch_url(url)
        if not text:
            continue
        time.sleep(0.2)

        # Find risk factor headings (lines in CAPS or bold style)
        lines = text.split("\n")
        headings = []
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100 and (line.isupper() or "risk" in line.lower()):
                if line not in headings:
                    headings.append(line)

        if not headings:
            continue

        heading = headings[0]
        cid = f"{cik}_{src['adsh'].replace('-', '')}"
        (FULL / f"{cid}.txt").write_text(text, encoding="utf-8")

        candidates.append({
            "id": cid,
            "company": src["display_names"][0],
            "risk_factor_heading": heading,
            "difficulty": "medium",
            "anchor": heading[:50],
            "validating_quote": heading,
            "url": url,
        })
        print(f"  + {cid}  {heading[:40]}")

    if candidates:
        (HERE / "oracle.jsonl").write_text(
            "\n".join(json.dumps(c) for c in candidates) + "\n", encoding="utf-8")
        print(f"\nWROTE {len(candidates)} items")
    else:
        print("\nNo items found")


if __name__ == "__main__":
    main()
