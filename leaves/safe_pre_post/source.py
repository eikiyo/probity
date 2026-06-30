"""
Location: leaves/safe_pre_post/source.py
Purpose: Source REAL YC SAFEs from SEC EDGAR and classify pre-money vs post-money. Reuses
         engine/edgar. Requires the doc to BE a SAFE (excludes narrative prospectuses). hint_class
         is a search bucket; every item is hand-verified before the oracle.
Imports: engine.edgar, json, pathlib
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
import edgar  # noqa: E402

HERE = Path(__file__).parent
RAW, FULL = HERE / "corpus" / "raw", HERE / "corpus" / "full"
SECTION = ["valuation cap", "company capitalization", "conversion price", "post-money", "pre-money"]
DET = ["post-money valuation cap", "pre-money valuation cap", "company capitalization",
       "converting securities", "conversion price", "valuation cap", "as-converted",
       "safe price", "liquidity price", "standard preferred"]
PHRASES = [
    ('"Post-Money Valuation Cap"', "post-money"),
    ('"Pre-Money Valuation Cap"', "pre-money"),
    ('"based on the Post-Money Valuation Cap"', "post-money"),
    ('"the Company Capitalization"', "post-money"),
]
MAX_PER_CIK = 1


def is_safe(text):
    low = text.lower()
    return "this safe" in low or "simple agreement for future equity" in low


def main():
    RAW.mkdir(parents=True, exist_ok=True); FULL.mkdir(parents=True, exist_ok=True)
    have, added = set(), 0
    for phrase, hint in PHRASES:
        for h in edgar.fts_search(phrase, limit=16):
            src = h["_source"]; cik = int(src["ciks"][0])
            if cik in have:
                continue
            try:
                full = edgar.fetch_clean(edgar.build_url(h))
            except Exception as e:
                print(f"  fetch FAIL {cik}: {e}", flush=True); continue
            time.sleep(0.3)
            if not is_safe(full) or len(full) > 40000:  # must be an actual SAFE form, not a prospectus
                continue
            clause = edgar.best_window(full, SECTION, DET, window=3800)
            if len(clause) < 500 or "valuation cap" not in clause.lower():
                continue
            have.add(cik); cid = f"{cik}_{src['adsh'].replace('-', '')}"
            (RAW / f"{cid}.txt").write_text(clause); (FULL / f"{cid}.txt").write_text(full)
            with open(HERE / "candidates.jsonl", "a") as f:
                f.write(json.dumps({"id": cid, "company": src["display_names"][0],
                                    "file_type": src.get("file_type"), "url": edgar.build_url(h),
                                    "hint_class": hint, "clause_chars": len(clause)}) + "\n")
            added += 1; print(f"  + {cid} [{hint}] {src['display_names'][0][:42]}", flush=True)
    print(f"\nADDED {added} SAFE candidates", flush=True)


if __name__ == "__main__":
    main()
