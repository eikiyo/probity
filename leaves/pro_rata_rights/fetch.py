"""
Location: leaves/pro_rata_rights/fetch.py
Purpose: Pull candidate docs for the pro_rata_rights leaf. PRESENT pool = FTS "Pro Rata Right" exhibits;
         ABSENT pool = restricted-stock/plain agreements without pro-rata participation rights.
         Saves cleaned full text + candidates_*.jsonl (company/url/prorata_count) for manual oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

PRESENT = ['"Pro Rata Right"', '"Right to Future Stock Issuances"', '"preemptive right to participate"', '"Pro Rata Rights Agreement"']
ABSENT  = ['"waiver of preemptive rights"', '"no preemptive rights"', '"Stock Restriction Agreement"']

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def prorata_count(text):
    """Count co-occurrences of pro rata + preemptive (case-insensitive)."""
    low = text.lower()
    return low.count("pro rata") + low.count("preemptive")

def pull():
    seen = set(); pres = []; absn = []
    for ph in PRESENT:
        try: hits = fts_search(ph, limit=10)
        except Exception as e: print(f"  ERR {ph}: {e}"); continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen: continue
            seen.add(cid)
            try: txt = fetch_clean(build_url(h))
            except Exception as e: print(f"  fetch ERR {cid}: {e}"); continue
            if not txt or len(txt) < 400: continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            pres.append({"id": cid, "company": company_of(h), "url": build_url(h),
                         "prorata_count": prorata_count(txt)})
    for ph in ABSENT:
        try: hits = fts_search(ph, limit=12)
        except Exception as e: print(f"  ERR {ph}: {e}"); continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen: continue
            seen.add(cid)
            try: txt = fetch_clean(build_url(h))
            except Exception as e: print(f"  fetch ERR {cid}: {e}"); continue
            if not txt or len(txt) < 400: continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            absn.append({"id": cid, "company": company_of(h), "url": build_url(h),
                         "prorata_count": prorata_count(txt)})
    with open(HERE / "candidates_present.jsonl", "w") as f:
        for d in pres: f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_absent.jsonl", "w") as f:
        for d in absn: f.write(json.dumps(d) + "\n")
    print(f"PRESENT pool: {len(pres)} docs (prorata_count>0 expected)")
    for d in pres: print(f"   {d['prorata_count']:3}  {d['id']:40} {d['company']}")
    print(f"ABSENT candidates: {len(absn)} docs (want prorata_count==0 for clean 'no')")
    for d in absn: print(f"   {d['prorata_count']:3}  {d['id']:40} {d['company']}")

if __name__ == "__main__":
    pull()
