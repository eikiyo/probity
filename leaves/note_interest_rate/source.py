"""
Location: leaves/note_interest_rate/source.py
Purpose: Build the note_interest_rate leaf corpus + SEPARATED oracle (2.2.2) from real SEC EDGAR
         documents. NUMBER extraction: each item's ground truth is the annual interest rate
         (as a percentage) stated on a convertible promissory note's principal.
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

# oracle_id -> (read_from_file_id, rate_value, difficulty, anchor, company)
# RATE_VALUE is the bare number (e.g., 0.28, 6.0, 12.0) representing the annual percentage
ITEMS = {
    "acology_0p28": (
        "000072174814000435_pncr050514s1ex104",
        0.28,
        "easy",
        "This Convertible Promissory Note shall bear interest at the rate of twenty-eight hundredths of one percent (0.28%) per annum",
        "ACOLOGY, INC."
    ),
    "helix_10p00": (
        "000091068003000216_exhb10_2",
        10.0,
        "easy",
        "The interest rate shall be ten percent (10%) per annum (the \"Interest Rate\")",
        "Helix Technology Corporation"
    ),
    "veritasfarms_10p00": (
        "000121390023048665_ea180241-8k_veritasfarms",
        10.0,
        "easy",
        "The Note will accrue interest on the aggregate amount loaned at a rate of 10% per annum",
        "VERITAS Farms Inc."
    ),
    "greenfieldrobotics_8p00": (
        "000147793216013565_gmgi_10k",
        8.0,
        "easy",
        "promissory note in the amount of $12,000. The promissory note is unsecured; bears interest at 8% per annum",
        "Golden Matrix Group, Inc."
    ),
    "lanzatech_8p00": (
        "exhibit41-formofconvertibl.htm",
        8.0,
        "easy",
        "interest shall accrue on the Principal Amount during such Interest Period at a rate equal to 8.00% per annum",
        "LanzaTech Global, Inc."
    ),
    "xtiaero_10p00": (
        "ea0262559-8k_xtiaero.htm",
        10.0,
        "medium",
        "Interest accrues on the outstanding principal amount at the lesser of 10% per annum",
        "XTI Aerospace Inc."
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
        oracle.append({"id": oid, "company": company, "note_interest_rate": value,
                       "anchor": anchor, "validating_quote": quote, "difficulty": diff})
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    print(f"wrote {len(oracle)} items  values={sorted(set(o['note_interest_rate'] for o in oracle))}")


if __name__ == "__main__":
    main()

# Excluded items (audit trail):
#   hepalife_18p00: Document mentions "Upon an Event of Default...interest shall accrue at a rate of 18% per annum"
#                   but contains NO base interest rate clause -- only the default/penalty rate is stated.
#                   Multi-value-ambiguity: cannot distinguish which rate applies to the base note (fail-closed).
#   minerco_notes:  These convertible notes from the Minerco 8-K do not explicitly state an interest rate
#                   in the converted promissory note text itself -- rates were not explicitly stated (valid 0% baseline).
#   (Independent audit, M3.1 -- the agent's own self-report missed all 4 of these:)
#   helix (was "helix_2p00"=2.0%): WRONG VALUE -- 2% is the DEFAULT/penalty add-on ("Interest Rate plus 2%
#                   per annum... Default Interest"); the actual base Interest Rate is 10%. Corrected id/value.
#   appleton_intellinetics_6p00: WRONG INSTRUMENT -- "note payable... to the Ohio State Development Authority"
#                   is a government development-authority loan mentioned in an 8-K background section, never
#                   described as convertible; excluded.
#   damonmotors_5p5: WRONG CONTEXT -- a promissory note issued to settle accounts-payable legal fees owed to
#                   Wilson Sonsini (a law firm), not a venture-financing convertible note; no conversion
#                   mechanic anywhere in the clause; excluded.
#   pppsba_1p00: WRONG INSTRUMENT -- a Paycheck Protection Program (SBA CARES Act) government relief loan
#                   buried in GRI Bio's audited financial-statement notes, not a convertible promissory
#                   note; excluded. Company field was also a placeholder ("SBA PPP Loan Program").
#   greenfieldrobotics_8p00 / exhibit_8p00: company fields were placeholders ("Greenfield Robotics / GMGI",
#                   "Convertible Note Form") -- corrected to the real filer/counterparty read from the
#                   document's own cover text (Golden Matrix Group, Inc.; LanzaTech Global, Inc.).
