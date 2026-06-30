"""
Location: leaves/protective_provisions/fetch.py
Purpose: Pull candidate docs for the protective_provisions leaf. PRESENT pool = FTS docs with
         investor veto rights (protective provisions in charters/CODs); ABSENT pool = docs with
         no preferred stock protective provisions. Saves cleaned full text + candidates_*.jsonl
         (id/company/url/pp_count) for the MANUAL oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# PRESENT: docs that should contain protective provisions language
PRESENT = ['"Protective Provisions"', '"so long as any shares of Series"', 
           '"vote or written consent of the holders of"', '"affirmative vote of the holders of at least"']

# ABSENT: docs unlikely to have preferred investor veto rights
ABSENT = ['"Common Stock Purchase Agreement"', '"no separate class vote"']

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
                         "pp_count": txt.lower().count("protective provision") + txt.lower().count("affirmative vote")})
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
                         "pp_count": txt.lower().count("protective provision") + txt.lower().count("affirmative vote")})
    with open(HERE / "candidates_present.jsonl", "w") as f:
        for d in pres: f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_absent.jsonl", "w") as f:
        for d in absn: f.write(json.dumps(d) + "\n")
    print(f"PRESENT pool: {len(pres)} docs (pp_count>0 expected)")
    for d in pres: 
        excerpt = open(FULL / f"{d['id']}.txt").read()[:150].replace("\n", " ")
        print(f"   {d['id']:40} | {d['company']:30} | pp_count={d['pp_count']:2} | {excerpt}")
    print(f"ABSENT candidates: {len(absn)} docs (want pp_count==0 for clean 'no')")
    for d in absn: 
        excerpt = open(FULL / f"{d['id']}.txt").read()[:150].replace("\n", " ")
        print(f"   {d['id']:40} | {d['company']:30} | pp_count={d['pp_count']:2} | {excerpt}")

if __name__ == "__main__":
    pull()
