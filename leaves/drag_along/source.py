"""
Location: leaves/drag_along/source.py
Purpose: Build the drag_along leaf corpus + SEPARATED oracle (5.6) from real SEC exhibits. YES = a
         document that OBLIGATES holders to join a sale (operative drag-along clause). NO = a full
         (non-amendment) Right-of-First-Refusal/Co-Sale agreement whose text grants only a RIGHT to
         participate and contains ZERO "drag" occurrences (deterministic absence, hand-verified). Each
         item was READ and hand-classified (manual oracle layer); the model sees only the clause window.
Functions: window_on(), load_meta(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

ITEMS = {
    # YES — operative drag-along OBLIGATION (holders forced to sell/vote in a sale)
    "0001193125-11-327662_d261388dex43":     ("yes", "easy",   "shall be obligated to, and shall, sell"),
    "0001047469-07-002039_a2176594zex-4_6":  ("yes", "easy",   "Drag-Along Stockholder shall be required to participate"),
    "0001193125-06-053345_dex101":           ("yes", "easy",   "Drag Along Obligation"),
    "0001104659-12-073362_a12-25837_1ex10d6":("yes", "medium", "shall also vote in favor of any Drag-Along Sale"),
    "0000950123-02-009442_e62399a2exv10w20": ("yes", "medium", "Drag-Along Stockholders shall otherwise participate"),
    "0001047469-06-008353_a2171167zex-10_13":("yes", "hard",   "Drag-Along Sale pursuant to Section 2.05"),
    # NO — full RoFR/Co-Sale agreement: a RIGHT (not obligation) to participate; zero "drag" in the text
    "0001047469-13-008148_a2216187zex-10_3": ("no",  "easy",   "elect to participate"),
    "0000912057-17-000020_filename4":        ("no",  "easy",   "Right of Co-Sale"),
    "0000950123-10-031429_b80142exv4w4":     ("no",  "medium", "right to participate in such sale"),
    "0000912057-01-534636_a2059793zex-10_20":("no",  "medium", "Co-Sale Right"),
    "0000950123-14-005490_filename11":       ("no",  "easy",   "right to participate in such sale"),
    "0001144204-16-141777_v455883_ex3-2":    ("no",  "medium", "right to participate in such sale"),
}


def window_on(text, anchor, before=420, after=760):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 90)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def load_meta():
    meta = {}
    for fn in [HERE / "candidates_present.jsonl", HERE / "candidates_absent.jsonl"]:
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
        p = FULL / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING full text {cid} — skip"); continue
        full = p.read_text(errors="ignore")
        # fail-closed safety net: a NO item whose text actually contains 'drag' is a mislabel
        if label == "no" and "drag" in full.lower():
            print(f"DROP {cid}: labelled 'no' but text contains 'drag' — fail-closed"); continue
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        c = meta.get(cid, {})
        company = re.sub(r"\s*\(.*$", "", c.get("company", "?")).strip()
        oracle.append({"id": cid, "company": company, "drag_along": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff,
                       "url": c.get("url", "")})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['drag_along'] for o in oracle))}")


if __name__ == "__main__":
    main()
