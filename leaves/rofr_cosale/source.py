"""
Location: leaves/rofr_cosale/source.py
Purpose: Build the rofr_cosale leaf corpus + SEPARATED oracle (5.5). REUSES the drag_along corpus's
         full-text docs (zero fresh fetch -- same stockholder/transfer-agreement pool already on disk,
         per the rights_governance corpus-reuse pattern). YES = a document that grants investors a
         RoFR and/or co-sale right on another holder's TRANSFER. NO = no such right, including two
         hand-verified TRAP mechanisms that share vocabulary: a company's own buy-back RoFR on
         unvested/restricted stock, and a preemptive/pro-rata right on FUTURE financings. Each item
         was READ and hand-classified against the real document text (manual oracle layer).
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
    # YES -- investor RoFR and/or co-sale right granted on a stockholder TRANSFER
    "0000912057-13-000222_filename4":        ("yes", "easy",   "RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT",
                                                "Acceleron Pharma"),
    "0000950123-14-005490_filename11":       ("yes", "easy",   "RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT",
                                                "Upland Software"),
    "0000950144-02-006194_g76584exv4w7":     ("yes", "easy",   "RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT",
                                                "Symbion (Uniphy Healthcare)"),
    "0001683168-22-000097_aclarion_ex1008":  ("yes", "easy",   "RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT",
                                                "Aclarion"),
    "0000912057-17-000020_filename4":        ("yes", "medium", "Right of Co-Sale", "Yext"),
    "0000912057-01-534636_a2059793zex-10_20":("yes", "hard",   "co-sale rights of the Stockholders", "Digirad"),
    # NO -- clean absence (different mechanism entirely)
    "0000891020-07-000003_v25599a1exv9w1":   ("no", "easy", "VOTING AGREEMENT", "Clearwire"),
    "0001493152-16-016248_ex10-1":           ("no", "easy", "MEMBERSHIP INTEREST TRANSFER AGREEMENT", "Tauriga Sciences"),
    "0001628280-19-001592_tmhc-123118xex1031": ("no", "easy", "AGREEMENT OF EXEMPTED LIMITED PARTNERSHIP",
                                                "Taylor Morrison (TMM Holdings)"),
    # NO -- TRAP: company's own repurchase RoFR on unvested stock, not an investor transfer right
    "0001077048-05-000165_ex10-1":           ("no", "hard", "First Refusal Right", "MotivNation"),
    "0001144204-04-017555_v08033_green":     ("no", "hard", "First Refusal Right", "EntreMetrix"),
    # NO -- TRAP: preemptive/pro-rata right on FUTURE financings, not transfer co-sale
    "0001193125-21-224403_d93222dex105":     ("no", "hard", "preemptive right to participate", "OppFi"),
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
        oracle.append({"id": cid, "company": company, "rofr_cosale": label,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  {dict(Counter(o['rofr_cosale'] for o in oracle))}")


if __name__ == "__main__":
    main()
