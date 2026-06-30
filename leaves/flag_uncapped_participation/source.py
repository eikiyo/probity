"""
Location: leaves/flag_uncapped_participation/source.py
Purpose: Build the flag_uncapped_participation leaf corpus + SEPARATED oracle (8.3) from real SEC EDGAR
         documents. YES = preferred holders have UNCAPPED participating-preferred rights (participate in
         remaining proceeds with NO CAP). NO = either non-participating, or participating-but-capped
         (explicit cap on total return), or no preference language.
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
    # YES -- uncapped participating preferred (participate in remaining proceeds without a cap)
    "1076103_000091476003000217":  ("yes", "hard",   "thereafter, the Holders of Preferred Stock shall be entitled to participate with the holders of Common Stock", "IESI Corp"),
    "1374128_000119312517292995":  ("yes", "easy",   "the remaining assets of the Company available for distribution will be distributed ratably among the holders of common stock and preferred stock", "Spirox, Inc."),
    "1604950_000119312517316695":  ("yes", "medium", "remaining assets of the Corporation available for distribution to its stockholders shall be distributed among the holders of the shares of Preferred Stock and Common Stock", "scPharmaceuticals Inc."),
    "1722271_000091205720000111":  ("yes", "medium", "the remaining assets of the Corporation available for distribution to its stockholders shall be distributed among the holders of the shares of Preferred Stock and Common Stock", "Akouos, Inc."),
    # NO -- non-participating (greater-of structure)
    "1314727_000095012317011479":  ("no", "easy",   "greater of (x) the Liquidation Preference specified for such share of Series C Preferred", "Sonos Inc"),
    "1585521_000119312519083351":  ("no", "easy",   "greater of (x) the Liquidation Preference for the shares of the Series A Preferred Stock", "Zoom Video Communications, Inc."),
    "319458_000143774924026112":   ("no", "easy",   "greater of (x) the Liquidation Preference and (y)", "Enservco Corp"),
    "828146_000110465921129281":   ("no", "easy",   "greater of (a) the Original Issue Price", "Interlink Electronics Inc"),
    "1469166_000095012314005342":  ("no", "medium", "greater of (i) the Series C Preferred Original Issue Price", "EndoStim, Inc."),
    # NO -- explicitly capped participation
    "1113481_000111348114000003":  ("no", "medium", "shall not exceed the Maximum Participation Amount", "The Medicines Co (Rempex)"),
    "1200720_000104746904001493":  ("no", "medium", "until the Preferred Stockholders have received 3.5 times", "Jazz Semiconductor Inc"),
    "1327811_000132781118000039":  ("no", "medium", "until the holders of Series E have received an aggregate of three times", "Workday, Inc."),
    "1344413_000089161805000914":  ("no", "medium", "until such time as the holders of Preferred Stock have received", "Alexza Pharmaceuticals Inc."),
    "1447599_000119312515209758":  ("no", "hard",   "Participation Cap Amount", "Fitbit Inc"),
    "1053148_000095014401503351":  ("no", "medium", "total payments in an amount equal to $6.58 per share", "Internet Security Systems Inc"),
    # NO -- non-participating (complex/hard cases)
    "1067837_000119312515255977":  ("no", "hard",   "shall not be entitled to participate in any further distributions", "Entercom Communications Corp"),
    "1119700_000114420405033377":  ("no", "hard",   "would receive on an as-converted basis an amount greater than the Liquidation Preference", "BioAccelerate Holdings Inc"),
    "1478121_000119312514227132":  ("no", "hard",   "greater of (i) the Maximum Participation Amount", "Pfenex Inc."),
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
            print(f"ANCHOR not found in {cid} ({anchor[:50]!r}...) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": cid, "company": company, "flag_uncapped_participation": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['flag_uncapped_participation'] for o in oracle))}")


if __name__ == "__main__":
    main()
