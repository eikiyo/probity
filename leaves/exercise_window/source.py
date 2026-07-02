"""
Location: leaves/exercise_window/source.py
Purpose: Build the exercise_window leaf corpus + oracle (ref 6.5, op EX=extract) from real SEC
         option-grant-agreement exhibits. Each item's target scenario + exercise window verified
         as literal substrings of the real fetched document -- five distinct real companies,
         five distinct real termination scenarios, five different real window durations.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# id -> (company, target_scenario_desc, exercise_window, anchor substring, source url)
ITEMS = {
    "sirva": ("SIRVA, Inc.", "termination for any reason other than Retirement, death, or Disability", "30 days",
        "thirty (30) days following the date of such Termination of Service",
        "https://www.sec.gov/Archives/edgar/data/1181232/000119312514230547/d693356dex1047.htm"),
    "covisint": ("Covisint Corp.", "termination without Cause", "85 days",
        "85 days following the date of such termination",
        "https://www.sec.gov/Archives/edgar/data/1563699/000119312513245466/d498010dex44.htm"),
    "annaslinens": ("Annas Linens, Inc.", "Retirement", "90 days",
        "ninety (90) days following the date of such termination",
        "https://www.sec.gov/Archives/edgar/data/821897/000119312505128763/dex1007.htm"),
    "williamsscotsman": ("Williams Scotsman International, Inc.", "termination for any reason other than the causes described earlier in the agreement", "90 days",
        "90 days following the date of such termination",
        "https://www.sec.gov/Archives/edgar/data/923144/000104746905022028/a2162361zex-10_34.htm"),
    "douglasdynamics1": ("Douglas Dynamics, Inc.", "Retirement, death, or Disability", "180 days",
        "one hundred eighty (180) days following the date of",
        "https://www.sec.gov/Archives/edgar/data/1287213/000104746910003916/a2197975zex-10_18.htm"),
}


def build_window(raw_text, anchor, scenario):
    idx = raw_text.find(anchor)
    if idx == -1:
        return None
    start = max(0, idx - 350)
    end = min(len(raw_text), idx + len(anchor) + 100)
    excerpt = raw_text[start:end].strip()
    return f"TARGET SCENARIO: {scenario}\n\n{excerpt}"


def main():
    oracle_lines = []
    for id_, (company, scenario, window_val, anchor, url) in ITEMS.items():
        raw = (FULL / f"{id_}.txt").read_text()
        if anchor not in raw:
            print(f"SKIP {id_}: anchor not found verbatim -- {anchor!r}")
            continue
        window = build_window(raw, anchor, scenario)
        if window is None:
            print(f"SKIP {id_}: could not build window")
            continue
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "exercise_window": window_val,
            "validating_quote": anchor,
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company} ({scenario}): {window_val}")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
