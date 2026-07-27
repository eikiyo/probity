"""
Location: engine/run_arm.py
Purpose: Run a whole temperature ARM one model at a time (Eikiyo 2026-07-27: "dont do 169K at one
         go. rather do 1 model at a time"), cheapest model first, with a HARD balance gate between
         models. Each model must finish 60/60 leaves at full coverage before the next one starts,
         and the real spend is measured from the provider's credits endpoint rather than estimated.
         Stops the whole arm on the first failure -- a sweep that half-ran must never be followed
         by another sweep spending more money on top of it.
Functions: ARM_ORDER, est_cost(), gate_balance(), run_one(), append_ledger(), main()
Calls: engine/run_hosted_sweep.py (subprocess), engine/coverage.py, engine/preflight.py, guard.py
Imports: argparse, json, subprocess, sys, time, pathlib
Run: python3 -u engine/run_arm.py --temperature 0.1 [--dry-run] [--from llama3.3-70b-or]
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ENGINE = Path(__file__).parent
sys.path.insert(0, str(ENGINE))

import coverage                 # noqa: E402
import guard as guard_mod       # noqa: E402
import preflight                # noqa: E402
from runner import N_RUNS       # noqa: E402

REPO = ENGINE.parent
LEDGER = REPO / "results" / "run_ledger.jsonl"

# Cheapest first. Rationale: a cheap model exercises the whole path -- client, prompts, checkpoint
# namespace, coverage assert -- for cents. If something is wrong with the arm's plumbing it surfaces
# on an $0.81 model instead of the $8.94 one.
ARM_ORDER = [
    ("llama3.3-70b-or",  "openrouter", "meta-llama/llama-3.3-70b-instruct"),
    ("deepseek-v4f",     "deepseek",   "deepseek-v4-flash"),
    ("gemma4-31b-or",    "openrouter", "google/gemma-4-31b-it"),
    ("haiku-4.5-direct", "anthropic",  "claude-haiku-4-5-20251001"),
    ("gpt5-mini-or",     "openrouter", "openai/gpt-5-mini"),
    ("deepseek-v4p",     "deepseek",   "deepseek-v4-pro"),
    ("mistral-large-or", "openrouter", "mistralai/mistral-large-2512"),
    ("gemini3-flash-or", "openrouter", "google/gemini-3-flash-preview"),
    ("minimax-m2.5-or",  "openrouter", "minimax/minimax-m2.5"),
]

# Keep this much OpenRouter credit unspent beyond the next model's estimate. A 402 lands mid-run
# with no clean resume marker, so stopping BEFORE a model is always cheaper than stopping during it.
BALANCE_BUFFER_USD = 1.00


def leaf_dirs():
    return sorted(d for d in (REPO / "leaves").iterdir()
                  if d.is_dir() and (d / "task.py").exists())


def calls_owed(label, temperature):
    """Calls this model still owes across the whole arm, read from the oracles and the checkpoints
    that exist right now -- so a resumed arm prices only what is left, never the full 9,400."""
    suffix = coverage.artifact_suffix(temperature)
    owed = 0
    for d in leaf_dirs():
        exp = coverage.expected_calls(d, N_RUNS)
        have = len(coverage.recorded_keys(coverage.checkpoint_path(d, label, suffix)))
        owed += max(0, exp - have)
    return owed


def est_cost(label, temperature):
    cost = guard_mod.per_call_cost(label)
    if cost is None:                      # `is None`, not `or`: 0.0 is a REAL price for local
        cost = guard_mod._UNKNOWN_MODEL_COST_USD
    return calls_owed(label, temperature) * cost


def gate_balance(label, client, temperature):
    """Fail closed BEFORE spending. Returns (ok, message). Only OpenRouter exposes a balance we
    can read; for the direct APIs we say so plainly rather than implying we checked."""
    need = est_cost(label, temperature)
    if client != "openrouter":
        return True, f"{client} direct API -- no readable balance, est ${need:.2f}"
    bal = preflight.or_balance()
    if bal is None:
        return False, "could not read the OpenRouter balance -- refusing to spend blind"
    if bal < need + BALANCE_BUFFER_USD:
        return False, (f"balance ${bal:.2f} < est ${need:.2f} + ${BALANCE_BUFFER_USD:.2f} buffer "
                        f"-- top up before running {label}")
    return True, f"balance ${bal:.2f}, est ${need:.2f}"


def coverage_of(label, temperature):
    matrix = coverage.coverage_matrix(leaf_dirs(), [label], N_RUNS,
                                       coverage.artifact_suffix(temperature))
    return (sum(c["recorded"] for c in matrix), sum(c["expected"] for c in matrix),
            [c for c in matrix if not c["complete"]])


def run_one(label, client, model_id, temperature, parallel, workers):
    """One model, all 60 leaves. Returns a ledger row describing what ACTUALLY happened."""
    before = preflight.or_balance() if client == "openrouter" else None
    t0 = time.time()
    cmd = [sys.executable, "-u", str(ENGINE / "run_hosted_sweep.py"),
           "--label", label, "--model", model_id, "--client", client,
           "--temperature", str(temperature),
           "--leaf-parallelism", str(parallel), "--workers-per-leaf", str(workers)]
    proc = subprocess.run(cmd, cwd=str(REPO))
    after = preflight.or_balance() if client == "openrouter" else None
    recorded, owed, holes = coverage_of(label, temperature)
    return {"label": label, "client": client, "model_id": model_id, "temperature": temperature,
            "exit_code": proc.returncode, "seconds": round(time.time() - t0, 1),
            "recorded": recorded, "owed": owed, "holes": len(holes),
            "complete": recorded == owed and proc.returncode == 0,
            "balance_before": before, "balance_after": after,
            "measured_spend_usd": (round(before - after, 4)
                                    if before is not None and after is not None else None)}


def append_ledger(row):
    """Append-only. RUN_LOG.md regenerates from this file, so no spend figure is ever hand-typed."""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def adopt(label, client, model_id, temperature, balance_before):
    """
    Write a ledger row for a model that ran OUTSIDE this driver (gpt-oss-120b-or was launched
    directly from run_hosted_sweep.py before the ledger existed).

    The before-balance cannot be sampled retroactively, so it is supplied by the operator and the
    row is stamped `provenance: "reconstructed"`. RUN_LOG renders those rows with a footnote
    saying the figure was not machine-sampled. This is the honest option: the alternative is
    either omitting a real cost or printing an operator-typed number as if the harness measured
    it, and a spend table that cannot tell those apart is not an audit trail.
    """
    after = preflight.or_balance() if client == "openrouter" else None
    recorded, owed, holes = coverage_of(label, temperature)
    row = {"label": label, "client": client, "model_id": model_id, "temperature": temperature,
           "exit_code": 0 if recorded == owed else 1, "seconds": None,
           "recorded": recorded, "owed": owed, "holes": len(holes),
           "complete": recorded == owed, "balance_before": balance_before,
           "balance_after": after, "provenance": "reconstructed",
           "measured_spend_usd": (round(balance_before - after, 4)
                                   if balance_before is not None and after is not None else None)}
    append_ledger(row)
    return row


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--temperature", type=float, required=True)
    p.add_argument("--adopt", default=None,
                    help="write a reconstructed ledger row for a label that ran outside this "
                         "driver; requires --balance-before. Makes NO model calls.")
    p.add_argument("--balance-before", type=float, default=None,
                    help="the operator-observed provider balance before the adopted run")
    p.add_argument("--from", dest="start", default=None, help="resume the arm at this label")
    p.add_argument("--only", action="append", dest="only", help="run only these labels")
    p.add_argument("--leaf-parallelism", type=int, default=10)
    p.add_argument("--workers-per-leaf", type=int, default=4)
    p.add_argument("--dry-run", action="store_true", help="print the plan, make ZERO calls")
    args = p.parse_args()

    if args.adopt:
        known = {l: (c, m) for l, c, m in preflight.LINEUP}
        if args.adopt not in known:
            raise SystemExit(f"--adopt {args.adopt!r} is not a known label")
        if args.balance_before is None:
            raise SystemExit("--adopt requires --balance-before (the observed pre-run balance)")
        client, model_id = known[args.adopt]
        row = adopt(args.adopt, client, model_id, args.temperature, args.balance_before)
        print(f"adopted {args.adopt}: {row['recorded']}/{row['owed']} calls, "
              f"spend {row['measured_spend_usd']} (provenance: reconstructed)")
        return

    order = list(ARM_ORDER)
    if args.start:
        names = [l for l, _, _ in order]
        if args.start not in names:
            raise SystemExit(f"--from {args.start!r} is not in ARM_ORDER")
        order = order[names.index(args.start):]
    if args.only:
        order = [r for r in order if r[0] in set(args.only)]

    print(f"=== ARM temp={args.temperature}: {len(order)} models, one at a time ===")
    total = 0.0
    for label, client, _mid in order:
        owed = calls_owed(label, args.temperature)
        cost = est_cost(label, args.temperature)
        total += cost
        print(f"  {label:20s} {client:11s} {owed:6d} calls   est ${cost:6.2f}")
    print(f"  {'TOTAL':20s} {'':11s} {'':6s}   est ${total:6.2f}")
    bal = preflight.or_balance()
    print(f"  OpenRouter balance: ${bal:.2f}" if bal is not None else "  OpenRouter balance: ?")
    if args.dry_run:
        print("\n--dry-run: no calls made.")
        return

    for i, (label, client, model_id) in enumerate(order, 1):
        if calls_owed(label, args.temperature) == 0:
            print(f"\n[{i}/{len(order)}] {label}: already complete, skipping (0 calls owed)")
            continue
        ok, msg = gate_balance(label, client, args.temperature)
        print(f"\n[{i}/{len(order)}] {label} -- {msg}", flush=True)
        if not ok:
            print(f"ABORTING ARM before {label}: {msg}")
            sys.exit(2)
        row = run_one(label, client, model_id, args.temperature,
                      args.leaf_parallelism, args.workers_per_leaf)
        append_ledger(row)
        spend = row["measured_spend_usd"]
        print(f"[{i}/{len(order)}] {label}: {row['recorded']}/{row['owed']} calls, "
              f"{row['holes']} holes, exit {row['exit_code']}, {row['seconds']}s, "
              f"spend {('$%.4f' % spend) if spend is not None else 'n/a (direct API)'}", flush=True)
        # Fail closed: never start the NEXT model's spend on top of a model that did not finish.
        if not row["complete"]:
            print(f"ABORTING ARM: {label} did not reach full coverage. Re-run it "
                  f"(it resumes per cell) before continuing.")
            sys.exit(1)
    print(f"\n=== ARM temp={args.temperature} complete: {len(order)} models at full coverage ===")


if __name__ == "__main__":
    main()
