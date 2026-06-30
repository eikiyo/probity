"""
Location: leaves/safe_pro_rata_side_letter/source.py
Purpose: Build the safe_pro_rata_side_letter leaf corpus + SEPARATED oracle from real SEC EDGAR documents
         (fetch pre-vetted SAFE documents; this script is the MANUAL oracle pass -- each item was READ
         and hand-classified against the real document text). YES = SAFE or convertible doc that includes
         an embedded or standalone "Pro Rata Rights Agreement" clause granting side-letter rights. 
         NO = SAFE without such side-letter language (standard conversion only).
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
    # YES -- SAFE with Pro Rata Rights Agreement side letter clause
    "0000721748-17-000529_s1safe": ("yes", "easy", "Pro Rata Rights Agreement", "SNM Global Holdings, Inc."),
    "0000721748-17-000577_s1safe": ("yes", "easy", "Pro Rata Rights Agreement", "SNM Global Holdings, Inc."),
    "0001424884-15-000185_exhibit10-11": ("yes", "medium", "Pro Rata Rights Agreement", "Cantabio Pharmaceuticals Inc."),
    "0001477932-18-004207_mblc_ex103": ("yes", "medium", "Pro Rata Rights Agreement", "Millennium Blockchain, Inc."),
    "0001477932-18-004955_mblc_ex103": ("yes", "medium", "Pro Rata Rights Agreement", "THC Therapeutics, Inc."),
    "0001493152-22-024010_ex3-3": ("yes", "hard", "Pro Rata Rights Agreement", "Parker Clay Global, PBC"),
    "0001493152-22-033890_ex10-3": ("yes", "hard", "Pro Rata Rights Agreement", "CEMTREX INC"),
    "0001721868-21-000866_filename15": ("yes", "hard", "Pro Rata Rights Agreement", "SOS Hydration Inc."),
    "0001903596-22-000170_f2ssos102121ex4_13": ("yes", "hard", "Pro Rata Rights Agreement", "SOS Hydration Inc."),
    # NO -- SAFE without Pro Rata Rights Agreement side letter clause
    "0001193125-26-035812_filename4": ("no", "easy", "SAFE", "Rare Earths Americas, Inc."),
    "0001193125-26-153091_rea-ex4_2": ("no", "easy", "Next Equity Financing", "Rare Earths Americas, Inc."),
    "0001117768-17-001842_mainbody": ("no", "medium", "SAFE", "Orangehook, Inc."),
    "0001575872-26-000442_amass027_8k": ("no", "medium", "Conversion", "AMASS BRANDS"),
    "0001437749-26-019366_twav20260603_8k": ("no", "hard", "Equity Financing", "TaoWeave, Inc."),
    "0001104659-21-005324_tm213128d1_ex99-1": ("no", "hard", "SAFE", "CHIMERIX INC"),
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
        oracle.append({"id": cid, "company": company, "safe_pro_rata_side_letter": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['safe_pro_rata_side_letter'] for o in oracle))}")


if __name__ == "__main__":
    main()
