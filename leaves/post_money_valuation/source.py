"""
Location: leaves/post_money_valuation/source.py
Purpose: Build the post_money_valuation leaf corpus + oracle from real SEC documents.
         Each item was READ AND HAND-CLASSIFIED (manual oracle layer) to extract the
         exact post-money valuation dollar figure stated in the priced-equity financing document,
         with the validating quote stored separately. The model sees only the provision window.
Functions: find_full(), window_on(), main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent

ITEMS = {
    # Post-money valuations from priced-equity financing press releases (8-K EX-99.1)
    # id -> (value, difficulty, anchor, company)
    "1491419_000121390022046600": (68000000, "easy", "at a post-money valuation of $68 million", "LiveOne, Inc. (PodcastOne subsidiary)"),
    "1529113_000121390024057583": (275000000, "medium", "at a post-money valuation of $275 million", "XTI Aerospace, Inc."),
    "1368365_000136836520000062": (5000000, "easy", "at a post-money valuation of $5", "Remark Holdings, Inc. (AIO subsidiary)"),
    "1089872_000095017025106543": (106000000, "medium", "post-money valuation to $106 million", "Gaia, Inc. (Igniton subsidiary)"),
}
# Excluded (audit caught duplicate/ambiguity, kept for trail, NEVER in oracle):
#   1529113_000121390024069181 (XTI Aerospace, Aug 14 2024): a SECOND press release restating the
#     SAME $275M valuation fact already captured above (July 1 2024) -- near-duplicate, not an
#     independent data point.
#   315545_000149315224049571 (VisiRose seed round): the same excerpt the model would see states
#     FIVE different post-money valuations ($20M/$26.67M/$25M/$33.33M/$44.44M) across conditional
#     tranches of a structured term sheet -- genuinely ambiguous, no single answer.


def window_on(text, anchor, before=470, after=520):
    """Extract a window around the anchor phrase."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 70)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    """Build the corpus and oracle."""
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    
    for cid, (expected_value, difficulty, anchor, company) in ITEMS.items():
        full_path = HERE / "corpus" / "full" / f"{cid}.txt"
        if not full_path.exists():
            print(f"MISSING full text {cid} — skip"); continue
        
        full_text = full_path.read_text(errors="ignore")
        win, quote = window_on(full_text, anchor)
        
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)"); continue
        
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        
        oracle.append({
            "id": cid,
            "company": company,
            "post_money_valuation": expected_value,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": difficulty,
        })
    
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    
    from collections import Counter
    print(f"wrote {len(oracle)} items with {len(set(o['post_money_valuation'] for o in oracle))} unique valuations")
    print(f"  Difficulty distribution: {dict(Counter(o['difficulty'] for o in oracle))}")


if __name__ == "__main__":
    main()
