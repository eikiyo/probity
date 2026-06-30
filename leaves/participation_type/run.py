"""
Location: leaves/participation_type/run.py
Purpose: Run the participation_type corpus through gemma (local) + DeepSeek, score ACCURACY (vs
         the validated oracle) AND RELIABILITY (run-to-run consistency). Writes scored.json.
Functions: load_instances(), run_model(), main()
Calls: engine.harness, engine.scorer, engine.models; task.TASK
Imports: sys, json, pathlib
"""

import sys
import json
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "engine"))
sys.path.insert(0, str(HERE))

import harness          # noqa: E402
import scorer           # noqa: E402
from models import OllamaClient, DeepSeekClient  # noqa: E402
from task import TASK   # noqa: E402

N_RUNS = 5
TEMPERATURE = 0.7


def load_instances():
    """Build (instance, ground_truth) pairs from the questions + the SEPARATED oracle."""
    oracle = [json.loads(l) for l in open(HERE / "oracle.jsonl") if l.strip()]
    instances = []
    for o in oracle:
        question = (HERE / "corpus" / "questions" / f"{o['id']}.txt").read_text(encoding="utf-8")
        instances.append(({"id": o["id"], "document": question},
                          {"participation_type": o["participation_type"]}))
    return instances, oracle


def run_model(label, client, instances):
    """Run one model, return its accuracy + reliability scores."""
    ckpt = str(HERE / f"runs_{label}.jsonl")
    runs, stats = harness.run_harness(client, TASK, instances, n_runs=N_RUNS,
                                      temperature=TEMPERATURE, checkpoint_file=ckpt)
    acc = scorer.score_accuracy(TASK, instances, runs)
    rel = scorer.score_runs(TASK, instances, runs)
    return {"model": getattr(client, "model", label), "stats": stats,
            "accuracy": acc, "reliability": rel}


def main():
    instances, oracle = load_instances()
    print(f"Loaded {len(instances)} real items "
          f"({sum(o['participation_type']=='non-participating' for o in oracle)} non-part / "
          f"{sum(o['participation_type']=='participating' for o in oracle)} part / "
          f"{sum(o['participation_type']=='capped' for o in oracle)} capped)\n")
    results = {}
    targets = []
    if "--deepseek-only" not in sys.argv:
        targets.append(("gemma", OllamaClient()))
    if "--gemma-only" not in sys.argv:
        targets.append(("deepseek", DeepSeekClient()))
    for label, client in targets:
        print(f"=== {label} ({getattr(client,'model','?')}) ===")
        results[label] = run_model(label, client, instances)
        a, r = results[label]["accuracy"], results[label]["reliability"]
        print(f"  accuracy(majority): {a['accuracy_majority']*100:.0f}%  "
              f"strict: {a['accuracy_strict']*100:.0f}%  "
              f"reliability: {r['consistency_pct']:.0f}%  "
              f"measurable: {a['n_measurable']}/{a['n_instances']}\n")
    (HERE / "scored.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("wrote scored.json")


if __name__ == "__main__":
    main()
