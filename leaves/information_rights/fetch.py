"""
Location: leaves/information_rights/fetch.py
Purpose: Pull candidate docs for the information_rights leaf. PRESENT pool = docs granting
         investors information rights (periodic financial statements, reports, cap tables);
         ABSENT pool = documents lacking such covenant (waivers, one-off purchases). Saves
         cleaned full text + candidates_*.jsonl (company/url/ir_count) for MANUAL oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# PRESENT: docs that GRANT investors info rights (annual/quarterly reports, cap tables, etc.)
PRESENT = [
    '"information rights"',
    '"annual financial statements" "investor"',
    '"deliver to each major investor"',
    '"inspection rights"',
]

# ABSENT: docs unlikely to grant ongoing information rights (waivers, one-off purchases)
ABSENT = [
    '"waiver of information rights"',
    '"Stock Purchase Agreement"',
    '"restricted stock agreement"',
]

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def count_info_rights(text):
    """Count occurrences of info-rights-related keywords (case-insensitive)."""
    low = text.lower()
    count = 0
    keywords = [
        "information rights",
        "financial statements",
        "inspection rights",
        "deliver to each",
        "major investor",
        "quarterly report",
        "annual report",
    ]
    for kw in keywords:
        count += low.count(kw)
    return count

def pull():
    seen = set(); pres = []; absn = []
    
    print("PRESENT pool (docs with information rights covenants):")
    for ph in PRESENT:
        print(f"  searching {ph}...", flush=True)
        try:
            hits = fts_search(ph, limit=10)
        except Exception as e:
            print(f"    ERR {ph}: {e}")
            continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen:
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
            ir_count = count_info_rights(txt)
            pres.append({"id": cid, "company": company_of(h), "url": build_url(h),
                         "ir_count": ir_count})
            print(f"    saved {cid}")
    
    print("\nABSENT pool (docs without information rights):")
    for ph in ABSENT:
        print(f"  searching {ph}...", flush=True)
        try:
            hits = fts_search(ph, limit=10)
        except Exception as e:
            print(f"    ERR {ph}: {e}")
            continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen:
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
            ir_count = count_info_rights(txt)
            absn.append({"id": cid, "company": company_of(h), "url": build_url(h),
                         "ir_count": ir_count})
            print(f"    saved {cid}")
    
    with open(HERE / "candidates_present.jsonl", "w") as f:
        for d in pres:
            f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_absent.jsonl", "w") as f:
        for d in absn:
            f.write(json.dumps(d) + "\n")
    
    print(f"\n=== RESULTS ===")
    print(f"PRESENT pool: {len(pres)} docs")
    for d in pres:
        first_150 = (FULL / f"{d['id']}.txt").read_text()[:150].replace("\n", " ")
        print(f"  {d['id']} | {d['company'][:30]:30} | ir_count={d['ir_count']:2} | {first_150}...")
    
    print(f"\nABSENT pool: {len(absn)} docs")
    for d in absn:
        first_150 = (FULL / f"{d['id']}.txt").read_text()[:150].replace("\n", " ")
        print(f"  {d['id']} | {d['company'][:30]:30} | ir_count={d['ir_count']:2} | {first_150}...")

if __name__ == "__main__":
    pull()
