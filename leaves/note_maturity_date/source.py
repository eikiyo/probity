"""
Location: leaves/note_maturity_date/source.py
Purpose: Build the note_maturity_date leaf corpus + SEPARATED oracle (2.2.3) from real SEC EDGAR
         documents. DATE extraction: maturity date (date note is due if not converted/extended).
Functions: main()
Calls: engine.corpus_utils.window_on
Imports: json, pathlib, sys
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from corpus_utils import window_on  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# oracle_id -> (read_from_file_id, maturity_date_value ISO YYYY-MM-DD, difficulty, anchor, company)
ITEMS = {
    "gardenburger_2005_03_31": (
        "000089291702000003_gbamnote",
        "2005-03-31",
        "easy",
        "principal amount of Seventeen Million Three Hundred Sixty Four Thousand Three Hundred Seventy Five dollars ($17,364,375) on March 31, 2005 (the \"MATURITY DATE\")",
        "GARDENBURGER, INC."
    ),
    "acology_2015_03_04": (
        "000072174814000435_pncr050514s1ex104",
        "2015-03-04",
        "medium",
        "on the Maturity Date (as that term is hereinafter defined) at 11415 NW 123rd Lane, Reddick, FL 32686, in accordance with the terms herein set forth, the principal amount",
        "ACOLOGY, INC."
    ),
    "xtiaero_2026_12_31": (
        "ea0262559-8k_xtiaero.htm",
        "2026-12-31",
        "easy",
        "is due and payable on December 31, 2026",
        "XTI Aerospace Inc."
    ),
    "veritasfarms_2026_10_01": (
        "000121390023048665_ea180241ex10-2_veritasfarms",
        "2026-10-01",
        "medium",
        "shall be due and payable by Maker to Holder, if not converted pursuant to the terms and conditions of this Promissory Note, on the earlier of (i) October 1, 2026",
        "VERITAS Farms Inc."
    ),
}
#   v209348_2011_01_03 (dropped): the document (000114420411004581_v209348_ex10-1.txt) is a
#     multi-note SETTLEMENT AGREEMENT (United Energy Corp., Wilen, Hilltop) restructuring several
#     DIFFERENT promissory notes with different dates (Mar 13 2009, May 13 2009 notes) -- "January 3,
#     2011" is the unrelated "Initial Closing" date of the settlement, not any note's maturity date.
#     No single unambiguous maturity date exists in this document; dropped.
#   artec_2015_01_07 (dropped): the anchor text ("dated January 7, 2015") is the note's ISSUANCE
#     date, not its maturity date -- conflated the two, same bug class as the original
#     veritasfarms error. The actual document is a credit-agreement default/waiver letter
#     (Borrower/Lender revolving-loan terminology) that only references the Artec note in
#     passing background recitals; no clean single maturity date for the Artec note is stated
#     in this document at all. Dropped.
#   sunworks_2013_07_31 (dropped): the read_from file id (000095012314005097_filename26) does not
#     contain "sunworks" anywhere -- it is actually a CAPNIA, INC. exhibit (confirmed by its own
#     header: "CAPNIA, INC."). The company label and anchor text were mismatched to the wrong
#     document entirely; no SUNWORKS document exists in this leaf's corpus. Dropped.
# Excluded (audit trail):
#   sedona_relative: ground-truth value was literally "unspecified in excerpt" -- an unresolvable
#     relative date with no anchor date in the same document; never a valid oracle value, excluded.
#   lanzatech_relative_60mo (was "lanzatech_2029_relative"): anchor's own validating_quote showed a
#     BLANK TEMPLATE bracket ("[__], 2029") -- not a real filled-in date; excluded.
#   minerco_rios_2016_11_01: the shown window states BOTH the superseded "Original Note" due date
#     (Nov 1, 2016) AND the current "New Note" due date (July 5, 2017) in the same excerpt, and the
#     ground truth was set to the WRONG (superseded) one -- classic multi-value-ambiguity, excluded.
#   helix_2005_02_14: company was fabricated as "Helix Technology Corporation" -- the word "Helix"
#     does not appear anywhere in the actual document (000091068003000216_exhb10_2.txt), which is a
#     10% convertible note of SmartServ Online, Inc. Also affects the note_interest_rate leaf's
#     "helix_10p00" item, which reused the same file with the same wrong company name -- fix tracked
#     separately (the extracted 10% rate itself is still correctly grounded, only the company label
#     was wrong).
#   spore_2015_05_31: BOTH the company name ("SPORE ENERGY, LTD." -- does not appear in the document,
#     which is a HepaLife Technologies note) AND the anchor text ("May 31, 2015") were fabricated --
#     the anchor string does not occur anywhere in the source document at all. Independent audit,
#     M3.1 -- source.py had drifted from the actually-shipped oracle.jsonl/corpus/questions on disk
#     (a real "spec vs code drift" bug: someone edited source.py after generating the oracle without
#     re-running it) -- this rewrite reconciles source.py to be the authoritative, re-runnable script
#     again, matching the corrected, audited oracle.


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
        oracle.append({"id": oid, "company": company, "note_maturity_date": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
