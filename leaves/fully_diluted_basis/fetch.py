"""
Location: leaves/fully_diluted_basis/fetch.py
Purpose: Pull candidate docs for the fully_diluted_basis leaf (cap table basis definition).
         FULLY-DILUTED = cap definition includes all convertible securities + unissued pool.
         ISSUED-OUTSTANDING = cap definition counts only actual issued shares, not options/pool.
         Saves cleaned full text + candidates_*.jsonl for manual oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# Search phrases for FULLY-DILUTED basis (explicit includes of options/pool/convertibles)
FULLY_DILUTED = [
    '"fully diluted basis"',
    '"Capitalization" "include all outstanding"',
    '"fully-diluted capitalization"',
    '"on a fully diluted basis"',
    '"shall include all issued"',
    '"Unissued Option Pool"',
    '"all outstanding shares and" "options"',
    '"fully diluted" "conversion"',
    '"as converted" "all convertible"'
]

# Search phrases for ISSUED-AND-OUTSTANDING basis (narrower, no options/pool)
ISSUED_OUTSTANDING = [
    '"issued and outstanding shares"',
    '"only actual issued shares"',
    '"excluding options and warrants"',
    '"not including" "option pool"',
    '"Common Stock" "issued"',
    '"ordinary issued"',
]

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def pull():
    seen = set(); fully = []; issued = []
    
    print("Fetching FULLY-DILUTED candidates...")
    for ph in FULLY_DILUTED:
        try:
            hits = fts_search(ph, limit=8)
        except Exception as e:
            print(f"  ERR {ph}: {e}"); continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen: continue
            seen.add(cid)
            try:
                txt = fetch_clean(build_url(h))
            except Exception as e:
                print(f"  fetch ERR {cid}: {e}"); continue
            if not txt or len(txt) < 400: continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            fully.append({"id": cid, "company": company_of(h), "url": build_url(h),
                          "phrase_count": txt.lower().count("fully diluted") + txt.lower().count("fully-diluted")})
    
    print("Fetching ISSUED-OUTSTANDING candidates...")
    for ph in ISSUED_OUTSTANDING:
        try:
            hits = fts_search(ph, limit=10)
        except Exception as e:
            print(f"  ERR {ph}: {e}"); continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen: continue
            seen.add(cid)
            try:
                txt = fetch_clean(build_url(h))
            except Exception as e:
                print(f"  fetch ERR {cid}: {e}"); continue
            if not txt or len(txt) < 400: continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            issued.append({"id": cid, "company": company_of(h), "url": build_url(h),
                           "basis_count": txt.lower().count("issued and outstanding")})
    
    with open(HERE / "candidates_fully_diluted.jsonl", "w") as f:
        for d in fully: f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_issued_outstanding.jsonl", "w") as f:
        for d in issued: f.write(json.dumps(d) + "\n")
    
    print(f"\nFULLY-DILUTED pool: {len(fully)} docs")
    for d in fully: print(f"   {d['phrase_count']:3}  {d['id']:40} {d['company']}")
    print(f"\nISSUED-OUTSTANDING pool: {len(issued)} docs")
    for d in issued: print(f"   {d['basis_count']:3}  {d['id']:40} {d['company']}")

if __name__ == "__main__":
    pull()
