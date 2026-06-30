"""
Location: leaves/post_money_valuation/fetch.py
Purpose: Search EDGAR for priced-equity financing documents with post-money valuations,
         fetch and save them to corpus/full/.
Functions: main()
"""

import sys
sys.path.insert(0, "engine")

from edgar import fts_search, build_url, fetch_clean
import json
import time
from pathlib import Path

HERE = Path(__file__).parent
CORPUS_DIR = HERE / "corpus" / "full"
CORPUS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """Search and fetch documents with post-money valuation language."""
    
    # Search phrases to find documents mentioning post-money valuations
    phrases = [
        '"post-money valuation of"',
        '"at a post-money valuation"',
        '"post-money valuation cap"',
        '"post-money valuation on"',
    ]
    
    all_hits = []
    for phrase in phrases:
        print(f"Searching: {phrase}", flush=True)
        hits = fts_search(phrase, limit=10)
        print(f"  Found {len(hits)} hits", flush=True)
        all_hits.extend(hits)
        time.sleep(1)
    
    # Deduplicate by document ID
    seen = {}
    for hit in all_hits:
        doc_id = hit['_id']
        if doc_id not in seen:
            seen[doc_id] = hit
    
    print(f"\nTotal unique documents: {len(seen)}", flush=True)
    
    # Fetch documents and save to corpus
    fetched = 0
    for i, (doc_id, hit) in enumerate(list(seen.items())[:25]):  # Limit to first 25
        try:
            src = hit['_source']
            cik = str(int(src['ciks'][0]))
            cid = f"{cik}_{src['adsh'].replace('-', '')}"
            url = build_url(hit)
            
            # Skip if already fetched
            outfile = CORPUS_DIR / f"{cid}.txt"
            if outfile.exists():
                print(f"[{i+1}] {cid} — already fetched", flush=True)
                continue
            
            print(f"[{i+1}] Fetching {cid}...", flush=True)
            text = fetch_clean(url)
            outfile.write_text(text, encoding="utf-8")
            fetched += 1
            
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
        
        time.sleep(0.5)
    
    print(f"\nFetched {fetched} new documents", flush=True)


if __name__ == "__main__":
    main()
