"""
Location: results/summary.py
Purpose: The ONE place a model or a document-category is given a display name, and the ONE place
         the two aggregate summary tables (per-model, per-category) are built. Extracted from
         results/render.py 2026-07-27: render.py had grown to 695 LOC against a 300 budget, and its
         display maps were a second copy of the ones in results/compare.py -- a rule-of-two
         violation that would let the README and the paired temperature report disagree about what
         a model is called. Every table here takes the ARM (temperature) as a parameter, so no
         caller can render one arm's numbers under another arm's caption.
Functions: display_name(), display_size(), badge(), aggregate_by_model(), aggregate_by_family(),
           suite_summary_table(), family_summary_table()
Calls: results/aggregate.py (the single reduction)
Imports: sys, pathlib
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

import aggregate as ag  # noqa: E402

FAMILY_DISPLAY = {
    "priced_equity": "Priced equity rounds",
    "convertibles": "SAFEs & convertible notes",
    "cap_table": "Cap table math",
    "exit_waterfall": "Exit waterfalls",
    "rights_governance": "Investor rights & governance",
    "founder_equity": "Founder & employee vesting",
    "regulatory": "Regulatory disclosures",
    "risk_flag": "Off-market risk flags",
}

# label -> (public model name, size/routing blurb). The label is the guard/checkpoint label from
# engine/runner.openrouter_model_set(), NOT the raw provider model id.
MODEL_DISPLAY = {
    "gemma3-1b": ("gemma3:1b", "1B, local"),
    "gemma3-1b-qat": ("gemma3:1b-it-qat", "1B QAT, local"),
    "qwen3.5-27b": ("qwen3.5:27b", "27B, local"),
    "deepseek-v4f": ("deepseek-v4-flash", "hosted, direct"),
    "gemma4-31b-or": ("gemma-4-31b-it", "31B, hosted (OR)"),
    "mistral-large-or": ("mistral-large-2512", "hosted (OR)"),
    "minimax-m2.5-or": ("minimax-m2.5", "hosted (OR)"),
    "llama3.3-70b-or": ("llama-3.3-70b", "70B, hosted (OR)"),
    "gemini3-flash-or": ("gemini-3-flash", "hosted (OR)"),
    "gpt-oss-120b-or": ("gpt-oss-120b", "120B, hosted (OR)"),
    "gpt5-mini-or": ("gpt-5-mini", "hosted (OR)"),
    "haiku-4.5-direct": ("claude-haiku-4.5", "hosted, direct API"),
}


def rel(path: Path) -> str:
    """Repo-relative when possible, absolute otherwise. `Path.relative_to` RAISES on a path
    outside the repo, so printing a result with it crashed AFTER the file was already written --
    a completed render reported as a failure, which misleads exactly as much as the reverse."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def display_name(label: str) -> str:
    return MODEL_DISPLAY.get(label, (label, "?"))[0]


def display_size(label: str) -> str:
    return MODEL_DISPLAY.get(label, (label, "?"))[1]


def _rate(num: int, den: int) -> Optional[float]:
    """A rate, or None when there is nothing to divide. None means UNMEASURED and must render as
    an em-dash -- never as 0%, which reads as a confident 'perfect' from no data."""
    return 100 * num / den if den else None


def badge(pct: Optional[float], lower_is_better: bool) -> str:
    """A colored shields.io pill for a percentage -- green/yellow/red by threshold."""
    if pct is None:
        return "—"
    if lower_is_better:
        color = "brightgreen" if pct < 10 else "yellow" if pct < 30 else "red"
    else:
        color = "brightgreen" if pct > 85 else "yellow" if pct > 60 else "red"
    return f"![{pct:.0f}%](https://img.shields.io/badge/-{pct:.0f}%25-{color})"


def aggregate_by_model(arm: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Per-model wobble + accuracy for one arm, in declared lineup order.

    Two behaviours are load-bearing and were both fixed when this moved out of render.py:
      * LINEUP, not a heuristic. The old filter was "a model counts if it ran >= 10 leaves". The
        fine-tune lab has since written 43 more labels into the same scored.json files and several
        clear 10 leaves, so re-rendering emitted a 29-ROW table mixing training experiments into
        the published result. A lineup is an editorial decision, so it is declared.
      * The denominator is what was MEASURED. The old weight was n_instances (every oracle item),
        so an item with zero valid runs counted as non-flipping -- biasing wobble DOWNWARD, the one
        direction this benchmark must never be biased in.
    """
    counts = ag.model_counts(arm)
    out = []
    for model in ag.canonical_lineup():
        c = counts.get(model)
        if not c:
            continue
        out.append({"model": model, "leaves": c["leaves"], "n_items": c["measured"],
                     "wobble": _rate(c["flipped"], c["measured"]),
                     "accuracy": _rate(c["correct"], c["measurable"])})
    return out


def aggregate_by_family(arm: Optional[float] = None) -> List[Dict[str, Any]]:
    """Per-category wobble + accuracy, averaged ACROSS EVERY MODEL in the lineup rather than
    pinned to one (Eikiyo, 2026-07-03: "why cant this be average of all models?"). `leaves` counts
    DISTINCT test leaves, not leaf*model combinations, so the Tests column keeps its meaning."""
    counts = ag.family_counts(arm)
    return [{"family": fam, "leaves": c["leaves"],
             "wobble": _rate(c["flipped"], c["measured"]),
             "accuracy": _rate(c["correct"], c["measurable"])}
            for fam, c in sorted(counts.items(), key=lambda kv: -kv[1]["leaves"])]


def suite_summary_table(arm: Optional[float] = None) -> str:
    """THE headline table: does wobble fall as model capability rises?"""
    lines = ["| Model | Size | Tests covered | **Wobble** ↓ | Accuracy |", "|---|---|---|---|---|"]
    for r in aggregate_by_model(arm):
        lines.append(f"| `{display_name(r['model'])}` | {display_size(r['model'])} | "
                      f"{r['leaves']} | {badge(r['wobble'], True)} | "
                      f"{badge(r['accuracy'], False)} |")
    return "\n".join(lines)


def family_summary_table(arm: Optional[float] = None) -> str:
    """One row per fundraising-document category, averaged across every model in the lineup."""
    lines = ["| Category | Tests | **Wobble** ↓ (all models) | Accuracy (all models) |",
             "|---|---|---|---|"]
    for r in aggregate_by_family(arm):
        lines.append(f"| {FAMILY_DISPLAY.get(r['family'], r['family'])} | {r['leaves']} | "
                      f"{badge(r['wobble'], True)} | {badge(r['accuracy'], False)} |")
    return "\n".join(lines)


def readme_block(n_leaves: int, temp: float, arm: Optional[float] = None) -> str:
    """The README's BENCHMARK block: a caption plus the two tables above. Lives here, beside the
    tables it is made of, so the caption's temperature can never drift from the data's."""
    cap = (f"*{n_leaves} tests, each item run 20x/item at temp {temp} across a model size ladder. "
           "**Wobble** (lower = better) is the run-to-run inconsistency rate, weighted by item "
           "count across every test that model ran. Full per-test breakdown (all "
           f"{n_leaves} tables): [`results/RESULTS.md`](results/RESULTS.md).*\n")
    return ("<!-- BENCHMARK:START -->\n" + cap +
            "\n### Does reliability improve with model size?\n\n" + suite_summary_table(arm) +
            "\n\n### By fundraising-document category\n\n" + family_summary_table(arm) +
            "\n\n<!-- BENCHMARK:END -->")


def inject_readme(n_leaves: int, temp: float, arm: Optional[float] = None) -> None:
    """Rewrite the README's BENCHMARK block in place. Callers must gate this on the PUBLISHED arm:
    the markers carry no arm identity, so writing a second arm here would silently replace the
    baseline half of the comparison with the new half."""
    import re
    block = readme_block(n_leaves, temp, arm)
    readme = ROOT / "README.md"
    txt = re.sub(r"<!-- BENCHMARK:START.*?-->.*?<!-- BENCHMARK:END -->", lambda m: block,
                 readme.read_text(), flags=re.S)
    readme.write_text(txt, encoding="utf-8")
    print("injected 2 summary tables (suite + by-category) into README.md")
