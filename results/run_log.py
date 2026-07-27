"""
Location: results/run_log.py
Purpose: Generate RUN_LOG.md for one arm ENTIRELY from disk -- calls made, failures, duplicate
         records, wall-clock and the MEASURED dollar spend read from the provider's credits
         endpoint before/after each model (results/run_ledger.jsonl, written by engine/run_arm.py).
         No figure here is hand-typed; re-running this regenerates every number. Where something
         genuinely is not recorded (per-call HTTP retries), it says so instead of printing a zero
         that would read as "we retried nothing".
Functions: call_stats(), ledger_for(), fmt_hms(), stats_table(), spend_table(), build_log(), main()
Calls: engine/coverage.py, results/aggregate.py
Imports: argparse, json, sys, pathlib
Run: python3 results/run_log.py --temperature 0.1 --out results/RUN_LOG.md
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "engine"))

import aggregate as ag   # noqa: E402
import summary           # noqa: E402
import coverage          # noqa: E402

LEDGER = HERE / "run_ledger.jsonl"
N_RUNS = 20


def call_stats(label: str, temperature: Optional[float]) -> Dict[str, int]:
    """
    Count what the checkpoints actually hold for one model across the whole arm.

    `records` is raw lines; `distinct` dedups by (instance, run). They differ when a cell was
    resumed and re-appended a key it already had -- reporting only `records` would overstate the
    work done, and reporting only `distinct` would hide that a resume happened at all.
    """
    suffix = coverage.artifact_suffix(temperature)
    out = {"records": 0, "distinct": 0, "errors": 0, "unparsed": 0, "expected": 0}
    for l in ag.built_leaves():
        leaf = ROOT / l["leaf"]
        out["expected"] += coverage.expected_calls(leaf, N_RUNS)
        path = coverage.checkpoint_path(leaf, label, suffix)
        if not path.exists():
            continue
        out["distinct"] += len(coverage.recorded_keys(path))
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                out["records"] += 1
                if rec.get("error"):
                    out["errors"] += 1
                if rec.get("parsed") is None:
                    out["unparsed"] += 1
    out["duplicates"] = out["records"] - out["distinct"]
    out["short_by"] = out["expected"] - out["distinct"]
    return out


def ledger_for(temperature: Optional[float]) -> List[Dict[str, Any]]:
    """Ledger rows for this arm, LAST write wins per label -- a model re-run to fill holes appends
    a second row, and the current truth is the latest one, not the sum."""
    if not LEDGER.exists():
        return []
    rows: Dict[str, Dict[str, Any]] = {}
    seconds: Dict[str, float] = {}
    spend: Dict[str, float] = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("temperature") != temperature:
            continue
        label = r["label"]
        rows[label] = r
        # wall-clock and spend ACCUMULATE across re-runs; coverage does not.
        seconds[label] = seconds.get(label, 0.0) + (r.get("seconds") or 0.0)
        if r.get("measured_spend_usd") is not None:
            spend[label] = spend.get(label, 0.0) + r["measured_spend_usd"]
    for label, r in rows.items():
        r["total_seconds"] = round(seconds[label], 1)
        r["total_spend_usd"] = round(spend[label], 4) if label in spend else None
        r["runs"] = sum(1 for line in LEDGER.read_text(encoding="utf-8").splitlines()
                        if line.strip() and json.loads(line).get("label") == label
                        and json.loads(line).get("temperature") == temperature)
    return list(rows.values())


def fmt_hms(seconds: Optional[float]) -> str:
    if not seconds:
        return "—"
    s = int(seconds)
    return f"{s // 3600}h {(s % 3600) // 60}m" if s >= 3600 else f"{s // 60}m {s % 60}s"


def stats_table(temperature: Optional[float], labels: List[str]) -> str:
    lines = ["| Model | Calls owed | Recorded | Short | Duplicate records | Errors | Unparsed |",
             "|---|---|---|---|---|---|---|"]
    tot = {k: 0 for k in ("expected", "distinct", "short_by", "duplicates", "errors", "unparsed")}
    for label in labels:
        s = call_stats(label, temperature)
        if s["distinct"] == 0:
            continue
        for k in tot:
            tot[k] += s[k]
        short = "—" if s["short_by"] == 0 else f"**{s['short_by']}**"
        lines.append(f"| `{label}` | {s['expected']} | {s['distinct']} | {short} | "
                      f"{s['duplicates']} | {s['errors']} | {s['unparsed']} |")
    lines.append(f"| **TOTAL** | **{tot['expected']}** | **{tot['distinct']}** | "
                  f"**{tot['short_by'] or '—'}** | {tot['duplicates']} | {tot['errors']} | "
                  f"{tot['unparsed']} |")
    return "\n".join(lines)


def spend_table(temperature: Optional[float]) -> str:
    rows = ledger_for(temperature)
    if not rows:
        return ("*No ledger rows for this arm. `results/run_ledger.jsonl` is written by "
                "`engine/run_arm.py`; a model launched directly via `run_hosted_sweep.py` records "
                "no spend row, so its cost is not measured here.*")
    lines = ["| Model | Routing | Wall-clock | Exit | Measured spend | Sweep runs |",
             "|---|---|---|---|---|---|"]
    total = 0.0
    unmeasured, reconstructed = [], []
    for r in sorted(rows, key=lambda x: x["label"]):
        spend = r.get("total_spend_usd")
        if spend is None:
            unmeasured.append(r["label"])
            cell = "n/a *(direct API — no readable balance)*"
        else:
            total += spend
            cell = f"${spend:.4f}"
            # A reconstructed row's pre-run balance was typed by the operator, not sampled by the
            # harness. Marking it is the whole point: a spend table that cannot distinguish a
            # measured figure from a remembered one is not an audit trail.
            if r.get("provenance") == "reconstructed":
                reconstructed.append(r["label"])
                cell += " †"
        lines.append(f"| `{r['label']}` | {r['client']} | {fmt_hms(r.get('total_seconds'))} | "
                      f"{r['exit_code']} | {cell} | {r.get('runs', 1)} |")
    lines.append(f"| **TOTAL (measured)** | | | | **${total:.2f}** | |")
    if reconstructed:
        lines += ["", f"† Pre-run balance for {', '.join('`' + x + '`' for x in reconstructed)} "
                       "was recorded by the operator rather than sampled by the harness (the model "
                       "was launched before the ledger existed). The post-run balance IS a live "
                       "reading, so the delta is accurate to the accuracy of that one figure."]
    if unmeasured:
        lines += ["", f"*{len(unmeasured)} model(s) ran on a direct provider API with no readable "
                       f"balance endpoint ({', '.join('`' + u + '`' for u in unmeasured)}), so "
                       "their spend is absent from the total rather than estimated into it.*"]
    return "\n".join(lines)


def build_log(temperature: Optional[float]) -> str:
    labels = ag.canonical_lineup()
    arm = coverage.arm_tag(temperature) if temperature is not None else "legacy (0.7)"
    return "\n".join([
        f"# Probity — run log, arm {arm}", "",
        "Every number on this page is read from disk by `results/run_log.py`: call counts and "
        "errors from the per-cell checkpoint files, spend from the provider credit balance "
        "sampled before and after each model. Nothing here is hand-entered.", "",
        "## Calls", "", stats_table(temperature, labels), "",
        "**Calls owed** is items × 20 read from each leaf's `oracle.jsonl` — the spec, never a "
        "count derived from the recorded data. **Duplicate records** are re-appended "
        "(instance, run) keys from a resumed cell; they are counted once toward coverage. "
        "**Errors** are records carrying a provider/network error; **Unparsed** are calls that "
        "returned text no parser could read. Both are retained in the checkpoint, not discarded.", "",
        "## Spend and wall-clock", "", spend_table(temperature), "",
        "## What is NOT measured here", "",
        "- **Per-call HTTP retries.** `models._post_with_retry` retries transient failures in "
        "process and does not persist an attempt counter, so a retry that eventually succeeded "
        "leaves no trace. The retried calls ARE included in the measured spend (the balance "
        "delta captures every billed attempt); they are simply not separately countable. A zero "
        "is not printed for them, because that would read as \"nothing was retried\".",
        "- **Direct-API spend.** Anthropic and DeepSeek expose no balance endpoint this harness "
        "reads, so those models' costs are excluded from the measured total rather than "
        "estimated into it.", ""])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    text = build_log(args.temperature)
    tag = "" if args.temperature is None else f"_{coverage.arm_tag(args.temperature).upper()}"
    out = Path(args.out) if args.out else HERE / f"RUN_LOG{tag}.md"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {summary.rel(out)} ({len(text.splitlines())} lines)")
