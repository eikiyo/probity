"""
Location: leaves/protective_provisions/source.py
Purpose: Build the protective_provisions leaf corpus + SEPARATED oracle (5.2) from real SEC EDGAR
         documents (raw candidates pre-fetched by a parallel agent into corpus/full/ +
         candidates_*.jsonl; this script is the MANUAL oracle pass -- each item was READ and
         hand-classified against the real document text by a human). YES = a real class-consent veto
         clause. NO = no such mechanism (different doc genre, post-IPO charter, or generic default
         majority-vote language with no separate-class requirement).
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
    # YES -- a real class-consent protective-provisions veto clause
    "0001047469-12-003207_a2208385zex-3_1":  ("yes", "easy",   "Protective Provisions", "Tesaro, Inc."),
    "0001628280-21-018818_exhibit31-sx1":    ("yes", "easy",   "Preferred Stock Protective Provisions", "Gitlab Inc."),
    "0000950123-10-024749_w77389exv3w1":     ("yes", "medium", "vote or written consent of the holders of at least sixty-six", "BroadSoft, Inc."),
    "0001193125-14-104715_d641160dex31":     ("yes", "medium", "vote or written consent of the holders of at least sixty-five", "SCYNEXIS, Inc."),
    "0001193125-04-167617_dex41":            ("yes", "medium", "shall not, without consent of the holders of at least a majority", "Firearms Training Systems, Inc."),
    "0000950134-06-002466_f17144exv99w2":    ("yes", "medium", "Subject to the Protective Provisions in the Operating Agreement", "JCM Partners, LLC"),
    # NO -- no class-consent veto mechanism shown
    "0001193125-07-255707_dex32":            ("no", "easy", "POST-IPO AMENDED AND RESTATED CERTIFICATE OF INCORPORATION", "NetSuite Inc."),
    "0001144204-13-065207_v361967_ex99-1":   ("no", "easy", "Letter of Intent", "UCP Holdings, Inc."),
    "0001193125-05-192064_dex101":           ("no", "easy", "NON-BINDING LETTER OF INTENT", "Non-binding LOI (Omni Energy Services counterparty)"),
    "0001193125-08-189285_dex31":            ("no", "easy", "ARTICLES OF INCORPORATION OF TRIDENT BANCSHARES", "Trident Bancshares, Inc."),
    "0001193125-17-003078_d284169dex31":     ("no", "easy", "AMENDED AND RESTATED ARTICLES OF INCORPORATION OF ALTISOURCE", "Altisource Asset Management Corp"),
    "0001068874-16-000081_imsc160408_ex10z3":("no", "medium", "Comfort Letter", "Implant Sciences Corp"),
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
        oracle.append({"id": cid, "company": company, "protective_provisions": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['protective_provisions'] for o in oracle))}")


if __name__ == "__main__":
    main()
