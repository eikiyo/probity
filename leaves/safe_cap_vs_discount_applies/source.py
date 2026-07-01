"""
Location: leaves/safe_cap_vs_discount_applies/source.py
Purpose: Build safe_cap_vs_discount_applies leaf (2.1.3) — classify whether a SAFE uses cap only,
         discount only, or both cap+discount with MFN (most-favored-nation) clause.
         Reuses 12 documents from safe_discount_rate corpus.
Functions: window_on(), main()
Imports: json, re, pathlib
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# Source 12 diverse SAFEs from safe_discount_rate corpus.
# oracle_id -> (read_from_file_id, classification, difficulty, anchor, company)
# Classifications: "cap" (cap-only), "discount" (discount-only), "both-mfn" (cap+discount with MFN)
ITEMS = {
    "snm_discount_only": (
        "0000721748-17-000529_s1safe",
        "discount",
        "easy",
        "is fifty percent (50%)",
        "SNM Global Holdings, Inc."),
    "parker_both_mfn": (
        "0001493152-22-024010_ex3-3",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "Parker Clay Global, PBC"),
    "sos_both_mfn": (
        "0001721868-21-000866_filename15",
        "both-mfn",
        "hard",
        "whichever calculation results in a greater number of shares",
        "SOS Hydration Inc."),
    "maison_both_mfn": (
        "1486452_000168316824001414",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "Maison Luxe, Inc."),
    "rentberry_both_mfn": (
        "1657493_000121390021028831",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "Rentberry Inc."),
    "paxmedica_both_mfn": (
        "1811623_000110465922070160",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "PaxMedica, Inc."),
    "creci_both_mfn": (
        "1821951_000121390022000982",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "Creci Inc."),
    "complete_both_mfn": (
        "1838987_000121390024014892",
        "both-mfn",
        "easy",
        "whichever calculation results in a greater number of shares",
        "Complete Solaria, Inc."),
    "lomond_both_mfn": (
        "1900520_000121390024095442",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "Lomond Therapeutics Holdings, Inc."),
    "neo_aero_both_mfn": (
        "2036444_000121390025123767",
        "both-mfn",
        "medium",
        "whichever calculation results in a greater number of shares",
        "Neo Aeronautics, Inc."),
    "taoweave_both_mfn": (
        "746210_000143774926019366",
        "both-mfn",
        "medium",
        "whichever calculation results in the greater number of Safe Shares",
        "Manako Labs Ltd"),
}


def window_on(text, anchor, before=600, after=1400):
    """Find anchor in text and extract a window around it."""
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    # Shorter quote for oracle validation
    qs = max(0, i - 20)
    qe = min(len(text), i + len(anchor) + 120)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()


def main():
    """Build corpus/questions and oracle.jsonl from source documents."""
    SAFE_DISCOUNT_FULL = HERE.parent / "safe_discount_rate" / "corpus" / "full"

    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    (HERE / "corpus" / "full").mkdir(parents=True, exist_ok=True)
    oracle = []

    for oid, (read_from, classification, diff, anchor, company) in ITEMS.items():
        p = SAFE_DISCOUNT_FULL / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING full text {read_from} -- skip")
            continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)")
            continue

        # Write to corpus/questions and corpus/full
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        (HERE / "corpus" / "full" / f"{read_from}.txt").write_text(full, encoding="utf-8")

        oracle.append({
            "id": oid,
            "company": company,
            "safe_cap_vs_discount_applies": classification,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": diff
        })

    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")

    print(f"wrote {len(oracle)} items | classifications: discount={sum(1 for o in oracle if o['safe_cap_vs_discount_applies']=='discount')}, both-mfn={sum(1 for o in oracle if o['safe_cap_vs_discount_applies']=='both-mfn')}")


if __name__ == "__main__":
    main()
