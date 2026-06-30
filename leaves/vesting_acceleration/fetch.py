"""
Location: leaves/vesting_acceleration/fetch.py
Purpose: Pull candidate docs for the vesting_acceleration leaf (founder equity acceleration on trigger).
         PRESENT pool = FTS "acceleration" vesting agreements (grants acceleration upon specified event);
         ABSENT pool = vesting agreements with no acceleration language or explicit no-acceleration clauses.
         Saves cleaned full text + candidates_*.jsonl (company/url/accel_count) for manual oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

PRESENT = ['"Acceleration of Vesting"', '"shall accelerate"', '"acceleration of the vesting"',
           '"accelerated vesting"', '"single trigger acceleration"', '"double trigger acceleration"']
ABSENT  = ['"shall not be accelerated"', '"no acceleration"', '"no accelerated vesting"',
           '"vest in equal annual installments"', '"vest in equal monthly installments"']

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

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
                         "accel_count": txt.lower().count("accelerat")})
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
                         "accel_count": txt.lower().count("accelerat")})
    with open(HERE / "candidates_present.jsonl", "w") as f:
        for d in pres: f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_absent.jsonl", "w") as f:
        for d in absn: f.write(json.dumps(d) + "\n")
    print(f"PRESENT pool: {len(pres)} docs (accel_count>0 expected)")
    for d in pres: print(f"   {d['accel_count']:3}  {d['id']:40} {d['company']}")
    print(f"ABSENT candidates: {len(absn)} docs (want clean 'no acceleration')")
    for d in absn: print(f"   {d['accel_count']:3}  {d['id']:40} {d['company']}")

if __name__ == "__main__":
    pull()
