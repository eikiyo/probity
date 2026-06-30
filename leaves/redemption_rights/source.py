"""
Location: leaves/redemption_rights/source.py
Purpose: Build the redemption_rights leaf corpus + SEPARATED oracle from real SEC charters (most reused
         from the participation corpus, some freshly fetched). Each item was READ AND HAND-CLASSIFIED
         (manual oracle layer) as redeemable (holder/mandatory, "yes") or non-redeemable ("no"), with
         the validating quote stored separately. The model sees only the provision window.
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
    # REDEEMABLE (holder-triggered or mandatory)
    "1725255_000110465920135025": ("yes", "easy",   "all Series C Preferred Stock shall be redeemed for cash"),
    "1780201_000119312521296901": ("yes", "medium", "The shares shall be redeemed in up to two installments"),
    "1469166_000095012314005342": ("yes", "medium", "the Company shall redeem, out of funds legally available therefor, all (but not less than all)"),
    "1660280_000095012318006158": ("yes", "medium", "the Company shall redeem, out of surplus, all of the shares of Series A Preferred Stock"),
    "1478121_000119312514227132": ("yes", "hard",   "any shares of Preferred Stock shall be redeemed pursuant to subsection 3"),
    # NON-REDEEMABLE (no holder redemption right)
    "1781983_000104746919005375": ("no", "easy",   "The Preferred Stock shall not be redeemable"),
    "1447599_000119312515209758": ("no", "easy",   "Convertible Preferred Stock shall not be redeemable at the option of the holder"),
    "1556898_000119312517274422": ("no", "easy",   "The shares of Preferred Stock shall not be redeemable at the option of the holders"),
    "1888780_000157587222000105": ("no", "medium", "Series X Preferred Stock shall not be subject to redemption"),
    "1411057_000168316822006041": ("no", "medium", "Shares of Series A Preferred Stock shall not be redeemable at the option of any holder"),
}


def find_full(cid):
    for base in (LOCAL_FULL, PART_FULL):
        p = base / f"{cid}.txt"
        if p.exists():
            return p
    return None


def window_on(text, anchor, before=470, after=520):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 70)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def load_meta():
    meta = {}
    for fn in [HERE.parent / "participation_type" / "candidates.jsonl",
               HERE / "candidates_no.jsonl", HERE / "candidates_yes.jsonl"]:
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
        oracle.append({"id": cid, "company": company, "redemption_rights": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff,
                       "url": c.get("url", "")})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    from collections import Counter
    print(f"wrote {len(oracle)} items  {dict(Counter(o['redemption_rights'] for o in oracle))}")


if __name__ == "__main__":
    main()
