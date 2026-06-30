"""Supplemental sourcing for thin classes (capped + participating). Incremental append."""
import urllib.request, urllib.parse, json, re, html, time
from pathlib import Path
UA = "Probity Research seyedmosayebalam@gmail.com"
HERE = Path(__file__).parent; RAW = HERE/'corpus'/'raw'; FULL = HERE/'corpus'/'full'
existing = [json.loads(l) for l in open(HERE/'candidates.jsonl') if l.strip()]
have = {int(c['id'].split('_')[0]) for c in existing}
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
