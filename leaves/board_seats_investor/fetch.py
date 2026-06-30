"""
Location: leaves/board_seats_investor/fetch.py
Purpose: Pull candidate docs for the board_seats_investor leaf (extraction task).
         Gathers Voting Agreements / Investors' Rights Agreements with explicit
         board-seat designation language. Saves cleaned full text + candidates_present.jsonl
         (id/company/url/keyword_count) for the MANUAL oracle pass.
Functions: pull()
Imports: edgar (shared), json, re, pathlib
"""
import sys, json, re, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# Board-seat designation phrases: Voting Agreements, Investors' Rights Agreements
# with explicit language about designating directors / board members
PHRASES = [
    '"designate one member" "Voting Agreement"',
    '"right to designate" director',
    '"elect to the Board" Investor',
    '"Series A Director"',
]

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def count_keywords(text):
    """Count occurrences of board-seat related keywords (case-insensitive)."""
    low = text.lower()
    count = 0
    keywords = ["designate", "director", "board", "voting agreement", "investors rights"]
    for kw in keywords:
        count += low.count(kw)
    return count

def extract_board_count_snippet(text):
    """Try to find an explicit numeric board-seat count in the text."""
    # Look for patterns like "one (1) director", "two (2) directors", "Series A Director", etc.
    patterns = [
        r'(one|two|three|four|five|six|seven|eight|nine)\s*\(\d+\)\s*(director|seat|member)',
        r'\((\d+)\)\s*(director|seat|member)',
        r'Series\s+[A-Z]\s+(Director|board member|seat)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def pull():
    seen = set()
    candidates = []
    
    for ph in PHRASES:
        print(f"\nSearching: {ph}")
        try:
            hits = fts_search(ph, limit=10)
        except Exception as e:
            print(f"  ERR {ph}: {e}")
            continue
        
        if not hits:
            print(f"  0 hits for {ph}")
            continue
        
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt", "").replace(".htm", "")
            if cid in seen:
                continue
            seen.add(cid)
            
            try:
                txt = fetch_clean(build_url(h))
            except Exception as e:
                print(f"  fetch ERR {cid}: {e}")
                continue
            
            if not txt or len(txt) < 400:
                print(f"  SKIP {cid} (too short: {len(txt)} chars)")
                continue
            
            # Save full text
            (FULL / f"{cid}.txt").write_text(txt, encoding="utf-8")
            
            kw_count = count_keywords(txt)
            board_snippet = extract_board_count_snippet(txt)
            
            candidates.append({
                "id": cid,
                "company": company_of(h),
                "url": build_url(h),
                "board_count": kw_count,
            })
            
            print(f"  OK {cid:40} | {company_of(h):30} | kw={kw_count:2} | {board_snippet or '(no explicit count)'}")
            time.sleep(0.5)  # be polite to EDGAR
    
    # Write candidates file
    with open(HERE / "candidates_present.jsonl", "w") as f:
        for d in candidates:
            f.write(json.dumps(d) + "\n")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total docs saved: {len(candidates)}")
    print(f"\nDocs by id | company | keyword_count:")
    for d in sorted(candidates, key=lambda x: x['id']):
        # Read the saved file to get a snippet
        try:
            saved_txt = (FULL / f"{d['id']}.txt").read_text(encoding="utf-8")
            snippet = saved_txt[:150].replace("\n", " ").strip()
        except:
            snippet = "(could not read)"
        print(f"{d['id']:40} | {d['company']:30} | {d['board_count']:2} | {snippet}...")

if __name__ == "__main__":
    pull()
