"""
Location: leaves/pro_rata_rights/source.py
Purpose: Build the pro_rata_rights leaf corpus + SEPARATED oracle (5.4) from real SEC EDGAR documents
         (raw candidates pre-fetched by a parallel agent into corpus/full/ + candidates_*.jsonl; this
         script is the MANUAL oracle pass -- each item was READ and hand-classified against the real
         document text by a human). YES = a live pro-rata grant. NO = no mechanism, or a TRAP where the
         operative text is a narrow WAIVER of the right (term present, but no live grant shown).
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

ITEMS = {
    # YES -- a live pro-rata grant clause
    "0001213900-26-025748_ea025686308ex10-4": ("yes", "easy",   "PRO RATA AGREEMENT", "Salspera, Inc."),
    "0001437749-26-019366_ex_971837":         ("yes", "easy",   "Pro Rata Right", "Manako Labs (via TaoWeave filing)"),
    "0001104659-26-075802_tm2617498d1_ex3-9": ("yes", "easy",   "Pro Rata Right", "Greenfield Robotics Corp"),
    "0001721868-21-000866_filename15":        ("yes", "medium", "Pro Rata Rights Agreement", "SOS Hydration Inc."),
    "0001477932-18-004207_mblc_ex103":        ("yes", "medium", "Pro Rata Rights Agreement", "Millennium Blockchain, Inc."),
    "0001424884-15-000185_exhibit10-11":      ("yes", "medium", "Pro Rata Rights Agreement", "Cantabio Pharmaceuticals Inc."),
    # NO -- no pro-rata mechanism at all (different doc genre)
    "0001193125-05-088679_dex105":            ("no", "easy", "STOCK RESTRICTION AGREEMENT", "Hoku Scientific, Inc."),
    "0001104659-20-131754_tm2030105d13_ex10-20": ("no", "easy", "STOCK RESTRICTION AGREEMENT", "Certara, Inc."),
    "0001047469-12-004869_a2208908zex-4_12":  ("no", "easy", "STOCK RESTRICTION AGREEMENT", "Supernus Pharmaceuticals Inc."),
    "0001193125-06-192598_dex1012":           ("no", "easy", "LETTER AGREEMENT", "Infinity Pharmaceuticals, Inc."),
    # NO -- TRAP: operative text is a narrow WAIVER, not a live grant
    "0000950123-15-006790_filename6":         ("no", "hard", "hereby waive the right to future stock issuances", "Rapid7, Inc."),
    "0001193125-03-085295_dex108":            ("no", "hard", "WAIVER OF PREEMPTIVE RIGHTS", "Xcyte Therapies, Inc."),
}


def window_on(text, anchor, before=420, after=900):
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before); e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20); qe = min(len(text), i + len(anchor) + 90)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    for cid, (label, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING full text {cid} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": cid, "company": company, "pro_rata_rights": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['pro_rata_rights'] for o in oracle))}")


if __name__ == "__main__":
    main()
