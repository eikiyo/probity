"""Second fetch pass targeting financing documents and SAFEs with explicit cap definitions."""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from edgar import fts_search, build_url, fetch_clean  # noqa: E402

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# More specific searches for financing documents
FINANCING_SEARCHES = [
    '"valuation cap" "capitalization"',
    '"Capitalization means" "issued"',
    '"Company Capitalization" "aggregate"',
    '"post-money valuation" "issued and outstanding"',
    '"option pool" "fully diluted"',
]

def company_of(hit):
    dn = hit["_source"].get("display_names", ["?"])
    return re.sub(r"\s*\(CIK.*$", "", dn[0]).strip() if dn else "?"

def pull():
    print("Running second fetch for better examples...")
    for ph in FINANCING_SEARCHES:
        try:
            hits = fts_search(ph, limit=5)
        except Exception as e:
            print(f"  ERR {ph}: {e}"); continue
        print(f"  Search '{ph[:40]}': {len(hits)} results")
        for h in hits:
            cid = h["_id"].replace(":", "_").replace(".txt","").replace(".htm","")
            fpath = FULL / f"{cid}.txt"
            if fpath.exists():
                print(f"    Already have {cid}")
            else:
                try:
                    txt = fetch_clean(build_url(h))
                except Exception as e:
                    print(f"    fetch ERR {cid}: {e}"); continue
                if txt and len(txt) > 400:
                    fpath.write_text(txt, encoding="utf-8")
                    print(f"    + Fetched {cid} ({len(txt)} chars)")

if __name__ == "__main__":
    pull()
