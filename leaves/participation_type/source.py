"""
Location: leaves/participation_type/source.py
Purpose: Source REAL preferred-stock liquidation clauses from SEC EDGAR full-text search.
         Fetches charter exhibits, extracts the liquidation PROVISION (keyword-scored window),
         writes candidates for MANUAL labeling. hint_class is a search bucket, never the oracle.
Functions: fts_search(), build_url(), fetch_clean(), extract_clause(), main()
Calls: urllib, EDGAR efts.sec.gov + www.sec.gov/Archives
Imports: urllib, json, re, html, time, pathlib

HOW THIS LEAF'S ORACLE ACTUALLY GETS BUILT (intern-level walkthrough, since this leaf's build
process spans 3 files unlike the newer single-source.py leaves): (1) this file's main() searches
EDGAR full-text search for 12 hand-picked exact phrases (PHRASES below) that are STRONG
indicators of one of the 3 classes, fetches each hit's real filing, extracts the richest
liquidation-provision window around it (extract_clause()), and writes everything to
candidates.jsonl -- NOT to oracle.jsonl. (2) source_more.py runs a second supplemental search
pass with 10 more phrases, appending more candidates for the thinner classes (participating/
capped were harder to find than non-participating). (3) oracle.jsonl itself is then built BY
HAND by a human reading each candidate's real corpus/full/<id>.txt and writing the final
participation_type label + a "note" explaining the reasoning -- this is intentional and
important: hint_class (the search phrase's bucket) is explicitly documented as "never the
oracle" because the search phrase that FOUND a candidate is not proof of what that candidate's
clause actually says once you read the whole thing (this is the project-wide "keyword-is-
candidate-not-oracle" discipline -- see root vault/mistakes.md).

ADVERSARIAL AUDIT FINDING (2026-07-02, RESOLVED -- Eikiyo confirmed the relabel, oracle.jsonl's
label for this item is now "participating" and the leaf has been rerun): the "Pfenex Inc." item
(id=1478121_000119312514227132, oracle.jsonl's own hardest/"TRAP" item) is labeled
"non-participating" with the stated reasoning "MPA implies capped, but MPA is the preference
amount and the structure is greater-of => non-participating." A full re-read of the item's
complete clause -- including subsections 2(a) and 2(b), which are REFERENCED by the visible
model-facing window but are NOT actually shown to the model (the window starts mid-way through
the clause, per extract_clause()'s 4200-char window landing past them) -- suggests the opposite
conclusion. The real structure: 2(a)+2(b) establish a FIXED liquidation preference of the
"Series A Original Issue Price" (confirmed elsewhere in the same document: $1.00/share) plus an
8% PER ANNUM SIMPLE (non-compounding) dividend. 2(c) then gives Preferred a pro-rata,
as-converted share of ALL remaining assets ALONGSIDE Common -- UNLESS the 2(a)+2(b) amount alone
exceeds a $2.50/share "Maximum Participation Amount" threshold, in which case a greater-of
override applies instead. Since $1.00 (the fixed preference) would need roughly 18.75 years of
accrued-but-unpaid 8% simple dividends to cross $2.50, the override is realistically almost never
triggered within a normal venture-exit timeline (typically 5-10 years) -- meaning in the
overwhelming majority of real outcomes, this instrument functions as ordinary UNCAPPED
PARTICIPATING preferred (fixed preference AND ALSO pro-rata sharing), not non-participating. See
the full char-by-char verification (window text before/after the extracted clause, the exact
$1.00 Original Issue Price definition, and the 8% simple-dividend clause) in the audit session
transcript / vault/mistakes.md. The oracle.jsonl "note" field for this item was appended with
this counter-finding, then Eikiyo explicitly confirmed the relabel on 2026-07-02 -- the
"participation_type" value was changed from "non-participating" to "participating" and the note
field updated to record both the original TRAP reasoning and the resolution. This item's leaf
was rerun after the flip so scored.json reflects the corrected ground truth.
"""

import urllib.request
import urllib.parse
import json
import re
import html
import time
from pathlib import Path

UA = "Probity Research seyedmosayebalam@gmail.com"
HERE = Path(__file__).parent
RAW = HERE / "corpus" / "raw"
FULL = HERE / "corpus" / "full"
MAX_PER_CIK = 1  # diversity: one clause per company

# Single clean quoted phrase per query (EDGAR FTS 500s on parens / multi-quote / boolean).
PHRASES = [
    ('"would have received if all shares of Preferred Stock had been converted into Common Stock"', "non-participating"),
    ('"as if all shares of Series A Preferred Stock had been converted into Common Stock"', "non-participating"),
    ('"the greater of the applicable Original Issue Price"', "non-participating"),
    ('"whichever would result in the larger aggregate amount"', "non-participating"),
    ('"remaining assets of the Corporation available for distribution shall be distributed"', "participating"),
    ('"Preferred Stock and Common Stock on a pro rata as-converted basis"', "participating"),
    ('"shall be distributed ratably among the holders of Preferred Stock and Common Stock"', "participating"),
    ('"on an as-converted to Common Stock basis together with the holders of Common Stock"', "participating"),
    ('"times the Original Issue Price per share"', "capped"),
    ('"shall not exceed three times the Original Issue Price"', "capped"),
    ('"the Maximum Participation Amount"', "capped"),
    ('"until such holders shall have received an aggregate amount per share"', "capped"),
]

# Determinative liquidation-provision keywords (used to score which window to extract).
DETERMINERS = [
    "preference", "original issue price", "converted into common", "as-converted",
    "participate", "remaining assets", "greater of", "pari passu", "times the original",
    "ratably", "pro rata", "distributed",
]


def fts_search(phrase: str, forms: str = "8-K,S-1,10-12G,DRS,1-A,10-K,424B4", limit: int = 12) -> list:
    """Query EDGAR full-text search; return hits (newest first)."""
    q = urllib.parse.quote(phrase)
    url = f"https://efts.sec.gov/LATEST/search-index?q={q}&forms={forms}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data.get("hits", {}).get("hits", [])[:limit]


def build_url(hit: dict) -> str:
    """Construct the Archives document URL from a FTS hit."""
    src = hit["_source"]
    cik = str(int(src["ciks"][0]))
    adsh_nodash = src["adsh"].replace("-", "")
    filename = hit["_id"].split(":", 1)[1]
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh_nodash}/{filename}"


def fetch_clean(url: str) -> str:
    """Fetch an EDGAR doc and strip it to plain text."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", "ignore")
    txt = re.sub(r"<[^>]+>", " ", raw)
    return html.unescape(re.sub(r"\s+", " ", txt)).strip()


def extract_clause(text: str, window: int = 4200) -> str:
    """Return the liquidation window richest in determinative terms (not just the first match)."""
    low = text.lower()
    positions = [m.start() for m in re.finditer(r"liquidat", low)]
    if not positions:
        return ""
    best, best_score = "", -1
    for p in positions:
        start = max(0, p - 300)
        chunk = text[start:start + window]
        cl = chunk.lower()
        score = sum(k in cl for k in DETERMINERS)
        if score > best_score:
            best_score, best = score, chunk
    return best


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    FULL.mkdir(parents=True, exist_ok=True)
    seen, per_cik, candidates = set(), {}, []
    for phrase, hint in PHRASES:
        try:
            hits = fts_search(phrase)
        except Exception as e:
            print(f"  search FAILED [{phrase[:38]}]: {e}")
            continue
        for h in hits:
            src = h["_source"]
            cik = int(src["ciks"][0])
            key = (src["adsh"], h["_id"].split(":", 1)[1])
            if key in seen or per_cik.get(cik, 0) >= MAX_PER_CIK:
                continue
            seen.add(key)
            url = build_url(h)
            try:
                full = fetch_clean(url)
            except Exception as e:
                print(f"  fetch FAILED {url}: {e}")
                continue
            time.sleep(0.3)
            clause = extract_clause(full)
            cl = clause.lower()
            # require a real liquidation provision that actually discusses the common-sharing decision
            if len(clause) < 600 or "participat" not in cl and "converted into common" not in cl and "as-converted" not in cl:
                continue
            per_cik[cik] = per_cik.get(cik, 0) + 1
            cid = f"{cik}_{src['adsh'].replace('-', '')}"
            (RAW / f"{cid}.txt").write_text(clause, encoding="utf-8")
            (FULL / f"{cid}.txt").write_text(full, encoding="utf-8")
            candidates.append({
                "id": cid, "company": src["display_names"][0], "file_type": src.get("file_type"),
                "file_date": src.get("file_date"), "url": url, "hint_class": hint,
                "clause_chars": len(clause),
            })
            print(f"  + {cid}  [{hint}]  {src['display_names'][0][:45]}")
    (HERE / "candidates.jsonl").write_text(
        "\n".join(json.dumps(c) for c in candidates) + "\n", encoding="utf-8")
    print(f"\nWROTE {len(candidates)} candidates -> candidates.jsonl (for MANUAL labeling)")


if __name__ == "__main__":
    main()
