"""
Location: leaves/board_seats_investor/source.py
Purpose: Build the board_seats_investor leaf corpus + SEPARATED oracle (5.1) from real SEC EDGAR
         documents (raw candidates fetched into corpus/full/). NUMBER extraction: each item's ground
         truth is the integer count of board seats an investor/class has the right to designate, hand-
         verified against the real clause text. Several oracle items share one source document with
         DIFFERENT investor-designation clauses (e.g. Emergent Capital grants both PJC=3 and a separate
         Opal Sheppard=1 seat) -- each gets its own windowed excerpt anchored at its own clause so the
         number shown to the model is unambiguous.
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# oracle_id -> (read_from_file_id, value, difficulty, anchor, company)
ITEMS = {
    "0001047469-03-010357_a2106288zex-4_8": (
        "0001047469-03-010357_a2106288zex-4_8", 3, "easy",
        "Rakepoll shall have the right to designate for nomination and approval three Investor Directors",
        "SICOR Inc."),
    "0001047469-09-010296_a2195611zex-4_1": (
        "0001047469-09-010296_a2195611zex-4_1", 1, "medium",
        "Shareholders have the right to designate only one Director",
        "Dollar General Corporation"),
    "0001104659-17-048201_a17-18633_1ex10d6_pjc": (
        "0001104659-17-048201_a17-18633_1ex10d6", 3, "medium",
        "PJC has the right to designate three",
        "Emergent Capital, Inc. (PJC)"),
    "0001104659-17-048201_a17-18633_1ex10d6_opal": (
        "0001104659-17-048201_a17-18633_1ex10d6", 1, "easy",
        "Opal Sheppard to designate one",
        "Emergent Capital, Inc. (Opal Sheppard)"),
    "0001193125-12-119900_d267119dex43_quantum": (
        "0001193125-12-119900_d267119dex43", 1, "medium",
        "Quantum Designee", "Ute Energy Corporation (Quantum)"),
    "0001193125-12-119900_d267119dex43_tribal": (
        "0001193125-12-119900_d267119dex43", 2, "medium",
        "Tribal Designees", "Ute Energy Corporation (Tribal Company)"),
    "0000950134-07-010103_d46152e8vk_mdp": (
        "0000950134-07-010103_d46152e8vk", 5, "easy",
        "will have the right to designate up to five nominees", "Cinemark Holdings, Inc. (MDP)"),
    "0000950134-07-010103_d46152e8vk_mdp_old": (
        "0000950134-07-010103_d46152e8vk", 9, "hard",
        "MDP had the right to designate up to nine of the nominees", "Cinemark Holdings, Inc. (MDP, prior agreement)"),
    "0001437749-22-001514_ex_325546": (
        "0001437749-22-001514_ex_325546", 1, "easy",
        "BDI will have the right to designate one member", "Eleison Pharmaceuticals, LLC (BDI)"),
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
    for oid, (read_from, value, diff, anchor, company) in ITEMS.items():
        p = FULL / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING full text {read_from} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "board_seats_investor": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['board_seats_investor'] for o in oracle))}")


if __name__ == "__main__":
    main()
