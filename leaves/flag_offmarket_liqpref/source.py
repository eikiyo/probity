"""
Location: leaves/flag_offmarket_liqpref/source.py
Purpose: Build the flag_offmarket_liqpref leaf corpus + SEPARATED oracle from real SEC charters (most
         reused from the participation corpus, one freshly fetched). Each item's liquidation-preference
         MULTIPLE was READ AND HAND-CLASSIFIED (manual oracle layer) as off-market (>1x, "yes") or
         standard (1x, "no"), with the validating quote stored separately.
Functions: find_full(), window_on(), main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
LOCAL_FULL = HERE / "corpus" / "full"
PART_FULL = HERE.parent / "participation_type" / "corpus" / "full"

ITEMS = {
    # OFF-MARKET (>1x)
    "1461993_000119312517361673": ("yes", "easy",   "liquidation preference equal to two times the original issue price"),
    "877931_000119312508100740":  ("yes", "easy",   "an amount equal to three times the Original Issue Price"),
    "1427222_000101376208000358": ("yes", "medium", "the amount of $44.44 (two times the original issue price)"),
    "1780201_000119312521296901": ("yes", "hard",   "two times the original issue price of $1.00 per share until August"),
    "1130258_000104746906010148": ("yes", "medium", "liquidation preference of $2.89, or two times the original issue price"),
    # STANDARD (1x)
    "1447599_000119312515209758": ("no", "medium", "an amount per share equal to the sum of the Original Issue Price"),
    "1722271_000091205720000111": ("no", "easy",   "an amount per share equal to the applicable Original Issue Price"),
    "317788_000114420415017108":  ("no", "medium", "an amount equal to the original issue price of $1.00 per share for Series A"),
    "1119700_000114420405033377": ("no", "medium", "shall mean the original issue price per share of the Series A Preferred Stock"),
    "1327811_000132781118000039": ("no", "hard",   "an amount equal to their original issue price per share, plus any declared but unpaid dividends in the preference order"),
    "1469166_000095012314005342": ("no", "easy",   "an amount per share equal to the Series B Original Issue Price"),
}


def find_full(cid):
    for base in (LOCAL_FULL, PART_FULL):
        p = base / f"{cid}.txt"
        if p.exists():
            return p
    return None


def window_on(text, anchor, before=480, after=520):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 60)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def load_meta():
    meta = {}
    for fn in [HERE.parent / "participation_type" / "candidates.jsonl", HERE / "candidates_true.jsonl"]:
        if fn.exists():
            for l in open(fn):
                if l.strip():
                    d = json.loads(l); meta[d["id"]] = d
    return meta


def main():
    meta = load_meta()
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor) in ITEMS.items():
        full = find_full(cid)
        if not full:
            print(f"MISSING full text {cid} — skip"); continue
        win, quote = window_on(full.read_text(errors="ignore"), anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        c = meta.get(cid, {})
        company = re.sub(r"\s*\(.*$", "", c.get("company", "?")).strip()
        oracle.append({"id": cid, "company": company, "flag_offmarket_liqpref": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff,
                       "url": c.get("url", "")})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    from collections import Counter
    print(f"wrote {len(oracle)} items  {dict(Counter(o['flag_offmarket_liqpref'] for o in oracle))}")


if __name__ == "__main__":
    main()
