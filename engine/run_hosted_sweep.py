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

from runner import run_leaf, openrouter_model_set, anthropic_model_set  # noqa: E402

REPO = ENGINE.parent
LEAVES_DIR = REPO / "leaves"

# Per-leaf cap, not per-sweep -- run_model() builds a fresh BrakePedalGuard per leaf (see
# runner.py's run_model), so this bounds each leaf independently regardless of how many leaves
# run concurrently. Largest leaf (pre_vs_post_money, 19 items x 20 runs = 380 calls) fits with
# headroom; a runaway bug on any one leaf still can't spend past this per leaf.
DEFAULT_MAX_STEPS_PER_LEAF = 500
DEFAULT_MAX_COST_PER_LEAF = 0.20

# Soft warn threshold, not a hard block -- see module docstring's Concurrency budget note.
SOFT_CONCURRENCY_WARN = 50


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--label", required=True, help="model_label for guard/checkpoint/scorecard, "
                    "e.g. gemma4-31b-or (must match a guard.ESTIMATED_COST_PER_CALL_USD entry "
                    "or it fails closed to the most-expensive-known default)")
    p.add_argument("--model", required=True, help="OpenRouter model id, e.g. google/gemma-4-31b-it")
    p.add_argument("--client", choices=["openrouter", "anthropic"], default="openrouter",
                    help="which provider backs --label/--model (anthropic = direct API,"
                    " Sec 0.10 override, see models.AnthropicClient)")
    p.add_argument("--leaf-parallelism", type=int, default=10,
                    help="how many leaves run their harness concurrently")
    p.add_argument("--workers-per-leaf", type=int, default=4,
                    help="max_workers passed into each leaf's own harness run")
    p.add_argument("--max-steps-per-leaf", type=int, default=DEFAULT_MAX_STEPS_PER_LEAF)
    p.add_argument("--max-cost-per-leaf", type=float, default=DEFAULT_MAX_COST_PER_LEAF)
    p.add_argument("--only-leaf", default=None, help="run a single leaf by name (debugging)")
    args = p.parse_args()

    total_concurrency = args.leaf_parallelism * args.workers_per_leaf
    if total_concurrency > SOFT_CONCURRENCY_WARN:
        print(f"WARN: leaf_parallelism({args.leaf_parallelism}) x workers_per_leaf"
              f"({args.workers_per_leaf}) = {total_concurrency} concurrent calls, above the "
              f"informal ~{SOFT_CONCURRENCY_WARN}-request OpenRouter/Cloudflare ceiling (see "
              f"module docstring) -- proceeding, but expect possible 429s.", flush=True)

    model_set = (anthropic_model_set(args.label, args.model) if args.client == "anthropic"
                 else openrouter_model_set(args.label, args.model))
    guard_config = {"max_steps": args.max_steps_per_leaf, "max_cost_usd": args.max_cost_per_leaf}

    leaves = sorted(d.name for d in LEAVES_DIR.iterdir() if d.is_dir() and (d / "task.py").exists())
    if args.only_leaf:
        leaves = [l for l in leaves if l == args.only_leaf]
        if not leaves:
            print(f"error: no such leaf '{args.only_leaf}'", file=sys.stderr)
            sys.exit(1)

    print(f"=== hosted sweep: {args.label} ({args.model}) across {len(leaves)} leaves -- "
          f"{args.leaf_parallelism} leaves concurrently x {args.workers_per_leaf} "
          f"workers/leaf ({total_concurrency} total in-flight) -- "
          f"per-leaf cap steps={args.max_steps_per_leaf} cost=${args.max_cost_per_leaf} ===\n",
          flush=True)

    print_lock = threading.Lock()
    done_count = [0]
    errors = []

    def _run_one(leaf_name):
        leaf_dir = LEAVES_DIR / leaf_name
        try:
            run_leaf(leaf_dir, model_set=model_set, guard_config=guard_config,
                     max_workers=args.workers_per_leaf)
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


if __name__ == "__main__":
    main()
