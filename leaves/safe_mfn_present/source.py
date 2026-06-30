"""
Location: leaves/safe_mfn_present/source.py
Purpose: Build the safe_mfn_present leaf corpus + oracle (2.1.5) from real SAFE documents already
         verified by the safe_pro_rata_side_letter leaf (reused, not re-fetched -- the agent's
         original sourcing for this leaf was almost entirely wrong-document-type: convertible notes,
         a repurchase agreement, a preferred-stock redemption agreement, a bank credit facility, and
         a "safe harbor" securities-disclaimer false match -- all rejected on audit. Only Lendbuzz
         survived from the original sourcing; this corpus replaces the rest with genuine SAFEs.
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
REUSE_FULL = HERE.parent / "safe_pro_rata_side_letter" / "corpus" / "full"
OWN_FULL = HERE / "corpus" / "full"

# id -> (source_dir, label, difficulty, anchor, company)
ITEMS = {
    "d715014dex1026_htm": (
        "own", "yes", "easy",
        "If the Company issues any Subsequent Convertible Securities",
        "Lendbuzz Inc."),
    "0001477932-18-004207_mblc_ex103": (
        "reuse", "yes", "easy",
        "Subsequent Convertible Securities prior to termination",
        "Millennium Blockchain, Inc."),
    "0001477932-18-004955_mblc_ex103": (
        "reuse", "yes", "easy",
        "Subsequent Convertible Securities prior to termination",
        "THC Therapeutics, Inc."),
    "0001493152-22-033890_ex10-3": (
        "reuse", "yes", "easy",
        "Subsequent Convertible Securities prior to termination",
        "CEMTREX INC"),
    "0001424884-15-000185_exhibit10-11": (
        "reuse", "no", "medium",
        "is $4,000,000",
        "Cantabio Pharmaceuticals Inc."),
    "0001493152-22-024010_ex3-3": (
        "reuse", "no", "medium",
        "is $15,000,000",
        "Parker Clay Global, PBC"),
    "0001721868-21-000866_filename15": (
        "reuse", "no", "medium",
        "is $14,000,000",
        "SOS Hydration Inc."),
}


def window_on(text, anchor, before=420, after=900):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ 	]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 90)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (src, label, diff, anchor, company) in ITEMS.items():
        base = REUSE_FULL if src == "reuse" else OWN_FULL
        p = base / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING full text {cid} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": cid, "company": company, "safe_mfn_present": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['safe_mfn_present'] for o in oracle))}")


if __name__ == "__main__":
    main()
