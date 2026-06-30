"""
Location: leaves/acceleration_trigger/source.py
Purpose: Build the acceleration_trigger leaf corpus + SEPARATED oracle from the real SEC-filed
         equity-award / employment agreements already fetched into corpus/full. Each item was READ
         AND HAND-CLASSIFIED (the manual oracle layer) as single-trigger or double-trigger, with the
         validating quote stored separately. The model sees only the provision window.
Functions: window_on(), main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# id -> (label, difficulty, anchor substring to center the provision window on).
ITEMS = {
    # DOUBLE-TRIGGER (change of control AND termination required)
    "912562_000091256215000002":  ("double-trigger", "hard",   "Double Trigger Event"),
    "1671858_000119312522280241": ("double-trigger", "medium", "Double-Trigger Acceleration"),
    "1293310_000119312512306440": ("double-trigger", "medium", "if you are subject to an Involuntary Termination"),
    "1433714_000119312514041287": ("double-trigger", "easy",   "Double Trigger Acceleration Policy"),
    "1318568_000155837016005813": ("double-trigger", "hard",   "terminated by the Company without cause or by the executive for good reason within a specified period following such change of control"),
    "1396009_000095014408007433": ("double-trigger", "hard",   "upon a Change of Control, as defined below, if an executive"),
    "1358403_000135840318000037": ("double-trigger", "easy",   "DOUBLE TRIGGER FORM"),
    # SINGLE-TRIGGER (change of control alone accelerates)
    "1452751_000119312513403444": ("single-trigger", "medium", "effective as of immediately prior to the effective date of the Change in Control"),
    "1108271_000119312504159873": ("single-trigger", "medium", "accelerated vesting of all unvested shares in the event of a Change of Control"),
    "1566826_000121390025046512": ("single-trigger", "easy",   "single-trigger acceleration upon"),
    "1158172_000095013308000368": ("single-trigger", "hard",   "fully lapsing upon the occurrence of a"),
    "1661460_000119312523020421": ("single-trigger", "easy",   "single-trigger acceleration benefit"),
    "31791_000003179124000004":   ("single-trigger", "easy",   "SINGLE-TRIGGER"),
}


def window_on(text, anchor, before=520, after=560):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 40); qe = min(len(text), i + len(anchor) + 170)
    quote = re.sub(r"\s+", " ", text[qs:qe]).strip()
    return win, quote


def main():
    cands = {json.loads(l)["id"]: json.loads(l) for l in open(HERE / "candidates.jsonl") if l.strip()}
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor) in ITEMS.items():
        f = FULL / f"{cid}.txt"
        if not f.exists():
            print(f"MISSING {cid} — skip"); continue
        win, quote = window_on(f.read_text(errors="ignore"), anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        c = cands.get(cid, {})
        oracle.append({"id": cid, "company": c.get("company", "?"), "acceleration_trigger": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff,
                       "url": c.get("url", "")})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as fo:
        for o in oracle:
            fo.write(json.dumps(o) + "\n")
    from collections import Counter
    print(f"wrote {len(oracle)} items  {dict(Counter(o['acceleration_trigger'] for o in oracle))}")


if __name__ == "__main__":
    main()
