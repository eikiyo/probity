"""
Location: engine/backfill.py
Purpose: Fill the HOLES in an arm without re-billing anything already recorded. Five cells of the
         published 0.7 arm were silently truncated by a flat per-leaf cost cap (guard.caps_for_leaf
         now sizes the cap from what the leaf actually owes), leaving 377 calls unrecorded and
         biasing wobble DOWNWARD -- an item with zero runs can never be counted as flipping. This
         re-runs ONLY the short cells, relying on harness.run_harness's checkpoint resume so a
         completed (instance, run) is never called again.
Functions: model_set_for(), find_holes(), backfill_cell(), main()
Calls: engine/coverage.py (hole detection), engine/preflight.py (label -> client), engine/runner.py
Imports: argparse, json, sys, pathlib
Run: python3 engine/backfill.py --temperature 0.7 --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

ENGINE = Path(__file__).parent
sys.path.insert(0, str(ENGINE))

import coverage    # noqa: E402
import preflight   # noqa: E402
import runner      # noqa: E402

REPO = ENGINE.parent


def model_set_for(label):
    """The one-model `model_set` runner.run_leaf expects, built from preflight.LINEUP so the
    label -> (routing, model id) mapping has exactly ONE definition in the repo. A backfill that
    guessed the client would silently move a cell to a different provider mid-experiment, which
    is precisely the parity break this whole exercise exists to avoid."""
    for lbl, kind, model_id in preflight.LINEUP:
        if lbl != label:
            continue
        ollama_model = model_id if kind == "ollama" else None
        return [(label, ollama_model, lambda k=kind, m=model_id: preflight.build_client(k, m))]
    raise SystemExit(f"unknown label {label!r}; known: "
                     f"{', '.join(l for l, _, _ in preflight.LINEUP)}")


def built_leaf_dirs():
    reg = json.loads((REPO / "engine" / "registry.json").read_text())
    return [REPO / l["leaf"] for l in reg["leaves"]
            if l.get("tier") == "built" and "leaf" in l]


def find_holes(labels, temperature):
    """Every (leaf, label) cell that recorded fewer DISTINCT (instance, run) keys than the leaf's
    oracle owes. `expected` comes from oracle.jsonl -- the SPEC -- never from the result file,
    which is how a cell owing 360 calls printed '332/333 (100%)' in the published README."""
    suffix = coverage.artifact_suffix(temperature)
    holes = []
    for leaf_dir in built_leaf_dirs():
        for label in labels:
            cell = coverage.cell_status(leaf_dir, label, runner.N_RUNS, suffix)
            if cell["recorded"] == 0:
                continue          # never run here at all -- a sweep's job, not a backfill's
            if not cell["complete"]:
                holes.append({"leaf": leaf_dir, "label": label,
                              "recorded": cell["recorded"], "expected": cell["expected"],
                              "short_by": cell["short_by"]})
    return holes


def backfill_cell(hole, temperature, workers=4):
    """Re-run ONE short cell. run_leaf -> run_model -> harness.run_harness reads the existing
    checkpoint and skips every (instance, run) already present, so only the missing calls are
    billed. Returns the post-run cell status, read back from disk rather than assumed."""
    print(f"\n=== BACKFILL {hole['leaf'].name} / {hole['label']}: "
          f"{hole['recorded']}/{hole['expected']} (+{hole['short_by']} to run) ===", flush=True)
    runner.run_leaf(hole["leaf"], model_set=model_set_for(hole["label"]),
                    only=hole["label"], temperature=temperature, max_workers=workers)
    return coverage.cell_status(hole["leaf"], hole["label"], runner.N_RUNS,
                                coverage.artifact_suffix(temperature))


def _report(holes):
    if not holes:
        print("no holes: every cell that has data has ALL of its data.")
        return
    print(f"{'leaf':38s} {'label':20s} {'have':>6s} {'owe':>6s} {'short':>6s}")
    for h in holes:
        print(f"{h['leaf'].name:38s} {h['label']:20s} {h['recorded']:6d} "
              f"{h['expected']:6d} {h['short_by']:6d}")
    print(f"\n{len(holes)} short cells, {sum(h['short_by'] for h in holes)} calls to run.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--temperature", type=float, default=None,
                    help="omit for the LEGACY 0.7 arm (unsuffixed artifacts)")
    p.add_argument("--label", action="append", dest="labels",
                    help="restrict to one label; repeatable. default: the whole lineup")
    p.add_argument("--workers", type=int, default=4,
                    help="concurrent calls within a cell")
    p.add_argument("--dry-run", action="store_true", help="report holes, make ZERO calls")
    args = p.parse_args()

    labels = args.labels or [l for l, _, _ in preflight.LINEUP]
    holes = find_holes(labels, args.temperature)
    arm = coverage.arm_tag(args.temperature) if args.temperature is not None else "legacy(0.7)"
    print(f"=== HOLES in arm {arm} ===")
    _report(holes)
    if args.dry_run or not holes:
        if args.dry_run:
            print("\n--dry-run: no calls made.")
        return

    still_short = []
    for h in holes:
        after = backfill_cell(h, args.temperature, args.workers)
        if not after["complete"]:
            still_short.append((h, after))
        else:
            print(f"  FILLED: {after['recorded']}/{after['expected']}", flush=True)

    # Fail closed: the exit code, not the prose, is what a caller can trust.
    if still_short:
        print(f"\n!! {len(still_short)} cells STILL short after backfill:")
        for h, a in still_short:
            print(f"   {h['leaf'].name}/{h['label']}: {a['recorded']}/{a['expected']}")
        sys.exit(1)
    print(f"\nall {len(holes)} cells filled.")


if __name__ == "__main__":
    main()
