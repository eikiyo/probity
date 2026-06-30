"""
Location: results/render.py
Purpose: Render the living benchmark table (RESULTS.md) from a leaf's scored.json + oracle.jsonl.
         Reports ACCURACY and RELIABILITY separately, per-class accuracy, the majority-class
         baseline, and a hard-item spotlight. Never averages accuracy and reliability.
Functions: per_class(), render_leaf(), main()
Calls: (none) Imports: json, pathlib
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEAF = ROOT / "leaves" / "participation_type"
CLASSES = ["non-participating", "participating", "capped"]


def per_class(per_instance, oracle):
    """Accuracy within each true class: {class: (correct, total)}."""
    out = {c: [0, 0] for c in CLASSES}
    for row, o in zip(per_instance, oracle):
        c = o["participation_type"]
        if row["n_valid"] == 0:
            continue
        out[c][1] += 1
        out[c][0] += int(row["majority_correct"])
    return out


def render_leaf(scored, oracle):
    lines = []
    counts = {c: sum(o["participation_type"] == c for o in oracle) for c in CLASSES}
    total = len(oracle)
    base = max(counts.values()) / total * 100
    lines.append("## Test 1.3.2 — Preferred-stock liquidation participation\n")
    lines.append(f"**Corpus:** {total} real SEC-filed charter clauses, human-validated answers "
                 f"({counts['non-participating']} non-participating / {counts['participating']} "
                 f"participating / {counts['capped']} capped). "
                 f"Majority-class baseline (always guess non-participating) = **{base:.0f}%**.\n")
    lines.append("### Headline (accuracy vs validated answer · reliability = run-to-run consistency)\n")
    lines.append("| Model | Accuracy (majority vote) | Accuracy (strict, all 5 runs) | Reliability | Measurable |")
    lines.append("|---|---|---|---|---|")
    for label, res in scored.items():
        a, r = res["accuracy"], res["reliability"]
        lines.append(f"| `{res['model']}` | **{a['accuracy_majority']*100:.0f}%** | "
                     f"{a['accuracy_strict']*100:.0f}% | {r['consistency_pct']:.0f}% | "
                     f"{a['n_measurable']}/{a['n_instances']} |")
    lines.append("\n### Accuracy by class\n")
    lines.append("| Model | non-participating | participating | capped |")
    lines.append("|---|---|---|---|")
    for label, res in scored.items():
        pc = per_class(res["accuracy"]["per_instance"], oracle)
        cells = " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "—" for c in CLASSES)
        lines.append(f"| `{res['model']}` | {cells} |")
    lines.append("\n### Hard-item spotlight (the traps)\n")
    hard = [(i, o) for i, o in enumerate(oracle) if o["difficulty"] == "hard"]
    lines.append("| Item | True | " + " | ".join(f"`{res['model']}`" for res in scored.values()) + " |")
    lines.append("|---|---|" + "---|" * len(scored))
    for i, o in hard:
        cells = []
        for res in scored.values():
            row = res["accuracy"]["per_instance"][i]
            maj = row["fields"].get("participation_type", {}).get("majority")
            cells.append(f"{'✓' if row['majority_correct'] else '✗'} ({maj})")
        lines.append(f"| {o['company'][:22]} | {o['participation_type']} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    scored = json.loads((LEAF / "scored.json").read_text())
    oracle = [json.loads(l) for l in open(LEAF / "oracle.jsonl") if l.strip()]
    header = ("# Probity — Benchmark Results\n\n"
              "Accuracy = % correct vs a human-validated answer extracted from the source document. "
              "Reliability = % run-to-run agreement at temperature 0.7 (label-free). "
              "They are reported separately and never averaged.\n\n"
              "Primary runners: **gemma4:12b** (local, zero egress) and **deepseek-v4-flash**. "
              "Frontier models are sampled occasionally, not on every leaf.\n\n---\n\n")
    (ROOT / "results" / "RESULTS.md").write_text(header + render_leaf(scored, oracle) + FOOTER + "\n", encoding="utf-8")
    print("wrote results/RESULTS.md")




FOOTER = """

---

## What this round shows

- **Reliability is not accuracy — demonstrated on real data.** Both models answered identically
  across all 5 runs of every item (100% reliability) yet were wrong on 4 of 13 (69% accuracy).
  A model you can trust to be *consistent* is not a model you can trust to be *right*.
- **A 12B local model tied a frontier-class hosted model, exactly.** `gemma4:12b` and
  `deepseek-v4-flash` produced the same label on all 65 runs. Verified genuine (not a duplication
  bug): on a live re-run gemma emits ```json-fenced output and DeepSeek emits raw JSON — different
  models, same answers.
- **Shared blind spot = participating preferred.** Both got only 1/3 participating clauses right,
  misreading the "preference THEN also share with common" structure as *capped*.
- **A naming trap fooled both.** Pfenex's "Maximum Participation Amount" lured both models to
  *capped*, though its greater-of structure is non-participating.
- **A clean greater-of was misread.** Zoom's textbook non-participating clause was called
  *participating* by both models.

The errors are systematic and shared across two very different models — evidence of a common
misconception about preferred-stock liquidation, not random sampling noise. This is exactly the
reliable-but-wrong failure a finance agent would propagate silently.

## Reproduce

```bash
cd leaves/participation_type
python3 source.py     # re-fetch the real SEC charter clauses
python3 run.py        # run gemma + DeepSeek, score
python3 ../../results/render.py
```

Corpus: real SEC EDGAR charter exhibits; answers human-validated from each clause's own legal text
(see `leaves/participation_type/oracle.jsonl`, with the validating quote per item).
"""


if __name__ == "__main__":
    main()
