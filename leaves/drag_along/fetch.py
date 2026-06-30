"""
Location: leaves/drag_along/fetch.py
Purpose: Pull candidate docs for the drag_along leaf (5.6). PRESENT pool = FTS "Drag-Along" exhibits;
         ABSENT pool = transfer-governing agreements (ROFR/Co-Sale/Voting) that we then verify contain
         ZERO "drag" occurrences (deterministic absence, not a guessed negative). Saves cleaned full
         text + candidates_*.jsonl (company/url/drag_count) for the MANUAL oracle pass in source.py.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

PRESENT = ['"Drag-Along Right"', '"Drag Along Right"', '"Drag-Along Obligation"', '"Drag-Along Sale"']
ABSENT  = ['"Right of First Refusal and Co-Sale Agreement"', '"Right of First Refusal and Co-Sale"',
           '"Co-Sale Agreement"']

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
                         "drag_count": txt.lower().count("drag")})
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
                         "drag_count": txt.lower().count("drag")})
    with open(HERE / "candidates_present.jsonl", "w") as f:
        for d in pres: f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_absent.jsonl", "w") as f:
        for d in absn: f.write(json.dumps(d) + "\n")
    print(f"PRESENT pool: {len(pres)} docs (drag_count>0 expected)")
    for d in pres: print(f"   {d['drag_count']:3}  {d['id']:40} {d['company']}")
    print(f"ABSENT candidates: {len(absn)} docs (want drag_count==0 for clean 'no')")
    for d in absn: print(f"   {d['drag_count']:3}  {d['id']:40} {d['company']}")

if __name__ == "__main__":
    pull()
