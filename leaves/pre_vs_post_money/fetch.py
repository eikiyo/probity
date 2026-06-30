"""
Location: leaves/pre_vs_post_money/fetch.py
Purpose: Pull candidate priced-equity documents from SEC EDGAR (Series Seed/A/B). Search for
         "pre-money valuation" and "post-money valuation" terms. Each doc's full text is saved;
         candidates_pre.jsonl and candidates_post.jsonl record metadata for manual oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# Search phrases for pre-money and post-money priced equity rounds
PRE_PHRASES = ['"pre-money valuation"', '"on a pre-money basis"', '"pre-money capitalization"']
POST_PHRASES = ['"post-money valuation"', '"on a post-money basis"', '"post-money capitalization"']

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def pull():
    seen = set(); pre = []; post = []
    
    # Fetch pre-money candidates
    for ph in PRE_PHRASES:
        print(f"  searching {ph}...", flush=True)
        try: hits = fts_search(ph, limit=12)
        except Exception as e: print(f"  ERR {ph}: {e}", flush=True); continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen: continue
            seen.add(cid)
            try: 
                txt = fetch_clean(build_url(h))
                time.sleep(0.3)
            except Exception as e: print(f"  fetch ERR {cid}: {e}", flush=True); continue
            if not txt or len(txt) < 600: continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            pre.append({"id": cid, "company": company_of(h), "url": build_url(h),
                        "file_type": h["_source"].get("file_type", ""),
                        "pre_count": txt.lower().count("pre-money valuation"),
                        "post_count": txt.lower().count("post-money valuation")})
            print(f"    + {cid} {company_of(h)[:50]}", flush=True)
    
    # Fetch post-money candidates
    for ph in POST_PHRASES:
        print(f"  searching {ph}...", flush=True)
        try: hits = fts_search(ph, limit=12)
        except Exception as e: print(f"  ERR {ph}: {e}", flush=True); continue
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            if cid in seen: continue
            seen.add(cid)
            try: 
                txt = fetch_clean(build_url(h))
                time.sleep(0.3)
            except Exception as e: print(f"  fetch ERR {cid}: {e}", flush=True); continue
            if not txt or len(txt) < 600: continue
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            post.append({"id": cid, "company": company_of(h), "url": build_url(h),
                         "file_type": h["_source"].get("file_type", ""),
                         "pre_count": txt.lower().count("pre-money valuation"),
                         "post_count": txt.lower().count("post-money valuation")})
            print(f"    + {cid} {company_of(h)[:50]}", flush=True)
    
    with open(HERE / "candidates_pre.jsonl", "w") as f:
        for d in pre: f.write(json.dumps(d) + "\n")
    with open(HERE / "candidates_post.jsonl", "w") as f:
        for d in post: f.write(json.dumps(d) + "\n")
    
    print(f"\nPRE-MONEY pool: {len(pre)} docs", flush=True)
    print(f"POST-MONEY pool: {len(post)} docs", flush=True)

if __name__ == "__main__":
    pull()
