"""
Location: leaves/flag_full_ratchet/fetch.py
Purpose: Pull candidate docs for the flag_full_ratchet leaf. FULL-RATCHET pool = docs with 
         full-ratchet anti-dilution language (rare); WEIGHTED-AVERAGE pool = documents with 
         weighted-average anti-dilution protection (common). Saves cleaned full text + 
         candidates_*.jsonl for MANUAL oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# FULL-RATCHET: docs that GRANT full-ratchet anti-dilution protection (rare, founder-hostile)
FULL_RATCHET = [
    '"full ratchet"',
    '"full-ratchet" anti-dilution',
    '"full ratchet" preferred',
]

# WEIGHTED-AVERAGE: docs with weighted-average anti-dilution protection (common, standard)
WEIGHTED_AVG = [
    '"weighted average" "anti-dilution"',
    '"broad-based weighted average"',
    '"weighted average" "conversion price"',
]

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def pull():
    seen = set()
    full_ratchet_cands = []
    weighted_avg_cands = []
    
    print("FULL-RATCHET pool (docs with full-ratchet anti-dilution):")
    for ph in FULL_RATCHET:
        print(f"  searching {ph}...", flush=True)
        try:
            hits = fts_search(ph, limit=20)
        except Exception as e:
            print(f"    ERR {ph}: {e}")
            continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen or len(full_ratchet_cands) >= 8:
                continue
            seen.add(cid)
            try:
                txt = fetch_clean(build_url(h))
            except Exception as e:
                print(f"    fetch ERR {cid}: {e}")
                continue
            if not txt or len(txt) < 400:
                continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            full_ratchet_cands.append({"id": cid, "company": company_of(h), "url": build_url(h)})
            print(f"    saved {cid}")
    
    print("\nWEIGHTED-AVERAGE pool (docs with weighted-average anti-dilution):")
    for ph in WEIGHTED_AVG:
        print(f"  searching {ph}...", flush=True)
        try:
            hits = fts_search(ph, limit=20)
        except Exception as e:
            print(f"    ERR {ph}: {e}")
            continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen or len(weighted_avg_cands) >= 8:
                continue
            seen.add(cid)
            try:
                txt = fetch_clean(build_url(h))
            except Exception as e:
                print(f"    fetch ERR {cid}: {e}")
                continue
            if not txt or len(txt) < 400:
                continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            weighted_avg_cands.append({"id": cid, "company": company_of(h), "url": build_url(h)})
            print(f"    saved {cid}")
    
    with open(HERE / "candidates_full_ratchet.jsonl", "w") as f:
        for d in full_ratchet_cands:
            f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_weighted_avg.jsonl", "w") as f:
        for d in weighted_avg_cands:
            f.write(json.dumps(d) + "\n")
    
    print(f"\n=== RESULTS ===")
    print(f"FULL-RATCHET pool: {len(full_ratchet_cands)} docs")
    print(f"WEIGHTED-AVERAGE pool: {len(weighted_avg_cands)} docs")

if __name__ == "__main__":
    pull()
