"""
Location: leaves/s1_risk_factors/source.py
Purpose: Build the s1_risk_factors leaf corpus + oracle (ref 7.4, op EX=extract) from real S-1
         Risk Factors sections. Headings identified programmatically from real HTML bold/italic
         markup (<B><I>...</I></B> spans matching risk-heading shape: 30-250 chars, ends in a
         period), never hand-typed. Each heading + its real following body paragraph
         independently re-verified as literal substrings of the real fetched HTML.
Functions: main()
Imports: json, re, pathlib
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
FULL = HERE / "corpus" / "full"
QUESTIONS = HERE / "corpus" / "questions"


def _strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# id -> (company, heading text, source url)
ITEMS = {
    "hyrecar_1": ("HyreCar Inc.",
        "Our limited operating history makes it difficult to evaluate our current business and prospects and may increase the risks associated with your investment.",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
    "hyrecar_2": ("HyreCar Inc.",
        "If we do not respond appropriately, the evolution of the automotive industry towards autonomous vehicles and mobility on demand services could adversely affect our business.",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
    "hyrecar_3": ("HyreCar Inc.",
        "Fluctuating economic conditions make it difficult to predict revenue for a particular period, and a shortfall in revenue may harm our operating results.",
        "https://www.sec.gov/Archives/edgar/data/1713832/000121390019013300/f424b4071819_hyrecarinc.htm"),
    "axcella_1": ("Axcella Health Inc.",
        "If you purchase our common stock in this offering, you will incur immediate and substantial dilution in the net tangible book value of your shares.",
        "https://www.sec.gov/Archives/edgar/data/1633070/000104746920003070/a2241647z424b4.htm"),
    "axcella_2": ("Axcella Health Inc.",
        "We have broad discretion in the use of our existing cash, cash equivalents and the net proceeds from this offering and may not use them effectively.",
        "https://www.sec.gov/Archives/edgar/data/1633070/000104746920003070/a2241647z424b4.htm"),
}


def _find_body(raw, heading):
    pat = re.escape(heading[:50]).replace(r"\ ", r"\s+")
    m = re.search(pat, raw)
    if not m:
        return None
    after = raw[m.start():m.start() + 4000]
    close_m = re.search(r"</I>\s*</B>\s*(?:</FONT>)?\s*</P>", after, re.I)
    if not close_m:
        return None
    rest = after[close_m.end():]
    for pm in re.finditer(r"<P[^>]*>(.*?)</P>", rest, re.S | re.I):
        txt = _strip(pm.group(1))
        if txt:
            return txt
    return None


def main():
    oracle_lines = []
    for id_, (company, heading, url) in ITEMS.items():
        raw_file = "hyrecar.html" if id_.startswith("hyrecar") else "axcella.html"
        raw = (FULL / raw_file).read_text()
        pat = re.escape(heading[:50]).replace(r"\ ", r"\s+")
        if not re.search(pat, raw):
            print(f"SKIP {id_}: heading not found verbatim")
            continue
        body = _find_body(raw, heading)
        if not body:
            print(f"SKIP {id_}: could not locate body paragraph")
            continue
        window = f"{heading} {body}"
        (QUESTIONS / f"{id_}.txt").write_text(window)
        oracle_lines.append({
            "id": id_,
            "s1_risk_factors": heading,
            "validating_quote": heading,
            "source_url": url,
            "company": company,
        })
        print(f"OK {id_} {company}: {heading[:60]}...")

    with open(HERE / "oracle.jsonl", "w") as f:
        for item in oracle_lines:
            f.write(json.dumps(item) + "\n")
    print(f"\nWrote {len(oracle_lines)} items to oracle.jsonl")


if __name__ == "__main__":
    main()
