"""
Location: leaves/form_d_fields/source.py
Purpose: Extract specific numeric fields from real Form D filings (total offering, amount sold,
         minimum investment).
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
FIELDS = ["Total Amount of Securities Offered", "Total Amount Sold"]


def main():
    FULL.mkdir(parents=True, exist_ok=True)
    candidates = []
    seen_cik = set()

    for field in FIELDS:
        hits = search_edgar(field, forms="D", limit=6)
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

            pat = rf"{field}[:\s]+\$?([\d,]+(?:\.\d+)?)"
            m = re.search(pat, text, re.IGNORECASE)
            if not m:
                continue

            value = m.group(1)
            cid = f"{cik}_{src['adsh'].replace('-', '')}"
            (FULL / f"{cid}.txt").write_text(text, encoding="utf-8")

            candidates.append({
                "id": cid,
                "company": src["display_names"][0],
                "field_name": field,
                "form_d_field_value": value,
                "difficulty": "medium",
                "anchor": f"{field}: ${value}",
                "validating_quote": value,
                "url": url,
            })
            print(f"  + {cid}  {field[:35]}  {value}")

    if candidates:
        (HERE / "oracle.jsonl").write_text(
            "\n".join(json.dumps(c) for c in candidates) + "\n", encoding="utf-8")
        print(f"\nWROTE {len(candidates)} items")
    else:
        print("\nNo items found")


if __name__ == "__main__":
    main()
