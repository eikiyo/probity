"""
Location: leaves/dividend_cumulative/source.py
Purpose: Build the dividend_cumulative leaf corpus + SEPARATED oracle by REUSING the already-fetched
         SEC charter corpus (leaves/participation_type/corpus/full). Each item is a real charter whose
         dividend clause was READ AND HAND-CLASSIFIED (the manual oracle layer) as cumulative or
         non-cumulative, with the validating quote stored separately. The model sees only the clause.
Functions: window_on(), main()
Calls: candidates.jsonl (company/url), participation charters (full text)
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CHARTERS = HERE.parent / "participation_type" / "corpus" / "full"
CANDS = HERE.parent / "participation_type" / "candidates.jsonl"

# id -> (label, difficulty, anchor substring to center the clause window on).
# Each label was assigned by reading the real dividend clause; anchor is the determinative phrase.
ITEMS = {
    "1067837_000119312515255977": ("cumulative", "easy", "cumulative cash dividends"),
    "1119700_000114420405033377": ("cumulative", "easy", "cumulative dividend"),
    "1200720_000104746904001493": ("cumulative", "hard", "if and when declared by the Board of Directors and are cumulative"),
    "1337675_000114420407009831": ("cumulative", "hard", "and are cumulative"),
    "1461993_000119312517361673": ("cumulative", "medium", "These dividends are cumulative"),
    "1568194_000119312522082723": ("cumulative", "hard", "cumulative cash dividends"),
    "1620179_000104746918002690": ("cumulative", "easy", "cumulative dividends at a rate per annum"),
    "1725255_000110465920135025": ("cumulative", "hard", "whether or not declared, and shall be cumulative"),
    "1445499_000095012321001942": ("non-cumulative", "easy", "Dividends are non-cumulative"),
    "1447599_000119312515209758": ("non-cumulative", "medium", "Such dividends shall not be cumulative"),
    "1477449_000155837016008265": ("non-cumulative", "easy", "Dividends are noncumulative"),
    "1722271_000091205720000111": ("non-cumulative", "medium", "Such dividends shall not be cumulative"),
    "1585521_000119312519083351": ("non-cumulative", "medium", "shall not be cumulative"),
    "1053148_000095014401503351": ("non-cumulative", "easy", "non-cumulative dividends at the per annum rate"),
    "1305253_000119312516625139": ("non-cumulative", "medium", "dividends declared are non-cumulative"),
    "1604950_000119312517316695": ("non-cumulative", "easy", "Non-Cumulative Dividend"),
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
    cands = {json.loads(l)["id"]: json.loads(l) for l in open(CANDS) if l.strip()}
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor) in ITEMS.items():
        full = (CHARTERS / f"{cid}.txt")
        if not full.exists():
            print(f"MISSING charter {cid} — skip"); continue
        text = full.read_text(errors="ignore")
        win, quote = window_on(text, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        c = cands.get(cid, {})
        company = re.sub(r"\s*\(.*$", "", c.get("company", "?")).strip()
        oracle.append({"id": cid, "company": company, "dividend_cumulative": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff,
                       "url": c.get("url", "")})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    from collections import Counter
    print(f"wrote {len(oracle)} items  {dict(Counter(o['dividend_cumulative'] for o in oracle))}")


if __name__ == "__main__":
    main()
