"""
Location: leaves/auto_conversion_trigger/source.py
Purpose: Build the auto_conversion_trigger leaf corpus + oracle (1.6.2) from real SEC EDGAR
         preferred-stock charter documents. Extract the QPO (Qualified Public Offering)
         threshold in USD—the aggregate gross proceeds amount that AUTOMATICALLY triggers
         conversion of preferred to common stock.
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

# id -> (source_leaf_dir, full_text_id, value, difficulty, anchor, company)
# value = the dollar threshold (aggregate gross proceeds) that triggers automatic conversion
# anchor = the exact phrase in the charter text containing the trigger clause
ITEMS = {
    "silicon_energy_30m": (
        "conversion_ratio", "0000891618-01-501192_f73225orex3-1", 30000000, "easy",
        "aggregate gross proceeds to the corporation exceed $30,000,000",
        "Silicon Energy Corp"),
    "elastic_bv_30m": (
        "conversion_ratio", "d588632dex31", 30000000, "easy",
        "aggregate cash proceeds to the company of not less than thirty million United States dollar (USD 30,000,000)",
        "Elastic B.V."),
    "asana_100m": (
        "conversion_ratio", "d855753dex31", 100000000, "easy",
        "aggregate cash proceeds to the Corporation of not less than $100,000,000",
        "Asana, Inc."),
    "filename2_30m": (
        "conversion_ratio", "filename2", 30000000, "medium",
        "Net proceeds of at least $30,000,000",
        "Exagen Diagnostics, Inc."),
    "terrascend_30m": (
        "conversion_ratio", "tm2129883d1_ex3-2", 30000000, "medium",
        "gross proceeds in excess of US$30,000,000",
        "TerraScend Corp."),
}
# tm2129883d2_ex3-3 (a government-stamped Ontario certificate for the SAME TerraScend articles of
# amendment as tm2129883d1_ex3-2) dropped as a duplicate filing of the same legal event, not an
# independent data point. Company for both was mislabeled "Altira Group Corp" by the sourcing agent
# (never traced back to the real registrant in the document's own cover text) -- corrected to
# TerraScend Corp. (read from the Articles of Amendment header) and for filename2 -- corrected from
# placeholder "Unknown" to Exagen Diagnostics, Inc. (read from the Certificate of Incorporation
# header). Independent audit catch, M3.1.


def window_on(text, anchor, before=420, after=900):
    """Extract a window around the anchor phrase, plus a shorter validating quote."""
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
    for oid, (src_leaf, read_from, value, diff, anchor, company) in ITEMS.items():
        p = HERE.parent / src_leaf / "corpus" / "full" / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING full text {read_from} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor[:50]!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "auto_conversion_trigger": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['auto_conversion_trigger'] for o in oracle))}")


if __name__ == "__main__":
    main()
