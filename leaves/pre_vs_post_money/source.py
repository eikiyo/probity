"""
Location: leaves/pre_vs_post_money/source.py
Purpose: Build the pre_vs_post_money leaf oracle from fetched priced-equity docs. Filter out SAFEs
         (which are separate leaf 2.1.4), keep only Series A/B/Seed Stock Purchase Agreements.
         Each item is hand-verified against the real document's valuation basis language.
Functions: is_safe(), window_on(), load_meta(), main()
Imports: json, re, pathlib
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"

# Hand-verified items: (cid, label, anchor_phrase, difficulty)
# label = "pre-money" or "post-money"
# anchor = substring phrase from the doc that declares the basis
ITEMS = {
    # PRE-MONEY basis
    "0001193125-14-335661_d770501dex1024": ("pre-money", "Pre-Money Valuation", "easy"),
    "0000950123-10-024887_d70440a2exv3w3": ("pre-money", "Pre-Money Valuation", "easy"),
    "0001047469-04-038327_filename35": ("pre-money", "pre-money", "easy"),
    "0001140361-23-024212_ny20009051x2_8k": ("pre-money", "pre-money valuation", "easy"),
    "0001213900-25-077022_filename4": ("pre-money", "pre-money valuation", "easy"),
    "0001213900-25-123767_ea026659901ex10-4_neo": ("pre-money", "pre-money valuation", "easy"),
    "0001213900-25-123767_ea026659901ex10-5_neo": ("pre-money", "pre-money valuation", "easy"),
    "0001213900-25-123767_ea026659901ex10-6_neo": ("pre-money", "pre-money valuation", "easy"),
    "0001213900-25-077022_filename5": ("pre-money", "pre-money valuation", "easy"),
    "0001213900-25-077022_filename6": ("pre-money", "pre-money valuation", "easy"),
    "0000912057-19-000378_filename29": ("pre-money", "pre-money valuation", "easy"),
    "0000950123-14-012213_filename17": ("pre-money", "pre-money valuation", "easy"),
    # NOTE (2026-07-02, adversarial audit, Eikiyo-confirmed): the "_8k" variants of these two
    # Cytosorbents items were REMOVED here -- each was the SAME underlying convertible-note
    # transaction as its sibling "_ex10-1" item below (same accession number, near-identical
    # boilerplate text), just cited via the 8-K body instead of its own Exhibit 10.1. Counting
    # both inflated N from 19 unique transactions to 21 and double-weighted 2 real facts. Kept
    # the more complete "_ex10-1" full-text versions; see AUDIT_TODO.md for the full finding.
    "0001144204-10-046527_v195191_ex10-1": ("pre-money", "pre-money basis", "medium"),
    "0001193125-11-026716_filename6": ("pre-money", "pre-money valuation", "medium"),
    "0001193125-23-255006_d569281dex991": ("pre-money", "pre-money valuation", "medium"),
    "0001437749-18-019139_ex_127203": ("pre-money", "pre-money basis", "medium"),
    "0001144204-11-010165_v212119_ex10-1": ("pre-money", "pre-money basis", "medium"),
    "0001013762-09-002046_ex412": ("pre-money", "pre-money basis", "easy"),
    "0001607062-21-000118_filename14": ("pre-money", "pre-money", "easy"),
    "0001193125-11-124790_filename20": ("pre-money", "pre-money valuation", "easy"),
    "0001013762-09-001055_ex101": ("pre-money", "pre-money basis", "easy"),
    "0001193125-07-111369_dex31": ("pre-money", "pre-money valuation", "medium"),
    
    # POST-MONEY basis
    "0001213900-22-000982_ea153649ex3-1_creciinc": ("post-money", "POST-MONEY VALUATION CAP", "easy"),
    "0001493152-24-049571_form8-k": ("post-money", "post-money valuation", "easy"),
    "0001213900-25-014354_ea023010901ex99-1_fold": ("post-money", "post-money valuation", "easy"),
    "0001575872-26-000456_amass029_ex10-1": ("post-money", "post-money valuation", "easy"),
    "0001575872-26-000442_amass027_ex10-2": ("post-money", "post-money valuation", "easy"),
    "0001575872-26-000442_amass027_ex10-1": ("post-money", "post-money valuation", "easy"),
    "0001145236-02-000130_adpverilink10_22": ("post-money", "post-money valuation", "medium"),
    "0001511164-13-000507_ngeform8k11413": ("post-money", "post-money valuation", "easy"),
    "0001213900-24-095442_ea021976201ex4-2_lomond": ("post-money", "post-money valuation", "easy"),
    "0001096906-21-002893_byoc_ex10z1": ("post-money", "post-money valuation", "easy"),
    "0001213900-20-033888_ea128838ex3-1_oraclehealth": ("post-money", "post-money valuation", "easy"),
    "0001213900-26-025748_ea025686308ex10-2": ("post-money", "post-money valuation", "easy"),
    "0001628279-24-000336_filename9": ("post-money", "post-money valuation", "easy"),
    "0001628280-24-041596_exhibit109-sx1": ("post-money", "post-money basis", "medium"),
    "0001628280-26-029515_exhibit101e-sx1a": ("post-money", "post-money valuation", "easy"),
    "0001104659-23-071887_tm2318720d1_ex99-1": ("post-money", "post-money valuation", "easy"),
    "0001019687-14-000407_oculus_8k-ex1002": ("post-money", "post-money basis", "medium"),
    "0001019687-13-002945_oculus_8k-ex1001": ("post-money", "post-money basis", "medium"),
    "0001144204-14-011078_v367545_ex10-9": ("post-money", "post-money valuation", "easy"),
}

def is_safe(text):
    """True if the doc is a SAFE, which we exclude (that's leaf 2.1.4)."""
    low = text.lower()
    return ("simple agreement for future equity" in low or 
            ("this safe" in low and "safe is based on" in low))

def window_on(text, anchor, before=400, after=800):
    """Extract a window around the anchor phrase."""
    idx = text.lower().find(anchor.lower())
    if idx < 0:
        return None, None
    s = max(0, idx - before)
    e = min(len(text), idx + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    # Extract a shorter quote around the anchor
    qs = max(0, idx - 50)
    qe = min(len(text), idx + len(anchor) + 120)
    quote = re.sub(r"\s+", " ", text[qs:qe]).strip()
    return win, quote

def load_meta():
    """Load metadata from candidates files."""
    meta = {}
    for fn in [HERE / "candidates_pre.jsonl", HERE / "candidates_post.jsonl"]:
        if fn.exists():
            for line in open(fn):
                if line.strip():
                    d = json.loads(line)
                    meta[d["id"]] = d
    return meta

def main():
    meta = load_meta()
    (HERE / "corpus" / "questions").mkdir(parents=True, exist_ok=True)
    oracle = []
    dropped = 0
    
    for cid, (label, anchor, difficulty) in ITEMS.items():
        p = FULL / f"{cid}.txt"
        if not p.exists():
            print(f"MISSING {cid} — skip", flush=True)
            continue
        
        full = p.read_text(errors="ignore")
        
        # Fail-closed: exclude SAFEs
        if is_safe(full):
            print(f"DROP {cid}: is a SAFE, not priced equity — fail-closed", flush=True)
            dropped += 1
            continue
        
        # Anchor must exist in the text
        win, quote = window_on(full, anchor)
        if not win:
            print(f"ANCHOR NOT FOUND in {cid} ({anchor[:40]}) — skip", flush=True)
            dropped += 1
            continue
        
        # Write the question window
        (HERE / "corpus" / "questions" / f"{cid}.txt").write_text(win, encoding="utf-8")
        
        c = meta.get(cid, {})
        company = re.sub(r"\s*\(.*$", "", c.get("company", "?")).strip()
        
        oracle.append({
            "id": cid,
            "company": company,
            "pre_vs_post_money": label,
            "anchor": anchor,
            "validating_quote": quote,
            "difficulty": difficulty,
            "url": c.get("url", "")
        })
        print(f"  ✓ {cid} [{label}] {company[:45]}", flush=True)
    
    with open(HERE / "oracle.jsonl", "w", encoding="utf-8") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    
    from collections import Counter
    counts = Counter(o["pre_vs_post_money"] for o in oracle)
    print(f"\nwrote {len(oracle)} items  {dict(counts)}  (dropped {dropped})", flush=True)

if __name__ == "__main__":
    main()
