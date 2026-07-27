"""
Location: engine/run_hosted_sweep.py
Purpose: Run ONE hosted OpenRouter model across ALL 60 leaves, with TWO levels of parallelism:
         across leaves (multiple leaves' harness runs in flight at once) AND within a leaf
         (multiple calls for the same leaf, via engine/harness.py's max_workers). Needed because
         leaf sizes vary 20x (1 item to 19 items x 20 runs = 20-380 calls) -- a slow model
         sitting idle between leaves wastes wall-clock that leaf-level concurrency reclaims
         (Eikiyo 2026-07-02: "gemma is fast, others are slow. the slow ones will take a long
         time... try at least 10 parallel leaves"). Zero-touch on the 60 per-leaf run.py shims.
Concurrency budget: OpenRouter publishes no fixed concurrent-request cap for paid/PAYG keys (its
         docs only detail free-tier RPM/daily caps; this account's own /api/v1/auth/key response
         confirms `limit: null`, i.e. no account-level ceiling). The one documented mechanism
         that CAN reject a burst is Cloudflare's DDoS protection sitting in front of the API,
         and community reports put the safe unmanaged-account concurrency around ~50 in-flight
         requests before that kicks in. total_concurrency (leaf_parallelism * workers_per_leaf)
         defaults to 10 * 4 = 40 -- comfortably under that informal ceiling, not a documented
         guarantee. If this account is later confirmed to have a different real limit, adjust
         --leaf-parallelism / --workers-per-leaf, not this comment.
Functions: main()
Calls: runner.run_leaf, runner.openrouter_model_set
Imports: sys, argparse, pathlib, concurrent.futures, runner
Run: python3 engine/run_hosted_sweep.py --label gemma4-31b-or --model google/gemma-4-31b-it \
         --leaf-parallelism 10 --workers-per-leaf 4
"""
import sys
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ENGINE = Path(__file__).parent
sys.path.insert(0, str(ENGINE))

from runner import (run_leaf, openrouter_model_set, anthropic_model_set,   # noqa: E402
                     deepseek_model_set, N_RUNS)
import coverage                                                          # noqa: E402
import guard as guard_mod                                                # noqa: E402

REPO = ENGINE.parent
LEAVES_DIR = REPO / "leaves"

# Per-leaf caps are now DERIVED per leaf by guard.caps_for_leaf() from the work that leaf actually
# owes (items x n_runs x that model's real per-call cost x margin), rather than being flat.
#
# WHY THE FLAT DEFAULTS ARE GONE (2026-07-27): the old flat $0.20 cap did not scale with leaf size,
# so on the biggest leaves it fired MID-RUN and silently truncated 5 cells of the 0.7 sweep --
# gemini stopped at 333 calls of 380, haiku at 199 of 320. Those cells then scored fewer than 20
# runs on their last items, and since an item with no runs can never be counted as flipping, the
# missing data biased wobble DOWNWARD. A cap that scales with nothing cannot be right on a suite
# whose leaves vary 19x in size. Passing --max-cost-per-leaf still forces a flat cap for debugging,
# but the DEFAULT is now per-leaf derivation.
DEFAULT_MAX_STEPS_PER_LEAF = None
DEFAULT_MAX_COST_PER_LEAF = None

# Soft warn threshold, not a hard block -- see module docstring's Concurrency budget note.
SOFT_CONCURRENCY_WARN = 50


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--label", required=True, help="model_label for guard/checkpoint/scorecard, "
                    "e.g. gemma4-31b-or (must match a guard.ESTIMATED_COST_PER_CALL_USD entry "
                    "or it fails closed to the most-expensive-known default)")
    p.add_argument("--model", required=True, help="OpenRouter model id, e.g. google/gemma-4-31b-it")
    p.add_argument("--client", choices=["openrouter", "anthropic", "deepseek"],
                    default="openrouter",
                    help="which provider backs --label/--model (anthropic and deepseek are the"
                    " DIRECT provider APIs, Sec 0.10 override, see models.AnthropicClient)")
    p.add_argument("--leaf-parallelism", type=int, default=10,
                    help="how many leaves run their harness concurrently")
    p.add_argument("--workers-per-leaf", type=int, default=4,
                    help="max_workers passed into each leaf's own harness run")
    p.add_argument("--max-steps-per-leaf", type=int, default=DEFAULT_MAX_STEPS_PER_LEAF,
                    help="force a FLAT step cap on every leaf (default: derived per leaf)")
    p.add_argument("--max-cost-per-leaf", type=float, default=DEFAULT_MAX_COST_PER_LEAF,
                    help="force a FLAT cost cap on every leaf (default: derived per leaf from "
                         "items x n_runs x real per-call cost -- see guard.caps_for_leaf)")
    p.add_argument("--only-leaf", default=None, help="run a single leaf by name (debugging)")
    p.add_argument("--temperature", type=float, default=None,
                    help="sampling temperature AND arm namespace. 0.1 writes scored_t01.json / "
                         "runs_t01_<label>.jsonl; 0.7 writes the t07 arm. Omitting it runs the "
                         "LEGACY unsuffixed arm at the module default, which is what produced the "
                         "published 2026-07-03 baseline -- pass it explicitly for any new arm so "
                         "an existing arm can never be overwritten.")
    p.add_argument("--dry-run", action="store_true",
                    help="resolve every leaf, compute caps and the full call/cost plan, print it, "
                         "and make ZERO model calls")
    args = p.parse_args()

    total_concurrency = args.leaf_parallelism * args.workers_per_leaf
    if total_concurrency > SOFT_CONCURRENCY_WARN:
        print(f"WARN: leaf_parallelism({args.leaf_parallelism}) x workers_per_leaf"
              f"({args.workers_per_leaf}) = {total_concurrency} concurrent calls, above the "
              f"informal ~{SOFT_CONCURRENCY_WARN}-request OpenRouter/Cloudflare ceiling (see "
              f"module docstring) -- proceeding, but expect possible 429s.", flush=True)

    model_set = {"anthropic": anthropic_model_set,
                 "deepseek": deepseek_model_set,
                 "openrouter": openrouter_model_set}[args.client](args.label, args.model)
    # None => run_leaf derives caps per leaf. Only an explicitly-passed flat cap overrides that.
    guard_config = None
    if args.max_steps_per_leaf is not None or args.max_cost_per_leaf is not None:
        guard_config = {"max_steps": args.max_steps_per_leaf,
                        "max_cost_usd": args.max_cost_per_leaf}
        print("WARN: a FLAT per-leaf cap was passed explicitly, overriding per-leaf derivation. "
              "This is the configuration that truncated 5 cells of the 0.7 sweep.", flush=True)

    leaves = sorted(d.name for d in LEAVES_DIR.iterdir() if d.is_dir() and (d / "task.py").exists())
    if args.only_leaf:
        leaves = [l for l in leaves if l == args.only_leaf]
        if not leaves:
            print(f"error: no such leaf '{args.only_leaf}'", file=sys.stderr)
            sys.exit(1)

    if args.dry_run:
        print(plan_report(args.label, args.model, leaves, args.temperature, guard_config))
        return

    print(f"=== hosted sweep: {args.label} ({args.model}) across {len(leaves)} leaves at "
          f"temp={args.temperature} -- {args.leaf_parallelism} leaves concurrently x "
          f"{args.workers_per_leaf} workers/leaf ({total_concurrency} total in-flight) -- "
          f"per-leaf caps {'FLAT ' + str(guard_config) if guard_config else 'derived per leaf'} "
          f"===\n", flush=True)

    print_lock = threading.Lock()
    done_count = [0]
    errors = []

    def _run_one(leaf_name):
        leaf_dir = LEAVES_DIR / leaf_name
        try:
            run_leaf(leaf_dir, model_set=model_set, guard_config=guard_config,
                     max_workers=args.workers_per_leaf, temperature=args.temperature)
            ok, err = True, None
        except Exception as e:
            # Fail closed per leaf, never silent -- one leaf's error (network, parse-storm,
            # etc.) must not abort the whole sweep silently or crash it opaquely.
            ok, err = False, str(e)
        with print_lock:
            done_count[0] += 1
            status = "ok" if ok else f"ERROR: {err}"
            print(f"[{done_count[0]}/{len(leaves)}] {leaf_name} -- {status}", flush=True)
            if not ok:
                errors.append((leaf_name, err))
        return leaf_name, ok, err

    with ThreadPoolExecutor(max_workers=args.leaf_parallelism) as executor:
        futures = [executor.submit(_run_one, leaf_name) for leaf_name in leaves]
        for f in as_completed(futures):
            f.result()

    print(f"\n=== sweep done: {len(leaves) - len(errors)}/{len(leaves)} leaves clean ===")
    if errors:
        print("Leaves with errors:")
        for name, err in errors:
            print(f"  - {name}: {err}")

    # Coverage is asserted at the END of every sweep, against items x n_runs read from each
    # leaf's own oracle.jsonl. This is the check that did not exist on 2026-07-03, which is how
    # 5 truncated cells shipped looking complete. A hole is named, never averaged over.
    matrix = coverage.coverage_matrix(
        [LEAVES_DIR / n for n in leaves], [args.label], N_RUNS,
        coverage.artifact_suffix(args.temperature))
    holes = [c for c in matrix if not c["complete"]]
    recorded = sum(c["recorded"] for c in matrix)
    owed = sum(c["expected"] for c in matrix)
    print(f"COVERAGE {args.label} @ temp={args.temperature}: "
          f"{len(matrix) - len(holes)}/{len(matrix)} cells complete, {recorded}/{owed} calls")
    if holes:
        print("INCOMPLETE CELLS (re-run this sweep to fill them; it resumes per cell):")
        for c in holes:
            print(f"  - {c['leaf']}: {c['recorded']}/{c['expected']} (short {c['short_by']})")
        sys.exit(1)          # fail closed: a short sweep must not exit 0 and read as done


def plan_report(label, model_id, leaves, temperature, guard_config):
    """
    What: the --dry-run output. Resolves every leaf, computes its expected calls, its derived
          caps and its estimated cost, and reports the total -- making ZERO model calls.
    Why: a sweep is the expensive, irreversible-ish step. Reviewing the exact call and spend plan
          before launching is cheaper than discovering the shape of it from a bill.
    """
    per_call = guard_mod.per_call_cost(label)
    unknown = per_call is None
    if unknown:
        per_call = guard_mod._UNKNOWN_MODEL_COST_USD
    rows, total_calls, total_cost = [], 0, 0.0
    for name in leaves:
        d = LEAVES_DIR / name
        exp = coverage.expected_calls(d, N_RUNS)
        already = len(coverage.recorded_keys(
            coverage.checkpoint_path(d, label, coverage.artifact_suffix(temperature))))
        todo = max(0, exp - already)
        caps = guard_config or guard_mod.caps_for_leaf(label, exp)
        rows.append((name, coverage.n_items(d), exp, already, todo, caps["max_cost_usd"]))
        total_calls += todo
        total_cost += todo * per_call
    out = [f"=== DRY RUN: {label} ({model_id}) @ temp={temperature} -- NO CALLS MADE ===", "",
           f"arm namespace   : {coverage.artifact_suffix(temperature) or '(legacy, unsuffixed)'}",
           f"scored file     : {coverage.scored_filename(temperature)}",
           f"per-call cost   : ${per_call:.6f}" + ("  (UNKNOWN LABEL -> priced as the dearest "
                                                     "known model)" if unknown else ""),
           f"leaves          : {len(leaves)}",
           f"calls still owed: {total_calls}  (of {sum(r[2] for r in rows)} total; "
           f"{sum(r[3] for r in rows)} already recorded and will be SKIPPED on resume)",
           f"ESTIMATED SPEND : ${total_cost:.2f}", "",
           "| Leaf | items | owed | done | to run | cap $ |", "|---|---|---|---|---|---|"]
    for name, items, exp, already, todo, cap in rows:
        out.append(f"| {name} | {items} | {exp} | {already} | {todo} | {cap:.3f} |")
    return "\n".join(out)


if __name__ == "__main__":
    main()
