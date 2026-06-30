"""
Location: results/render.py
Purpose: Render RESULTS.md + the README landing-page table from EVERY leaf that has a scored.json.
         WOBBLE (run-to-run inconsistency) is the headline — the core thesis — with accuracy beside
         it, never averaged in. Multi-leaf: FIELD + CLASSES come from each leaf's own task.TASK
         (single source of truth); per-leaf display config lives in LEAVES.
Functions: load_leaf(), wobble_pct(), per_class(), definitions(), render_leaf(), readme_block_for(),
           auto_findings(), main()
Imports: json, re, importlib.util, pathlib
"""

import json
import re
import importlib.util
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Per-leaf DISPLAY config only — field + class enum are read from the leaf's task.TASK.
LEAVES = [
    {"slug": "participation_type",
     "title": "Test 1.3.2 — Preferred-stock liquidation participation",
     "corpus_desc": "real SEC-filed charter clauses",
     "labels": {"non-participating": "non-part", "participating": "part", "capped": "capped"}},
    {"slug": "safe_pre_post",
     "title": "Test 2.1.4 — SAFE valuation cap: pre-money vs post-money",
     "corpus_desc": "real SEC-filed YC SAFE provisions",
     "labels": {"post-money": "post", "pre-money": "pre"}},
    {"slug": "dividend_cumulative",
     "title": "Test 1.4.2 — Preferred dividends: cumulative vs non-cumulative",
     "corpus_desc": "real SEC-filed preferred-stock charter dividend clauses",
     "labels": {"cumulative": "cumulative", "non-cumulative": "non-cum"}},
    {"slug": "acceleration_trigger",
     "title": "Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger",
     "corpus_desc": "real SEC-filed equity-award / employment agreements",
     "labels": {"single-trigger": "single", "double-trigger": "double"}},
    {"slug": "preference_seniority",
     "title": "Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked",
     "corpus_desc": "real SEC-filed multi-series preferred charters",
     "labels": {"pari-passu": "pari-passu", "stacked": "stacked"}},
    {"slug": "flag_offmarket_liqpref",
     "title": "Test 8.1 — Risk flag: off-market liquidation preference (>1x)",
     "corpus_desc": "real SEC-filed preferred-stock liquidation clauses",
     "labels": {"yes": "off-market(>1x)", "no": "standard(1x)"}},
    {"slug": "redemption_rights",
     "title": "Test 1.7 — Redemption rights: redeemable vs non-redeemable",
     "corpus_desc": "real SEC-filed preferred-stock charter redemption clauses",
     "labels": {"yes": "redeemable", "no": "non-redeem"}},
    {"slug": "drag_along",
     "title": "Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)",
     "corpus_desc": "real SEC-filed stockholder/transfer agreements",
     "labels": {"yes": "drag(obligated)", "no": "co-sale(right)"}},
    {"slug": "rofr_cosale",
     "title": "Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent",
     "corpus_desc": "real SEC-filed stockholder/transfer documents",
     "labels": {"yes": "rofr/cosale", "no": "absent/other-right"}},
    {"slug": "pro_rata_rights",
     "title": "Test 5.4 — Pro-rata right on future financings: granted vs not",
     "corpus_desc": "real SEC-filed SAFEs, side letters and investors' rights agreements",
     "labels": {"yes": "pro-rata", "no": "absent/waived"}},
    {"slug": "cliff_present",
     "title": "Test 6.2 — Vesting schedule: cliff present vs absent",
     "corpus_desc": "real SEC-filed equity-award agreements and disclosures",
     "labels": {"yes": "cliff", "no": "no-cliff"}},
    {"slug": "protective_provisions",
     "title": "Test 5.2 — Protective provisions: investor class-veto right present vs absent",
     "corpus_desc": "real SEC-filed charters and governance documents",
     "labels": {"yes": "veto-right", "no": "absent"}},
    {"slug": "information_rights",
     "title": "Test 5.3 — Information rights: live financial-reporting obligation vs absent",
     "corpus_desc": "real SEC-filed investors' rights agreements and equity-award docs",
     "labels": {"yes": "info-rights", "no": "absent/waived"}},
]

SIZE = {"gemma3-1b": "1B", "llama3.2-3b": "3B", "gemma4-12b": "12B",
        "qwen3.5-27b": "27B", "deepseek-v4f": "hosted", "gemma": "12B", "deepseek": "hosted"}
ORDER = ["gemma3-1b", "llama3.2-3b", "gemma4-12b", "qwen3.5-27b", "deepseek-v4f", "gemma", "deepseek"]


def load_leaf(slug):
    """Return (field, classes, scored, oracle) for a leaf, deriving field+classes from its task.TASK."""
    leaf = ROOT / "leaves" / slug
    spec = importlib.util.spec_from_file_location(f"task_{slug}", leaf / "task.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    field = list(mod.TASK["fields"])[0]
    classes = mod.TASK["fields"][field]["values"]
    scored = json.loads((leaf / "scored.json").read_text())
    oracle = [json.loads(l) for l in open(leaf / "oracle.jsonl") if l.strip()]
    return field, classes, scored, oracle


def wobble_pct(res, field):
    """% of items whose answer flipped at least once across the runs (the core metric)."""
    return res["reliability"]["field_flips"].get(field, 0.0) * 100


def per_class(per_instance, oracle, field, classes):
    out = {c: [0, 0] for c in classes}
    for row, o in zip(per_instance, oracle):
        if row["n_valid"] == 0:
            continue
        out[o[field]][1] += 1
        out[o[field]][0] += int(row["majority_correct"])
    return out


def _models(scored):
    return [k for k in ORDER if k in scored] + [k for k in scored if k not in ORDER]


def _runs_each(scored):
    n = max((r["reliability"]["valid_run_count"] for r in scored.values()), default=0)
    per = max((len(r["accuracy"]["per_instance"]) for r in scored.values()), default=1)
    return n // per if per else 0


def definitions(labels, generic=False):
    cols = "the right-hand class columns" if generic else " · ".join(labels.values())
    return (
        "**What the columns mean:**\n\n"
        "- **Wobble** (headline, lower is better) — the share of items where the model gave **more "
        "than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a "
        "money workflow even when it's often right.\n"
        "- **Consistency** — the *average* agreement **within** each item's runs (how often they "
        "matched that item's most common answer). Wobble counts *whether* an item flipped; "
        "Consistency measures *how much*.\n"
        "- **Accuracy** — the share of items whose majority answer matched the human-validated truth.\n"
        f"- **{cols}** — accuracy **within** each true class (correct / total), so a model can't "
        "score well by always guessing the most common class.")


def _wobble_table(scored, field):
    L = ["| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable |",
         "|---|---|---|---|---|---|"]
    for k in _models(scored):
        res = scored[k]; a = res["accuracy"]; r = res["reliability"]
        L.append(f"| `{res['model']}` | {SIZE.get(k,'?')} | **{wobble_pct(res,field):.0f}%** | "
                 f"{r['consistency_pct']:.0f}% | {a['accuracy_majority']*100:.0f}% | "
                 f"{a['n_measurable']}/{a['n_instances']} |")
    return L


def _class_table(scored, oracle, field, classes, labels):
    L = ["| Model | " + " | ".join(labels[c] for c in classes) + " |",
         "|---|" + "---|" * len(classes)]
    for k in _models(scored):
        pc = per_class(scored[k]["accuracy"]["per_instance"], oracle, field, classes)
        L.append(f"| `{scored[k]['model']}` | " +
                 " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "—" for c in classes) + " |")
    return L


def auto_findings(scored, oracle, field, classes):
    """Data-driven summary when a leaf has no hand-written findings: cliff + best model."""
    rows = [(SIZE.get(k, k), wobble_pct(scored[k], field),
             scored[k]["accuracy"]["accuracy_majority"] * 100) for k in _models(scored)]
    best = min(rows, key=lambda x: (x[1], -x[2]))
    hi = max(r[1] for r in rows); lo = min(r[1] for r in rows)
    L = ["## What this shows\n"]
    L.append(f"- **Wobble spread: {lo:.0f}%–{hi:.0f}% across the ladder.** "
             f"Lowest-wobble model: **{best[0]}** ({best[1]:.0f}% wobble, {best[2]:.0f}% accuracy).")
    if hi - lo >= 30:
        L.append("- **Wobble is a cliff, not a slope** — small models flip on a large share of items "
                 "while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.")
    return "\n".join(L)


PART_FINDINGS = """## What this shows

- **Wobble has a cliff, not a slope.** The 1B and 3B models flip their answer on 61-72% of items
  across 20 runs at temp 0.7 - unusable in a workflow that touches money. At 12B wobble collapses
  to 0%; the hosted model sits at 6%. The usable/unusable boundary is between 3B and 12B, not a
  smooth gradient. (N=5 hid this entirely - both mid/hosted models looked perfectly stable.)
- **A local 12B model beats a hosted frontier-cheap model here.** gemma4:12b: 0% wobble, 72%
  accuracy. deepseek-v4-flash: 6% wobble, 67%. Bigger-and-hosted is not automatically better.
- **Participating preferred is the universal blind spot.** Even the best models get only 1-2 of 5
  participating clauses right; the small models get 0. The "preference AND THEN also share with the
  common" structure is systematically misread as capped or non-participating.
- **Small models can't classify the hard classes at all** (1B: 0/5 participating, 0/5 capped) -
  they collapse everything to non-participating."""

SAFE_FINDINGS = """## What this shows

- **Accuracy does not imply trustworthiness — the cleanest case yet.** deepseek-v4-flash answers
  every one of the 16 SAFEs correctly (100% accuracy) yet still **wobbles on 19% of them** across 20
  identical runs. A model you would call "100% accurate" from a single pass changes its answer on
  ~1 in 5 items when you actually repeat the question. Wobble catches what an accuracy score hides.
- **A local 12B fully solves the binary task** (gemma4:12b: 0% wobble, 100% accuracy) - and again
  beats the hosted model on the trust axis, matching it on accuracy at zero egress.
- **Low wobble can mask low accuracy.** gemma3:1b looks stable (6% wobble) but is only 62% accurate -
  it confidently and *repeatably* gives the wrong pre/post classification. Consistency without
  accuracy is its own trap; this is why the two numbers are never averaged.
- **The 3B is the worst wobbler** (llama3.2: 56% wobble) despite 81% accuracy - the mid-size model
  is both more right and far less stable than the 1B, so wobble is not a smooth function of size."""

FINDINGS = {"participation_type": PART_FINDINGS, "safe_pre_post": SAFE_FINDINGS}


def render_leaf(cfg):
    field, classes, scored, oracle = load_leaf(cfg["slug"])
    labels = cfg["labels"]; total = len(oracle)
    counts = {c: sum(o[field] == c for o in oracle) for c in classes}
    bal = " / ".join(f"{counts[c]} {labels[c]}" for c in classes)
    L = [f"## {cfg['title']}\n"]
    L.append(f"**Corpus:** {total} {cfg['corpus_desc']}, human-validated answers ({bal}). "
             f"Each model run **{_runs_each(scored)}×/item at temp 0.7**.\n")
    L.append("### Headline — WOBBLE (the core metric)\n")
    L.append("*Wobble = % of items where the model gave more than one answer across its runs. "
             "A model that wobbles cannot be trusted in a money workflow even when it is often right.*\n")
    L += _wobble_table(scored, field)
    L.append("\n" + definitions(labels) + "\n")
    L.append("\n### Accuracy by class (majority vote)\n")
    L += _class_table(scored, oracle, field, classes, labels)
    L.append("\n### Which items make models wobble\n")
    L.append("| Item | True | Difficulty | Models that wobbled |")
    L.append("|---|---|---|---|")
    for i, o in enumerate(oracle):
        wob = [SIZE.get(k, k) for k in _models(scored)
               if scored[k]["accuracy"]["per_instance"][i]["fields"].get(field, {}).get("consistency", 1.0) < 1.0]
        if wob:
            L.append(f"| {o['company'][:22]} | {o[field]} | {o.get('difficulty','?')} | {', '.join(wob)} |")
    L.append("\n" + FINDINGS.get(cfg["slug"]) if cfg["slug"] in FINDINGS
             else "\n" + auto_findings(scored, oracle, field, classes))
    return "\n".join(L)


def readme_block_for(cfg):
    field, classes, scored, oracle = load_leaf(cfg["slug"])
    labels = cfg["labels"]; total = len(oracle)
    counts = {c: sum(o[field] == c for o in oracle) for c in classes}
    bal = " / ".join(f"{counts[c]} {labels[c]}" for c in classes)
    L = [f"**{cfg['title']}** — {total} clauses ({bal}), each model run {_runs_each(scored)}×/item:", ""]
    L.append("| Model | Size | **Wobble** ↓ | Consistency | Accuracy | " +
             " | ".join(labels[c] for c in classes) + " |")
    L.append("|---|---|---|---|---|" + "---|" * len(classes))
    for k in _models(scored):
        res = scored[k]; a = res["accuracy"]; r = res["reliability"]
        pc = per_class(a["per_instance"], oracle, field, classes)
        cells = " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "-" for c in classes)
        L.append(f"| `{res['model']}` | {SIZE.get(k,'?')} | **{wobble_pct(res,field):.0f}%** | "
                 f"{r['consistency_pct']:.0f}% | {a['accuracy_majority']*100:.0f}% | {cells} |")
    return "\n".join(L)


def _present_leaves():
    return [c for c in LEAVES if (ROOT / "leaves" / c["slug"] / "scored.json").exists()]


def main():
    present = _present_leaves()
    header = ("# Probity — Benchmark Results\n\n"
              "**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at "
              "temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a "
              "human-validated answer extracted from the source document. They are reported separately "
              "and never averaged — a model can be perfectly consistent and consistently wrong.\n\n"
              "Models span a size ladder (1B → 12B local + a hosted model) to test whether wobble "
              "falls as capability rises. Local via Ollama (zero egress); hosted = deepseek-v4-flash.\n\n---\n\n")
    body = "\n\n---\n\n".join(render_leaf(c) for c in present)
    (ROOT / "results" / "RESULTS.md").write_text(header + body + REPRO + "\n", encoding="utf-8")
    print(f"wrote results/RESULTS.md ({len(present)} leaves)")

    cap = (f"*{len(present)} test{'s' if len(present)!=1 else ''} so far. Each model run 20×/item at "
           "temp 0.7. **Wobble** = % of items answered inconsistently across runs. During build-out a "
           "leaf is run on the fast set (gemma3:1b + deepseek); the heavier rows (llama3.2 3B, "
           "gemma4:12b, and hosted frontier models) are filled in by one comprehensive sweep once "
           "every leaf exists, which is why newer leaves show fewer rows for now.*\n")
    tables = "\n\n".join(readme_block_for(c) for c in present)
    block = ("<!-- BENCHMARK:START -->\n" + cap + "\n" + tables + "\n\n" +
             definitions(present[0]["labels"], generic=True) + "\n<!-- BENCHMARK:END -->")
    readme = ROOT / "README.md"
    txt = re.sub(r"<!-- BENCHMARK:START.*?-->.*?<!-- BENCHMARK:END -->", lambda m: block,
                 readme.read_text(), flags=re.S)
    readme.write_text(txt, encoding="utf-8")
    print(f"injected {len(present)} benchmark tables into README.md")


REPRO = """

---

## Models and scope

Per leaf during the build-out, Probity runs the **fast set** (1B/3B/12B local via Ollama, zero
egress, plus deepseek-v4-flash) so a leaf costs minutes. The **heavy comprehensive run**
(qwen3.5:27b and hosted frontier models - Gemini, Haiku, etc. - at N=20+) is deferred to a single
sweep across all leaves once the full benchmark exists.

## Reproduce

```bash
cd leaves/<test_name>
python3 source.py          # fetch the real SEC documents
python3 run.py             # run the model ladder, N=20
python3 ../../results/render.py
```

Answers are human-validated from each document's own legal text (`leaves/<test>/oracle.jsonl`, with
the validating quote + difficulty per item). Genuinely ambiguous clauses are excluded, not guessed.
"""

if __name__ == "__main__":
    main()
