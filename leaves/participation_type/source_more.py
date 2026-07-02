"""
Location: leaves/participation_type/source_more.py
Purpose: Supplemental EDGAR sourcing pass for this leaf's two thinner classes (participating,
         capped). source.py's first pass over-indexed on non-participating clauses (it's the
         most common real-world structure, so it's also the easiest to find via full-text
         search) -- this script runs 10 MORE hand-picked search phrases targeted specifically at
         participating/capped language, and APPENDS results to candidates.jsonl (skips any CIK
         already present via the `have` set below, so re-running this is safe/idempotent and
         won't duplicate a company already sourced by source.py's first pass).
Functions: fts() [EDGAR full-text search], build_url(), fetch(), extract() [see below for full run
Calls: urllib, EDGAR efts.sec.gov + www.sec.gov/Archives -- same pattern as source.py
Imports: urllib.request, urllib.parse, json, re, html, time, pathlib

WHY this is a SEPARATE file rather than just adding more phrases to source.py's PHRASES list:
this was written as an incremental, second sourcing pass AFTER source.py's first pass had
already run and candidates.jsonl already existed with real data in it -- re-running source.py
itself would have re-fetched everything from scratch (wasteful, and risks re-hitting EDGAR's
rate limits for no reason). Keeping the supplemental pass separate means it can be re-run on its
own, cheaply, without re-doing the first pass's work.

NOTE (found during 2026-07-02 adversarial audit): unlike every other file in this leaf/repo, the
module-level constants below (UA, HERE, RAW, FULL, existing, have, DET) are executed as TOP-LEVEL
statements outside any function -- meaning simply `import`-ing this module (rather than running it
as a script) immediately tries to open candidates.jsonl and parse it. This works fine as a
one-off manual script (`python3 source_more.py`) but would break if anything ever tried to import
this module for its function definitions alone (e.g. a future test file) without candidates.jsonl
present. Left as-is since this script has always been run standalone and is not currently
imported anywhere else in the codebase -- flagged here so a future maintainer doesn't hit this
surprise if they try to `import source_more` from elsewhere.
"""
import urllib.request, urllib.parse, json, re, html, time
from pathlib import Path
UA = "Probity Research seyedmosayebalam@gmail.com"
HERE = Path(__file__).parent; RAW = HERE/'corpus'/'raw'; FULL = HERE/'corpus'/'full'
existing = [json.loads(l) for l in open(HERE/'candidates.jsonl') if l.strip()]
have = {int(c['id'].split('_')[0]) for c in existing}
# DET = the same "determinative liquidation-provision keywords" idea as source.py's DETERMINERS
# (used to score which extracted window is richest in real participation-mechanism language) --
# this is a genuine near-duplicate of source.py's DETERMINERS list (12 vs 15 overlapping terms).
# Left un-deduplicated for now (each file's list was tuned independently for its own phrase set)
# but flagged here as a §0.8 "rule of two" candidate for extraction into a shared engine helper
# if a THIRD leaf ever needs the same kind of keyword-scored window extraction.
DET = ["preference","original issue price","converted into common","as-converted","participate",
       "remaining assets","greater of","pari passu","times the original","ratably","pro rata",
       "distributed","not exceed","maximum participation","aggregate"]
PHRASES = [
 ('"two times the Original Issue Price"','capped'),
 ('"three times the Original Issue Price"','capped'),
 ('"the Participation Cap"','capped'),
 ('"shall cease to participate"','capped'),
 ('"distributed ratably among the holders of Common Stock and Preferred Stock"','participating'),
 ('"the holders of Preferred Stock and Common Stock pro rata on an as-converted basis"','participating'),
 ('"shall participate in such distribution with the holders of Common Stock"','participating'),
 ('"on an as-if-converted to Common Stock basis"','participating'),
 ('"and the holders of Common Stock pro rata based on the number of shares of Common Stock"','participating'),
 ('"in an amount equal to two times the Original Issue Price"','capped'),
]
def fts(p, limit=14):
    url = f"https://efts.sec.gov/LATEST/search-index?q={urllib.parse.quote(p)}&forms=8-K,S-1,10-12G,DRS,1-A,424B4,10-K"
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
                return json.loads(r.read().decode())['hits']['hits'][:limit]
        except Exception as e:
            if a == 2: print(f"  search FAIL [{p[:28]}]: {e}", flush=True); return []
            time.sleep(1.5)
def clean(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
        raw = r.read().decode('utf-8', 'ignore')
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', raw))).strip()
def extract(t, window=4200):
    low = t.lower(); pos = [m.start() for m in re.finditer('liquidat', low)]
    if not pos: return ''
    best, bs = '', -1
    for p in pos:
        c = t[max(0, p-300):p-300+window]; s = sum(k in c.lower() for k in DET)
        if s > bs: bs, best = s, c
    return best
added = 0
for phrase, hint in PHRASES:
    for h in fts(phrase):
        src = h['_source']; cik = int(src['ciks'][0])
        if cik in have: continue
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{src['adsh'].replace('-','')}/{h['_id'].split(':',1)[1]}"
        try: full = clean(url)
        except Exception as e: print(f"  fetch FAIL {cik}: {e}", flush=True); continue
        time.sleep(0.3); cl = extract(full); low = cl.lower()
        if len(cl) < 600 or ('participat' not in low and 'converted into common' not in low and 'as-converted' not in low):
            continue
        have.add(cik); cid = f"{cik}_{src['adsh'].replace('-','')}"
        (RAW/f"{cid}.txt").write_text(cl); (FULL/f"{cid}.txt").write_text(full)
        rec = {"id": cid, "company": src['display_names'][0], "file_type": src.get('file_type'),
               "file_date": src.get('file_date'), "url": url, "hint_class": hint, "clause_chars": len(cl)}
        with open(HERE/'candidates.jsonl', 'a') as f:
            f.write(json.dumps(rec)+'\n')
        added += 1; print(f"  + {cid} [{hint}] {src['display_names'][0][:40]}", flush=True)
print(f"\nADDED {added} new candidates", flush=True)
