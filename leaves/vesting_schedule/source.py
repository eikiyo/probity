"""
Location: leaves/vesting_schedule/source.py
Purpose: Build the vesting_schedule leaf corpus + SEPARATED oracle (6.1) from real SEC EDGAR documents
         (raw candidates pre-fetched by sibling agents into corpus/full and already used by
         acceleration_trigger and cliff_present; this script is the MANUAL oracle pass -- each item
         was READ and hand-extracted from the real document text by reading the actual vesting clause).
         The model sees only the provision window and must extract + normalize the vesting schedule
         to a canonical string format: "Nyr/Myr-cliff" or "Nyr/no-cliff".
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
ACCEL_CORPUS = HERE.parent / "acceleration_trigger" / "corpus" / "full"
CLIFF_CORPUS = HERE.parent / "cliff_present" / "corpus" / "full"

# id -> (normalized_schedule, difficulty, anchor substring, company).
# Each item was READ and HAND-EXTRACTED from the actual document text, confirming the vesting terms.
# Normalized format: "4yr/1yr-cliff" = 4-year total, 1-year cliff; "3yr/no-cliff" = 3-year, no cliff.
ITEMS = {
    # From acceleration_trigger corpus
    "1293310_000119312512306440": ("4yr/1yr-cliff", "easy", "four-year vesting schedule, with a 12-month cliff", "KALOBIOS PHARMACEUTICALS INC"),
    "1452751_000119312513403444": ("4yr/1yr-cliff", "medium", "four-year vesting schedule subject to your Continuous Service", "NIMBLE STORAGE, INC."),
    "1108271_000119312504159873": ("1.5yr/no-cliff", "medium", "eighteen (18) month vesting schedule", "CONOR MEDSYSTEMS, INC."),

    # From cliff_present corpus
    "0001558370-21-008713_giii-20210628x8k": ("3yr/cliff", "easy", "three-year cliff-vesting", "G-III Apparel Group, Ltd."),
    "0001451809-24-000052_ex1034offerofemployment-sa": ("4yr/no-cliff", "easy", "four-year vesting schedule with no cliff", "SITIME CORP"),
    "0001144204-15-053727_v419640_ex10-1": ("4yr/no-cliff", "easy", "vests over four years of employment with no cliff", "ATOSSA GENETICS INC."),
    "0001516513-23-000036_ex-107xcraigoverpeckofferl": ("4yr/no-cliff", "medium", "4yr RSU, vests qtrly, no cliff", "DOXIMITY, INC."),
    "0000020740-17-000006_a201610kex1012": ("4yr/no-cliff", "hard", "shall vest on each anniversary", "CLARCOR INC."),
    "0001104659-09-054183_a09-26145_18k": ("3yr/no-cliff", "hard", "waiver of one-year cliff", "WORLD HEART CORP"),
}


# Excluded (audit trail, independent orchestrator audit, M3.1):
#   brandywine (0000790816-14-000054): the shown window never states an explicit duration (only that
#     the award is "scheduled to vest on April 15, 2017" against a 2014 filing date) -- "3yr" was
#     INFERRED from date arithmetic the model is never given both endpoints to perform; dropped.
#   viad (0001299933-11-000951): the shown window states BOTH a five-year cliff-vesting agreement AND
#     a three-year cliff-vesting agreement for the SAME executives with no signal which one governs --
#     multi-value-ambiguity, dropped.


def window_on(text, anchor, before=520, after=560):
    """Return (clause_window, validating_quote) centered on anchor phrase."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    # validating quote: ~the sentence around the anchor
    qs = max(0, i - 40)
    qe = min(len(text), i + len(anchor) + 170)
    quote = re.sub(r"\s+", " ", text[qs:qe]).strip()
    return win, quote


def main():
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []

    for cid, (schedule, diff, anchor, company) in ITEMS.items():
        # Try acceleration_trigger corpus first, then cliff_present
        f = ACCEL_CORPUS / f"{cid}.txt"
        if not f.exists():
            f = CLIFF_CORPUS / f"{cid}.txt"

        if not f.exists():
            print(f"MISSING {cid} — skip")
            continue

        text = f.read_text(errors="ignore")
        win, quote = window_on(text, anchor)

        if not win:
            print(f"ANCHOR not found in {cid} ({anchor!r}) — skip (fail-closed)")
            continue

        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        oracle.append({
            "id": cid,
            "company": company,
            "vesting_schedule": schedule,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff,
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    print(f"wrote {len(oracle)} items  {dict(Counter(o['vesting_schedule'] for o in oracle))}")


if __name__ == "__main__":
    main()
