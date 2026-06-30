"""
Location: engine/edgar.py
Purpose: Shared SEC EDGAR sourcing helpers (full-text search + fetch + section extraction),
         reused by every leaf's source script. Real public documents only; the model's answer
         is always validated by a human against the clause's own text, never by this module.
Functions: fts_search(), build_url(), fetch_clean(), best_window()
Imports: urllib, json, re, html, time
"""

import urllib.request
import urllib.parse
import json
import re
import html
import time

UA = "Probity Research seyedmosayebalam@gmail.com"
FORMS = "8-K,S-1,10-12G,DRS,1-A,424B4,10-K"


def fts_search(phrase, forms=FORMS, limit=12, retries=3):
    """EDGAR full-text search for ONE quoted phrase (FTS 500s on parens/multi-quote)."""
    url = f"https://efts.sec.gov/LATEST/search-index?q={urllib.parse.quote(phrase)}&forms={forms}"
    for a in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
                return json.loads(r.read().decode())["hits"]["hits"][:limit]
        except Exception as e:
            if a == retries - 1:
                print(f"  search FAIL [{phrase[:30]}]: {e}", flush=True)
                return []
            time.sleep(1.5)


def build_url(hit):
    """Construct the Archives document URL from a FTS hit (filer CIK + accession + filename)."""
    src = hit["_source"]
    cik = str(int(src["ciks"][0]))
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{src['adsh'].replace('-', '')}/{hit['_id'].split(':', 1)[1]}"


def fetch_clean(url):
    """Fetch an EDGAR doc and strip it to plain text."""
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
        raw = r.read().decode("utf-8", "ignore")
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw))).strip()


def best_window(text, section_terms, determiners, window=4200, pad=300):
    """Return the window (around any section_term) richest in determinative keywords, or ''."""
    low = text.lower()
    positions = []
    for term in section_terms:
        positions += [m.start() for m in re.finditer(re.escape(term), low)]
    if not positions:
        return ""
    best, best_score = "", -1
    for p in sorted(set(positions)):
        chunk = text[max(0, p - pad):p - pad + window]
        score = sum(k in chunk.lower() for k in determiners)
        if score > best_score:
            best_score, best = score, chunk
    return best
