"""
Location: leaves/liquidation_waterfall_payout/source.py
Purpose: Build the liquidation_waterfall_payout leaf corpus + oracle (ref 4.1, op CO=compute)
         from a real SC 13E-3 going-private fairness opinion (Connecture, Inc., filed 2018).
         The opinion's own DCF/comps table discloses 4 independent methodology columns, each
         with a real, self-consistent bridge from Enterprise Value to per-share common equity
         value through a real Series A + Series B preferred liquidation stack ($78.6M combined,
         itself verified as $52.0M Series A pref + $6.9M accrued Series A dividends + $17.5M
         Series B pref + $2.2M accrued Series B dividends = $78.6M). Every item's arithmetic
         independently re-verified: (EV - severance - debt - preferred) / shares == the
         document's own disclosed per-share figure, before being trusted.
Functions: main()
Imports: json, pathlib
Calls: none (standalone build script, run once by hand: `python3 source.py`) -- writes
       corpus/questions/<id>.txt (model-facing windows) and oracle.jsonl (ground truth), which
       engine/runner.py's load_instances() reads at every subsequent benchmark run.

WHY this file is separate from task.py: task.py defines HOW to prompt a model given an already-
built instance; source.py defines WHERE the instance's numbers come from and WHY they're trusted.
Splitting them means task.py never needs to change once the corpus exists, and source.py never
needs to know anything about prompting -- re-running `python3 source.py` regenerates the corpus/
oracle from ITEMS below without touching the benchmark logic at all.

DATA PROVENANCE NOTE (important for anyone auditing this leaf): the source PDF/HTML exhibit
(corpus/full/connecture_c3.txt, SEC EDGAR accession 0001193125-18-039721) never contains the
word "Connecture" anywhere in its 64,814 characters -- the banker's fairness-opinion deck refers
to the target company only by the internal M&A deal codename "Cure" (33 occurrences). This is
NORMAL practice for confidential banker presentation decks and is NOT a data error: the real
filer behind this exhibit is independently confirmed via SEC EDGAR CIK 1211759 -> "CONNECTURE
INC" (Brookfield, WI; SIC 7372 prepackaged software). Anyone re-auditing this leaf by opening
corpus/full/connecture_c3.txt directly and searching for "Connecture" will find zero hits --
that is expected, not a sign the company attribution is wrong. Verify via the CIK instead:
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1211759

KNOWN GAP (found on audit, not yet fixed): the `validating_quote` field below is hand-written
with a "..." ellipsis rather than extracted as a literal substring via engine/corpus_utils.
window_on() (the convention every other leaf in this repo follows, which guarantees the quote
is a real, grep-able substring of the source text). The real text at that location reads
"Implied Per Share Reference Range [6] ($1.04) -- $0.51" (an em-dash, a footnote marker, and the
LOW end of the range sit between "Range" and the stated high-end figure) -- so this leaf's
validating_quote is a paraphrase, not a literal substring. It is not currently machine-checked
anywhere (grep confirms no engine/*.py file asserts validating_quote is a real substring), but
results/render.py's public README table advertises "the validating quote... per item" as part of
this benchmark's rigor claim, so a broken quote here undermines that claim for any external
reader who tries to spot-check it against corpus/full/connecture_c3.txt directly.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"

# The 4 numeric facts that are IDENTICAL across all 4 methodology columns in the real document
# (severance/debt/preferred-stack/shares-outstanding don't vary by valuation methodology -- only
# Enterprise Value does, since EV is the thing each methodology is estimating). Repeating this
# verbatim across all 4 corpus/questions/*.txt windows is intentional and matches the real
# document's own structure (verified against corpus/full/connecture_c3.txt), not a copy-paste
# shortcut -- see WHY note above for why this makes the leaf a purer arithmetic-only test.
SHARED_FACTS = (
    "Severance Run-Off Payment: $(0.3) million. "
    "Projected Total Debt as of 12/31/17: $(32.6) million. "
    "Projected Preferred Stock as of 12/31/17: $(78.6) million "
    "(Series A Preferred Stock liquidation preference of $52.0 million plus projected accrued "
    "dividends as of 12/31/17 of $6.9 million, and Series B Preferred Stock liquidation "
    "preference of $17.5 million plus projected accrued dividends as of 12/31/17 of $2.2 "
    "million). Projected Shares Outstanding as of 12/31/17: 25.2 million."
)

# id -> (methodology label, enterprise_value_high_end, severance, debt, preferred, shares, stated_per_share)
# Every number here was manually cross-checked against the real disclosed table in
# corpus/full/connecture_c3.txt (search for "Implied Total Enterprise Value Reference Range" and
# "Implied Per Share Reference Range [6]") -- these are the HIGH end of each methodology's
# disclosed range, matching the "(high end of reference range)" label written into each window.
ITEMS = {
    "col1_selected_companies_ltm": ("Selected Companies Analysis (LTM Ended 9/30/17 GAAP Revenue)", 124.3, 0.3, 32.6, 78.6, 25.2, 0.51),
    "col2_selected_companies_fy17e": ("Selected Companies Analysis (FY2017E GAAP Revenue)", 122.0, 0.3, 32.6, 78.6, 25.2, 0.42),
    "col3_selected_companies_fy18e": ("Selected Companies Analysis (FY2018E GAAP Revenue)", 121.2, 0.3, 32.6, 78.6, 25.2, 0.39),
    "col4_discounted_cash_flow": ("Discounted Cash Flow Analysis", 122.6, 0.3, 32.6, 78.6, 25.2, 0.44),
}


def main():
    """
    What: for each of the 4 real methodology columns, (1) independently recompute the per-share
          answer from the raw EV/severance/debt/preferred/shares inputs, (2) verify that
          recomputed value matches the document's own disclosed per-share figure within a small
          tolerance, (3) if it matches, write the model-facing prompt window to
          corpus/questions/<id>.txt and append a ground-truth row to oracle.jsonl; if it does
          NOT match, skip the item and print a MISMATCH warning instead of shipping bad data.
    Why: this is the leaf's single fail-closed data-integrity gate (project-wide law, see root
         CLAUDE.md §0.7 "fail closed, never silent") -- an item whose disclosed answer doesn't
         follow from its own disclosed inputs is either a mis-transcription (a bug in ITEMS
         above) or a genuine document inconsistency, and either way it must NOT be shipped as a
         trustworthy benchmark item. A 0.02 tolerance is used deliberately: real fairness-opinion
         tables round each displayed figure (EV, equity value, per-share) independently from a
         higher-precision internal model, so recomputing per-share from the DISPLAYED (already-
         rounded) EV can legitimately land ~$0.01 off the document's own displayed per-share --
         that is expected rounding drift, not a data error (verified case: col3 recomputes to
         $0.3849, which the document itself displays as $0.39).
    Output: side effect only -- writes N .txt files under corpus/questions/ and one oracle.jsonl
            (overwriting any prior version). Also prints one OK/MISMATCH line per item plus a
            final count, so a human running this by hand can see at a glance whether every item
            in ITEMS survived the integrity check.
    Success criteria: oracle.jsonl's line count should equal len(ITEMS) (4) -- if it's fewer, the
            printed MISMATCH lines say which item(s) failed the recompute check and why, so the
            fix is either correcting ITEMS' inputs or investigating the source document further,
            never silently dropping the item and moving on.
    """
    oracle_lines = []
    for id_, (label, ev, severance, debt, pref, shares, stated) in ITEMS.items():
        computed = round((ev - severance - debt - pref) / shares, 2)
        if abs(computed - stated) > 0.02:
            print(f"MISMATCH {id_}: computed {computed} vs disclosed {stated}")
            continue
        window = (
            f"Methodology: {label} (high end of reference range).\n\n"
            f"Implied Total Enterprise Value: ${ev} million.\n\n{SHARED_FACTS}"
        )
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "liquidation_waterfall_payout": stated,
            # See "KNOWN GAP" module docstring note above: this quote is a hand-written
            # paraphrase (uses "..." where the real text has a footnote marker + the range's
            # low end), not a literal substring of corpus/full/connecture_c3.txt.
            "validating_quote": f"Implied Per Share Reference Range ... ${stated}",
            "source_url": "https://www.sec.gov/Archives/edgar/data/1211759/000119312518039721/d516937dex99c3.htm",
            # See "DATA PROVENANCE NOTE" above: the source document itself never says
            # "Connecture" (it uses the deal codename "Cure") -- this name is independently
            # confirmed via SEC EDGAR CIK 1211759, not extracted from corpus/full/connecture_c3.txt.
            "company": "Connecture, Inc.",
        })
        print(f"OK {id_}: EV={ev} -> per_share={stated} (computed {computed})")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
