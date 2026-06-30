"""
Location: leaves/flag_full_ratchet/source.py
Purpose: Build the flag_full_ratchet leaf corpus + SEPARATED oracle from real SEC filings.
         Each item's anti-dilution type was READ AND HAND-CLASSIFIED (manual oracle layer) 
         as full-ratchet (yes) or weighted-average/none (no), with the validating quote stored 
         separately.
Functions: find_full(), window_on(), load_meta(), main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
LOCAL_FULL = HERE / "corpus" / "full"
PART_FULL = HERE.parent / "participation_type" / "corpus" / "full"
ANTIDIL_FULL = HERE.parent / "antidilution_type" / "corpus" / "full"

ITEMS = {
    # FULL-RATCHET (yes) - genuinely preferred-stock conversion price reset to new issuance price
    "0000950123-14-003249_filename2.htm": ("yes", "easy",   "Full Ratchet Adjustment Date"),
    "0001104659-14-075598_a14-23423_18k.htm": ("yes", "medium", "Full Ratchet Anti-Dilution Provision"),
    "0001144204-14-015857_v371796_8k.htm": ("yes", "medium", "full ratchet"),
    "0001193125-12-290128_d377132d8k.htm": ("yes", "hard", "Full-Ratchet Anti-Dilution Provi"),

    # WEIGHTED-AVERAGE (no) - genuinely preferred-stock conversion price adjusts by formula
    "0000950134-02-011491_d99683e8vk.txt": ("no", "easy", "weighted average"),
    "1082733_000165495426003578": ("no", "medium", "broad-based weighted-average anti-dilution adjustment"),
    "1103078_000119312505072191": ("no", "medium", "broad-based weighted average anti-dilution adjustment"),
}
# Excluded (audit caught wrong document type or mislabel, kept for trail, NEVER in oracle):
#   LEAP THERAPEUTICS (a18-3138), MERRIMAN CURHAN FORD (v169335): the full-ratchet clause is on
#     WARRANTS, not the preferred stock itself -- wrong instrument for this field (task.py scopes
#     this leaf to preferred-stock anti-dilution).
#   LIGHTNING GAMING (s22-10735): "Amendment Of Warrants" -- about warrants entirely, no preferred-
#     stock anti-dilution language at all.
#   DIGITAL LIGHTWAVE (exhibit-103): a Lender/Borrower convertible-debt/loan document, not preferred
#     stock.
#   CORMEDIX (filename16): an SEC comment-letter response about EPS "weighted average shares"
#     accounting disclosure -- the anchor match was on an unrelated accounting term, not an
#     anti-dilution clause at all.
#   NYTEX ENERGY (d377132d8k) was originally mislabeled "no" -- the excerpt explicitly names itself
#     "Full-Ratchet Anti-Dilution Provision" applying to Series A Preferred Stock conversion price,
#     reset fully to the new lower price on a dilutive issuance. Re-anchored and moved to "yes" above.


def find_full(cid):
    """Find the full-text document in local, participation_type, or antidilution_type corpus."""
    for base in (LOCAL_FULL, PART_FULL, ANTIDIL_FULL):
        p = base / f"{cid}.txt"
        if p.exists():
            return p
    return None


def window_on(text, anchor, before=480, after=520):
    """Extract a window around the anchor phrase."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20)
    qe = min(len(text), i + len(anchor) + 60)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


MANUAL_COMPANY = {
    "0001104659-14-075598_a14-23423_18k.htm": "MINES MANAGEMENT, INC.",
    "1082733_000165495426003578": "VISIUM TECHNOLOGIES, INC.",
    "1103078_000119312505072191": "RASER TECHNOLOGIES INC",
}


def load_meta():
    """Load metadata from candidates files."""
    meta = {}
    for fn in [HERE / "candidates_full_ratchet.jsonl", HERE / "candidates_weighted_avg.jsonl"]:
        if fn.exists():
            for l in open(fn):
                if l.strip():
                    d = json.loads(l)
                    meta[d["id"]] = d
    return meta


def main():
    meta = load_meta()
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor) in ITEMS.items():
        full = find_full(cid)
        if not full:
            print(f"MISSING full text {cid} — skip")
            continue
        win, quote = window_on(full.read_text(errors="ignore"), anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)")
            continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        c = meta.get(cid, {})
        company = re.sub(r"\s*\(.*$", "", c.get("company", MANUAL_COMPANY.get(cid, "?"))).strip()
        oracle.append({
            "id": cid,
            "company": company,
            "flag_full_ratchet": label,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff,
            "url": c.get("url", "")
        })
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    from collections import Counter
    counts = Counter(o['flag_full_ratchet'] for o in oracle)
    print(f"wrote {len(oracle)} items  {dict(counts)}")


if __name__ == "__main__":
    main()
