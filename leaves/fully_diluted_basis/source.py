"""
Location: leaves/fully_diluted_basis/source.py
Purpose: Build the fully_diluted_basis leaf corpus + oracle by reading real SEC docs and
         hand-classifying whether capitalization definitions use FULLY-DILUTED basis
         (includes all outstanding + options/convertible securities/pool) vs
         ISSUED-OUTSTANDING basis (counts only actual issued shares, not options/pool).
         Each item is a real SEC filing whose cap definition was READ AND HAND-CLASSIFIED,
         with the validating quote stored. The model sees only the clause window.
         FAIL-CLOSED: only items with verifiable anchor phrases in real cap definition contexts.
Functions: window_on(), main()
Calls: candidates.jsonl (company/url), full doc texts
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CANDS_FD = HERE / "candidates_fully_diluted.jsonl"
CANDS_IO = HERE / "candidates_issued_outstanding.jsonl"
FULL = HERE / "corpus" / "full"

# id -> (label, difficulty, anchor substring to center the clause window on).
# Each label was assigned by READING the real capitalization clause in context.
# Anchor must appear in a DEFINITION section, not just mentioned in passing.
ITEMS = {
    # FULLY-DILUTED basis: definitions that explicitly include all options/pool/convertible securities
    # Easterly REIT docs - explicit "Other Definitions — Fully diluted basis assumes..." sections
    "0001193125-15-279828_d13426dex991": ("fully-diluted", "easy", 
        "Fully diluted basis assumes the exchange of all outstanding common units"),
    "0001193125-15-367178_d30089dex992": ("fully-diluted", "easy",
        "Fully diluted basis assumes the exchange of all outstanding common units"),
    "0001193125-16-489099_d152290dex991": ("fully-diluted", "easy",
        "Fully diluted basis assumes the exchange of all outstanding common units"),
    "0001564590-18-003959_dea-ex991_7": ("fully-diluted", "medium",
        "Fully diluted basis assumes"),
    "0001193125-15-367178_d30089dex991": ("fully-diluted", "medium",
        "Fully diluted basis assumes the exchange of all outstanding common units"),
    "0001564590-17-022000_dea-ex991_6": ("fully-diluted", "easy",
        "Fully diluted basis assumes"),
    # SAFEs with explicit Company Capitalization including Unissued Option Pool
    "0001213900-22-000982_ea153649ex3-1_creciinc": ("fully-diluted", "medium",
        "Includes the Unissued Option Pool"),
    "0001213900-21-030690_ea142082ex5-1_rentberry": ("fully-diluted", "medium",
        "Includes the Unissued Option Pool"),
    
    # ISSUED-OUTSTANDING basis: narrower cap definitions (only what's actually issued, not options)
    # SAFEs with Liquidity Capitalization that explicitly EXCLUDES the Unissued Option Pool
    "0001575872-26-000456_amass029_ex10-1": ("issued-outstanding", "hard",
        "Excludes the Unissued Option Pool"),
    "0001575872-26-000442_amass027_ex10-1": ("issued-outstanding", "hard",
        "Excludes the Unissued Option Pool"),
}


def window_on(text, anchor, before=760, after=760):
    """Return (clause_window, validating_sentence) centered on the anchor phrase."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    # validating quote: ~the sentence around the anchor
    qs = max(0, i - 90); qe = min(len(text), i + len(anchor) + 150)
    quote = re.sub(r"\s+", " ", text[qs:qe]).strip()
    return win, quote


def main():
    # Load candidates for company/URL lookup
    cands_by_id = {}
    for line in open(CANDS_FD):
        if line.strip():
            c = json.loads(line)
            cands_by_id[c["id"]] = c
    for line in open(CANDS_IO):
        if line.strip():
            c = json.loads(line)
            cands_by_id[c["id"]] = c
    
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    
    for cid, (label, diff, anchor) in ITEMS.items():
        full_path = FULL / f"{cid}.txt"
        if not full_path.exists():
            print(f"MISSING doc {cid} — skip"); continue
        
        text = full_path.read_text(errors="ignore")
        win, quote = window_on(text, anchor)
        
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)"); continue
        
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        c = cands_by_id.get(cid, {})
        company = re.sub(r"\s*\(.*$", "", c.get("company", "?")).strip()
        oracle.append({
            "id": cid,
            "company": company,
            "fully_diluted_basis": label,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff,
            "url": c.get("url", "")
        })
    
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    
    from collections import Counter
    counts = Counter(o['fully_diluted_basis'] for o in oracle)
    print(f"wrote {len(oracle)} items  {dict(counts)}")


if __name__ == "__main__":
    main()
