"""
Location: leaves/participation_type/source.py
Purpose: Source REAL preferred-stock liquidation clauses from SEC EDGAR full-text search.
         Fetches charter exhibits, extracts the liquidation PROVISION (keyword-scored window),
         writes candidates for MANUAL labeling. hint_class is a search bucket, never the oracle.
Functions: fts_search(), build_url(), fetch_clean(), extract_clause(), main()
Calls: urllib, EDGAR efts.sec.gov + www.sec.gov/Archives
Imports: urllib, json, re, html, time, pathlib
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
