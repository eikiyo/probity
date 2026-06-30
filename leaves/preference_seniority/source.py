"""
Location: leaves/preference_seniority/source.py
Purpose: Build the preference_seniority leaf corpus + SEPARATED oracle. Sources are real SEC charters,
         some REUSED from the participation_type corpus and some freshly fetched into ./corpus/full.
         Each item's inter-series liquidation seniority was READ AND HAND-CLASSIFIED (manual oracle
         layer) as pari-passu or stacked, with the validating quote stored separately.
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
    # STACKED (a senior series is paid before a junior one)
    "1076103_000091476003000217": ("stacked", "medium", "shall rank senior to the Series D Preferred Stock, Series C Preferred Stock"),
    "1341470_000119312509004895": ("stacked", "medium", "ranking junior to the Series C Preferred Stock in respect of the right to receive assets upon the liquidation"),
    "1477449_000155837016008265": ("stacked", "easy",   "in the following order of priority"),
    "932699_000093269916000092":  ("stacked", "easy",   "shall rank senior to the Series A Preferred Stock in liquidation preference"),
    "1092283_000119312505071414": ("stacked", "easy",   "The Series C Preferred Stock ranks senior to the Series B Preferred Stock"),
    # PARI-PASSU (all series rank equally / share ratably)
    "1585521_000119312519083351": ("pari-passu", "hard",   "shall be distributed among them on a pro rata basis according to the respective amounts"),
    "1113481_000111348114000003": ("pari-passu", "medium", "the Series A and Series B stockholders will share ratably"),
    "1556898_000119312517274422": ("pari-passu", "hard",   "distributed ratably among the holders of Preferred Stock in proportion to the preferential amount"),
    "745788_000114420408016648":  ("pari-passu", "easy",   "the holders of the Series A Stock shall rank pari passu with the Series B Stock"),
    "878720_000089843001500356":  ("pari-passu", "medium", "the Series B Preferred Stock shall rank pari passu with the Series A Preferred Stock and the Series C Preferred Stock"),
    "1123195_000112319502000020": ("pari-passu", "hard",   "shall share ratably in such distribution of assets in proportion to the amount"),
}


def find_full(cid):
    for base in (LOCAL_FULL, PART_FULL):
        p = base / f"{cid}.txt"
        if p.exists():
            return p
    return None


def window_on(text, anchor, before=560, after=540):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 30); qe = min(len(text), i + len(anchor) + 130)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def load_meta():
    meta = {}
    for fn in [HERE.parent / "participation_type" / "candidates.jsonl",
               HERE / "candidates_stack.jsonl", HERE / "candidates_pari.jsonl"]:
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
        oracle.append({"id": cid, "company": company, "preference_seniority": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff,
                       "url": c.get("url", "")})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    from collections import Counter
    print(f"wrote {len(oracle)} items  {dict(Counter(o['preference_seniority'] for o in oracle))}")


if __name__ == "__main__":
    main()
