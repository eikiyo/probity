"""
Location: leaves/participation_type/run.py
Purpose: Run the corpus through a MODEL SIZE LADDER (gemma3:1b -> llama3.2 -> gemma4:12b ->
         qwen3.5:27b -> deepseek-v4-flash), N=20 runs each at temp 0.7. WOBBLE (run-to-run
         inconsistency) is the headline metric; accuracy (vs validated oracle) is reported beside it.
Functions: load_instances(), run_model(), main()
Calls: engine.harness, engine.scorer, engine.models; task.TASK
Imports: sys, json, subprocess, pathlib
"""

import sys
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "engine"))
sys.path.insert(0, str(HERE))

import harness          # noqa: E402
import scorer           # noqa: E402
from models import OllamaClient, DeepSeekClient  # noqa: E402
from task import TASK   # noqa: E402

N_RUNS = 20
TEMPERATURE = 0.7

# (label, ollama_model_or_None, factory) — None model => hosted (no local unload).
LADDER = [
    ("gemma3-1b",   "gemma3:1b",    lambda: OllamaClient("gemma3:1b")),
    ("llama3.2-3b", "llama3.2:latest", lambda: OllamaClient("llama3.2:latest")),
    ("gemma4-12b",  "gemma4:12b",   lambda: OllamaClient("gemma4:12b")),
    ("qwen3.5-27b", "qwen3.5:27b",  lambda: OllamaClient("qwen3.5:27b")),
    ("deepseek-v4f", None,          lambda: DeepSeekClient()),
]


def load_instances():
    """Build (instance, ground_truth) pairs from questions + the SEPARATED oracle (in file order)."""
    oracle = [json.loads(l) for l in open(HERE / "oracle.jsonl") if l.strip()]
    instances = []
    for o in oracle:
        q = (HERE / "corpus" / "questions" / f"{o['id']}.txt").read_text(encoding="utf-8")
        instances.append(({"id": o["id"], "document": q},
                          {"participation_type": o["participation_type"]}))
    return instances, oracle


def run_model(label, factory, ollama_model, instances):
    """Run one model at N=20, return accuracy + reliability(wobble). Unload local model after."""
    client = factory()
    ckpt = str(HERE / f"runs_{label}.jsonl")
    runs, _ = harness.run_harness(client, TASK, instances, n_runs=N_RUNS,
                                  temperature=TEMPERATURE, checkpoint_file=ckpt)
    if ollama_model:
        subprocess.run(["ollama", "stop", ollama_model], capture_output=True)
    acc = scorer.score_accuracy(TASK, instances, runs)
    rel = scorer.score_runs(TASK, instances, runs)
    return {"model": getattr(client, "model", label), "accuracy": acc, "reliability": rel}


def main():
    instances, oracle = load_instances()
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    counts = {c: sum(o["participation_type"] == c for o in oracle) for c in
              ["non-participating", "participating", "capped"]}
    print(f"{len(instances)} items  {counts}  N={N_RUNS} runs/item\n")
    scored = {}
    for label, omodel, factory in LADDER:
        if only and label != only:
            continue
        print(f"=== {label} (N={N_RUNS}) ===", flush=True)
        res = run_model(label, factory, omodel, instances)
        a, r = res["accuracy"], res["reliability"]
        wobble = r["field_flips"].get("participation_type", 0.0) * 100
        print(f"  WOBBLE: {wobble:.0f}% of items flipped across {N_RUNS} runs  |  "
              f"consistency {r['consistency_pct']:.0f}%  |  accuracy {a['accuracy_majority']*100:.0f}%\n", flush=True)
        scored[label] = res
        out = HERE / "scored.json"
        prev = json.loads(out.read_text()) if out.exists() else {}
        prev.update(scored)
        out.write_text(json.dumps(prev, indent=1), encoding="utf-8")  # incremental
    print("wrote scored.json")


if __name__ == "__main__":
    main()
