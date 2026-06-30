"""
Location: leaves/conversion_ratio/source.py
Purpose: Build the conversion_ratio leaf corpus + oracle (1.6.1) from real SEC EDGAR preferred-
         stock charter documents, reused from sibling leaves' already-fetched corpora. The agent's
         original sourcing found only ONE candidate, and it was wrong-topic (Class B->Class A common
         stock conversion, not preferred-to-common) -- replaced entirely after audit.
Functions: window_on(), main()
Imports: json, re, pathlib, collections
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

# id -> (source_leaf_dir, full_text_id, value, difficulty, anchor, company)
ITEMS = {
    "loop_industries_1to1": (
        "protective_provisions", "0001654954-19-005416_loop_ex4-1", 1, "easy",
        "convertible into one fully paid and nonassessable share of common stock",
        "Loop Industries, Inc."),
    "precom_2to1": (
        "preference_seniority", "1123195_000112319502000020", 2, "easy",
        "convertible into two shares of Common Stock",
        "Precom Technology, Inc."),
    "air_defense_100to1": (
        "antidilution_type", "1077915_000107878212001904", 100, "medium",
        "convertible into one hundred shares of Common Stock",
        "Air Defense Services, Inc."),
    "boston_life_sciences_8000to1": (
        "antidilution_type", "94784_000119312503094870", 8000, "hard",
        "convertible into 8,000 shares of common stock",
        "Boston Life Sciences, Inc."),
    "uwink_4p57to1": (
        "antidilution_type", "1108699_000101968704002883", 4.57, "hard",
        "an initial conversion ratio of 4.57",
        "uWink, Inc."),
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
    for oid, (src_leaf, read_from, value, diff, anchor, company) in ITEMS.items():
        p = HERE.parent / src_leaf / "corpus" / "full" / f"{read_from}.txt"
        if not p.exists():
            print(f"MISSING full text {read_from} -- skip"); continue
        full = p.read_text(errors="ignore")
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR not found in {read_from} ({anchor!r}) -- skip (fail-closed)"); continue
        (HERE / "corpus" / "questions" / f"{oid}.txt").write_text(win, encoding="utf-8")
        oracle.append({"id": oid, "company": company, "conversion_ratio": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={dict(Counter(o['conversion_ratio'] for o in oracle))}")


if __name__ == "__main__":
    main()
