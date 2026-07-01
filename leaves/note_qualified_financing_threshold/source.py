"""
Location: leaves/note_qualified_financing_threshold/source.py
Purpose: Build the note_qualified_financing_threshold leaf corpus + SEPARATED oracle (2.2.6) from real SEC EDGAR
         documents. NUMBER extraction: each item's ground truth is the minimum aggregate dollar amount
         that qualifies as a "Qualified Financing" on a convertible promissory note.
Functions: main()
Calls: engine.corpus_utils.window_on
Imports: json, pathlib, collections, sys
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from corpus_utils import window_on  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# oracle_id -> (read_from_file_id, qf_value, difficulty, anchor, company)
# QF_VALUE is the bare number in dollars (e.g., 10000000, 40000000)
ITEMS = {
    "lanzatech_40m": (
        "exhibit41-formofconvertibl.htm",
        40000000,
        "medium",
        "minimum gross proceeds in an amount that is the greater of (i) $40,000,000 and (ii) 50% of the total principal amount under the outstanding Notes",
        "LanzaTech Global, Inc."
    ),
    "xtiaero_10m": (
        "ea0262559-8k_xtiaero.htm",
        10000000,
        "medium",
        "the earliest of the first Qualified Financing of at least $10 million",
        "Valkyrie Sciences Holdings LLC"
    ),
}


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
            print(f"ANCHOR not found in {read_from} ({anchor[:50]!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "note_qualified_financing_threshold": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={sorted(set(o['note_qualified_financing_threshold'] for o in oracle))}")


if __name__ == "__main__":
    main()

# Excluded items (audit trail):
#   capnia_* (000095012314005097_filename26.txt, 000119312514231812_d711637dex1015.txt):
#                   WRONG INSTRUMENT -- these are omnibus amendments to convertible notes, but they
#                   reference only "Next Financing" with no explicit dollar threshold defined.
#                   The documents define conversion mechanics for "Next Financing" events but contain
#                   NO "Qualified Financing" clause with a minimum aggregate proceeds dollar amount.
#                   Excluded (fail-closed).
