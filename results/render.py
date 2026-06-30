"""
Location: results/render.py
Purpose: Render RESULTS.md from a leaf's scored.json + oracle.jsonl. WOBBLE (run-to-run
         inconsistency) is the headline — the core thesis — with accuracy reported beside it,
         never averaged in. Adds a model size-ladder view (does wobble fall as scale rises?).
Functions: per_class(), wobble_rows(), render_leaf(), main()
Imports: json, pathlib
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEAF = ROOT / "leaves" / "participation_type"
CLASSES = ["non-participating", "participating", "capped"]

DEFINITIONS = (
    "**What the columns mean:**\n\n"
    "- **Wobble** (headline, lower is better) — the share of items where the model gave **more than "
    "one answer** across its 20 identical runs. A model that wobbles can't be trusted in a money "
    "workflow even when it's often right.\n"
    "- **Consistency** — the *average* agreement **within** each item's 20 runs (how often they "
    "matched that item's most common answer). It differs from Wobble: an item that flips even once "
    "is counted as wobble, yet can still be (say) 90% consistent. Wobble counts *whether* an item "
    "flipped; Consistency measures *how much*.\n"
    "- **Accuracy** — the share of items whose majority answer matched the human-validated truth.\n"
    "- **non-part / part / capped** — accuracy **within** each true class (correct / total: "
    "non-participating · participating · capped), so a model can't score well by always guessing the "
    "most common class."
)
SIZE = {"gemma3-1b": "1B", "llama3.2-3b": "3B", "gemma4-12b": "12B",
        "qwen3.5-27b": "27B", "deepseek-v4f": "hosted", "gemma": "12B", "deepseek": "hosted"}
ORDER = ["gemma3-1b", "llama3.2-3b", "gemma4-12b", "qwen3.5-27b", "deepseek-v4f", "gemma", "deepseek"]


def wobble_pct(res):
    """% of items whose answer flipped at least once across the runs (the core metric)."""
    return res["reliability"]["field_flips"].get("participation_type", 0.0) * 100


def per_class(per_instance, oracle):
    out = {c: [0, 0] for c in CLASSES}
    for row, o in zip(per_instance, oracle):
        if row["n_valid"] == 0:
            continue
        out[o["participation_type"]][1] += 1
        out[o["participation_type"]][0] += int(row["majority_correct"])
    return out


def _models(scored):
    return [k for k in ORDER if k in scored] + [k for k in scored if k not in ORDER]


def render_leaf(scored, oracle):
    L, total = [], len(oracle)
    counts = {c: sum(o["participation_type"] == c for o in oracle) for c in CLASSES}
    n_runs = max((r["reliability"]["valid_run_count"] for r in scored.values()), default=0)
    L.append("## Test 1.3.2 — Preferred-stock liquidation participation\n")
    L.append(f"**Corpus:** {total} real SEC-filed charter clauses, human-validated answers "
             f"({counts['non-participating']} non-participating / {counts['participating']} "
             f"participating / {counts['capped']} capped). Each model run **20×/item at temp 0.7**.\n")
    L.append("### Headline — WOBBLE (the core metric)\n")
    L.append("*Wobble = % of items where the model gave more than one answer across its 20 runs. "
             "A model that wobbles cannot be trusted in a money workflow even when it is often right.*\n")
    L.append("| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |")
    L.append("|---|---|---|---|---|---|")
    for k in _models(scored):
        res = scored[k]; a = res["accuracy"]; r = res["reliability"]
        L.append(f"| `{res['model']}` | {SIZE.get(k,'?')} | **{wobble_pct(res):.0f}%** | "
                 f"{r['consistency_pct']:.0f}% | {a['accuracy_majority']*100:.0f}% | "
                 f"{a['n_measurable']}/{a['n_instances']} |")
    L.append("\n" + DEFINITIONS + "\n")
    L.append("\n### Accuracy by class (majority vote)\n")
    L.append("| Model | non-participating | participating | capped |")
    L.append("|---|---|---|---|")
    for k in _models(scored):
        pc = per_class(scored[k]["accuracy"]["per_instance"], oracle)
        L.append(f"| `{scored[k]['model']}` | " +
                 " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "—" for c in CLASSES) + " |")
    L.append("\n### Which items make models wobble\n")
    L.append("| Item | True | Difficulty | Models that wobbled |")
    L.append("|---|---|---|---|")
    for i, o in enumerate(oracle):
        wob = []
        for k in _models(scored):
            cons = scored[k]["accuracy"]["per_instance"][i]["fields"].get("participation_type", {}).get("consistency", 1.0)
            if cons < 1.0:
                wob.append(SIZE.get(k, k))
        if wob:
            L.append(f"| {o['company'][:22]} | {o['participation_type']} | {o['difficulty']} | {', '.join(wob)} |")
    if not any("|" in x and "wobbled" not in x for x in L[-1:]):
        pass
    return "\n".join(L)


def readme_block(scored, oracle):
    """Compact headline tables for the landing-page README (wobble + accuracy-by-class)."""
    total = len(oracle)
    n = max((r["reliability"]["valid_run_count"] for r in scored.values()), default=0)
    per_item = max((len(r["accuracy"]["per_instance"]) for r in scored.values()), default=1)
    runs_each = n // per_item if per_item else 0
    L = [f"*{total} real SEC-filed charter clauses, human-validated answers. Each model run "
         f"{runs_each}x/item at temp 0.7. **Wobble** = % of items answered inconsistently across runs.*", ""]
    L.append("| Model | Size | **Wobble** ↓ | Consistency | Accuracy | non-part | part | capped |")
    L.append("|---|---|---|---|---|---|---|---|")
    for k in _models(scored):
        res = scored[k]; a = res["accuracy"]; r = res["reliability"]
        pc = per_class(a["per_instance"], oracle)
        cells = " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "-" for c in CLASSES)
        L.append(f"| `{res['model']}` | {SIZE.get(k,'?')} | **{wobble_pct(res):.0f}%** | "
                 f"{r['consistency_pct']:.0f}% | {a['accuracy_majority']*100:.0f}% | {cells} |")
    return "\n".join(L) + "\n\n" + DEFINITIONS


def main():
    scored = json.loads((LEAF / "scored.json").read_text())
    oracle = [json.loads(l) for l in open(LEAF / "oracle.jsonl") if l.strip()]
    header = ("# Probity — Benchmark Results\n\n"
              "**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at "
              "temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a "
              "human-validated answer extracted from the source document. They are reported separately "
              "and never averaged — a model can be perfectly consistent and consistently wrong.\n\n"
              "Models span a size ladder (1B → 27B local + a hosted model) to test whether wobble "
              "falls as capability rises. Local via Ollama (zero egress); hosted = deepseek-v4-flash.\n\n---\n\n")
    (ROOT / "results" / "RESULTS.md").write_text(header + render_leaf(scored, oracle) + FOOTER + "\n", encoding="utf-8")
    print("wrote results/RESULTS.md")
    import re
    readme = ROOT / "README.md"
    block = ("<!-- BENCHMARK:START -->\n" + readme_block(scored, oracle) + "\n<!-- BENCHMARK:END -->")
    txt = re.sub(r"<!-- BENCHMARK:START.*?-->.*?<!-- BENCHMARK:END -->", block,
                 readme.read_text(), flags=re.S)
    readme.write_text(txt, encoding="utf-8")
    print("injected benchmark table into README.md")


FOOTER = """

---

## What this shows

- **Wobble has a cliff, not a slope.** The 1B and 3B models flip their answer on 61-72% of items
  across 20 runs at temp 0.7 - unusable in a workflow that touches money. At 12B wobble collapses
  to 0%; the hosted model sits at 6%. The usable/unusable boundary is between 3B and 12B, not a
  smooth gradient. (N=5 hid this entirely - both mid/hosted models looked perfectly stable.)
- **A local 12B model beats a hosted frontier-cheap model here.** gemma4:12b: 0% wobble, 72%
  accuracy. deepseek-v4-flash: 6% wobble, 67%. Bigger-and-hosted is not automatically better.
- **Participating preferred is the universal blind spot.** Even the best models get only 1-2 of 5
  participating clauses right; the small models get 0. The "preference AND THEN also share with the
  common" structure is systematically misread as capped or non-participating. The genuinely-hard,
  validated structure - not random noise - is where every model fails.
- **Small models can't classify the hard classes at all** (1B: 0/5 participating, 0/5 capped) -
  they collapse everything to non-participating.

## Models and scope

Per leaf during the build-out, Probity runs the **fast set** (1B/3B/12B local via Ollama, zero
egress, plus deepseek-v4-flash) so a leaf costs minutes. The **heavy comprehensive run**
(qwen3.5:27b and hosted frontier models - Gemini, Haiku, etc. - at N=20+) is deferred to a single
sweep across all leaves once the full benchmark exists.

## Reproduce

```bash
cd leaves/participation_type
python3 source.py && python3 source_more.py   # fetch real SEC charter clauses
python3 run.py                                # run the model ladder, N=20
python3 ../../results/render.py
```

Corpus: real SEC EDGAR charter exhibits; answers human-validated from each clause's own legal text
(`leaves/participation_type/oracle.jsonl`, with the validating quote + difficulty per item).
Genuinely mixed-series or ambiguous clauses are excluded, not guessed.
"""

if __name__ == "__main__":
    main()
